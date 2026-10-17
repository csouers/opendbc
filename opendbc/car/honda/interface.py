#!/usr/bin/env python3
import numpy as np
from opendbc.car import get_safety_config, structs, uds
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.disable_ecu import disable_ecu
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.values import CarControllerParams, HondaFlags, CAR, HondaSafetyFlags
from opendbc.car.honda.carcontroller import CarController
from opendbc.car.honda.carstate import CarState
from opendbc.car.honda.radar_interface import RadarInterface
from opendbc.car.interfaces import CarInterfaceBase

TransmissionType = structs.CarParams.TransmissionType


class CarInterface(CarInterfaceBase):
  CarState = CarState
  CarController = CarController
  RadarInterface = RadarInterface

  DRIVABLE_GEARS = (structs.CarState.GearShifter.sport,)

  @staticmethod
  def get_pid_accel_limits(CP, current_speed, cruise_speed):
    if CP.flags & HondaFlags.BOSCH:
      return CarControllerParams.BOSCH_ACCEL_MIN, CarControllerParams.BOSCH_GAS_LOOKUP_BP[-1]
    else:
      # NIDECs don't allow acceleration near cruise_speed,
      # so limit limits of pid to prevent windup
      ACCEL_MAX_VALS = [CarControllerParams.NIDEC_ACCEL_MAX, 0.2]
      ACCEL_MAX_BP = [cruise_speed - 2., cruise_speed - .2]
      return CarControllerParams.NIDEC_ACCEL_MIN, np.interp(current_speed, ACCEL_MAX_BP, ACCEL_MAX_VALS)

  @staticmethod
  def _get_params(ret: structs.CarParams, candidate, fingerprint, car_fw, alpha_long, is_release, docs) -> structs.CarParams:
    ret.brand = "honda"

    CAN = CanBus(ret, fingerprint)

    if ret.flags & HondaFlags.BOSCH:
      cfgs = [get_safety_config(structs.CarParams.SafetyModel.hondaBosch)]
      if ret.flags & HondaFlags.BOSCH_CANFD and CAN.pt >= 4:
        cfgs.insert(0, get_safety_config(structs.CarParams.SafetyModel.noOutput))
      ret.safetyConfigs = cfgs

      ret.radarUnavailable = True
      # Disable the radar and let openpilot control longitudinal
      # WARNING: THIS DISABLES AEB!
      # If Bosch radarless, this blocks ACC messages from the camera
      # TODO: get radar disable working on Bosch CANFD
      ret.alphaLongitudinalAvailable = not (ret.flags & HondaFlags.BOSCH_CANFD)
      ret.openpilotLongitudinalControl = alpha_long and not (ret.flags & HondaFlags.BOSCH_CANFD)
      ret.pcmCruise = not ret.openpilotLongitudinalControl
    else:
      ret.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.hondaNidec)]
      ret.openpilotLongitudinalControl = True
      ret.pcmCruise = True

    if candidate == CAR.HONDA_CRV_5G and 0x12f8bfa7 in fingerprint[CAN.radar]:
      ret.flags |= HondaFlags.HAS_BSM.value

    # custom: always enable BSM, not just on CRV_5G
    ret.flags |= HondaFlags.HAS_BSM.value

    # This is from the fake Tesla. Means we should have radar too.
    # Hard code for now
    if True: #361 in fingerprint[CAN.radar]: # decimal
      ret.flags |= HondaFlags.TESLA_RADAR.value
      ret.radarUnavailable = False
      # ret.radarDelay = 0.25 # get this value

    # Detect the BCM via B-CAN
    # TODO Add back the param instead. gateway fw is flakey right now
    # TODO Fix it
    if True: #0x12F81018 in fingerprint[CAN.bcm]:
      ret.flags |= HondaFlags.ENABLE_BLINKERS.value

    # Detect Bosch cars with new HUD msgs
    if any(0x33DA in f for f in fingerprint.values()):
      ret.flags |= HondaFlags.BOSCH_EXT_HUD.value

    if 0x184 in fingerprint[CAN.pt]:
      ret.flags |= HondaFlags.HYBRID.value

    if all(msg not in fingerprint[CAN.pt] for msg in (0x191, 0x1A3)):
      ret.transmissionType = TransmissionType.manual
    elif 0x191 in fingerprint[CAN.pt] and candidate != CAR.ACURA_RDX:
      # Traditional CVTs, gearshift position in GEARBOX_CVT
      ret.transmissionType = TransmissionType.cvt
    else:
      # Traditional autos, direct-drive EVs and eCVTs, gearshift position in GEARBOX_AUTO
      ret.transmissionType = TransmissionType.automatic

    ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
    ret.lateralTuning.pid.kf = 0.00006  # conservative feed-forward
    ret.steerActuatorDelay = 0.1

    if ret.flags & HondaFlags.BOSCH:
      # ret.longitudinalTuning.kpV = [0.3]  # 0.5
      # ret.longitudinalTuning.kiV = [0.09]  # 0.025
      # ret.stoppingDecelRate = 0.30  # 0.075 # brake_travel/s while trying to stop
      # ret.vEgoStopping = 0.35
      # ret.vEgoStarting = 0.35
      ret.stopAccel = -0.75  # CarControllerParams.BOSCH_ACCEL_MIN  # stock uses -4.0 m/s^2 once stopped but limited by safety model
      ret.longitudinalActuatorDelay = 0.5  # 0.1
      if ret.flags & HondaFlags.BOSCH_RADARLESS:
        ret.stopAccel = CarControllerParams.BOSCH_ACCEL_MIN  # stock uses -4.0 m/s^2 once stopped but limited by safety model
    else:
      # default longitudinal tuning for all hondas
      ret.longitudinalTuning.kiBP = [0., 5., 35.]
      ret.longitudinalTuning.kiV = [1.2, 0.8, 0.5]

    # Disable control if EPS mod detected
    eps_modified = False
    for fw in car_fw:
      if fw.ecu == "eps" and b"," in fw.fwVersion:
        eps_modified = True

    if candidate == CAR.HONDA_CIVIC:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[1.1], [0.33]]

    elif candidate in (CAR.HONDA_CIVIC_BOSCH, CAR.HONDA_CIVIC_BOSCH_DIESEL):
      if eps_modified:
        ret.lateralParams.torqueBP, ret.lateralParams.torqueV = [[0, 2564, 8000], [0, 2564, 3840]]
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.36], [0.108]]
      else:
        ret.lateralParams.torqueBP, ret.lateralParams.torqueV = [[0, 4096], [0, 4096]]  # TODO: determine if there is a dead zone at the top end
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.8], [0.24]]
      # custom: upstream sets BOSCH_GAS_LOOKUP_V = [0, 750] here; the fork's 6-point BOSCH_GAS_LOOKUP_* map is used instead
      # if candidate == CAR.HONDA_CIVIC_BOSCH:
      #     CarControllerParams.BOSCH_GAS_LOOKUP_V = [0, 750]

    elif candidate in (CAR.HONDA_CIVIC_2022, CAR.HONDA_PRELUDE_6G):
      ret.lateralTuning.pid.kpBP, ret.lateralTuning.pid.kpV = [[0, 10], [0.05, 0.5]]
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kiV = [[0, 10], [0.0125, 0.125]]

    elif candidate == CAR.HONDA_ACCORD:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]]

    elif candidate == CAR.ACURA_ILX:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.8], [0.24]]

    elif candidate in (CAR.HONDA_CRV, CAR.HONDA_CRV_EU):
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.8], [0.24]]
      ret.wheelSpeedFactor = 1.025

    elif candidate == CAR.HONDA_CRV_5G:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.64], [0.192]]
      ret.wheelSpeedFactor = 1.025

    elif candidate == CAR.HONDA_CRV_HYBRID:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]]
      ret.wheelSpeedFactor = 1.025

    elif candidate == CAR.HONDA_FIT:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2], [0.05]]

    elif candidate == CAR.HONDA_FREED:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2], [0.05]]

    elif candidate in (CAR.HONDA_HRV, CAR.HONDA_HRV_3G):
      if candidate == CAR.HONDA_HRV:
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.16], [0.025]]
        ret.wheelSpeedFactor = 1.025
      else:
        ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.8], [0.24]]  # TODO: can probably use some tuning

    elif candidate == CAR.ACURA_RDX:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.8], [0.24]]

    elif candidate == CAR.ACURA_RDX_3G:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.2], [0.06]]

    elif candidate == CAR.HONDA_ODYSSEY:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.28], [0.08]]

    elif candidate == CAR.HONDA_ODYSSEY_TWN:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.28], [0.08]]

    elif candidate == CAR.HONDA_PILOT:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.38], [0.11]]

    elif candidate == CAR.HONDA_RIDGELINE:
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.38], [0.11]]

    elif candidate in (CAR.HONDA_INSIGHT, CAR.HONDA_NBOX_2G):
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]]

    elif candidate in (CAR.HONDA_E, CAR.HONDA_E_ADVANCE):
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.6], [0.18]] # TODO: can probably use some tuning

    elif candidate == CAR.HONDA_ODYSSEY_5G_MMR:
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)
      ret.steerActuatorDelay = 0.15
      # custom: upstream sets BOSCH_GAS_LOOKUP_V = [0, 2000] here; the fork's 6-point BOSCH_GAS_LOOKUP_* map is used instead
      # CarControllerParams.BOSCH_GAS_LOOKUP_V = [0, 2000]
      if not ret.openpilotLongitudinalControl:
        # When using stock ACC, the radar intercepts and filters steering commands the EPS would otherwise accept
        ret.minSteerSpeed = 70. * CV.KPH_TO_MS

    else:
      ret.steerActuatorDelay = 0.15
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    if candidate == CAR.ACURA_RDX_3G_MMR:
      # custom: upstream sets BOSCH_GAS_LOOKUP_V = [0, 2000] here; the fork's 6-point BOSCH_GAS_LOOKUP_* map is used instead
      # CarControllerParams.BOSCH_GAS_LOOKUP_V = [0, 2000] # alpha longitudinal pedal tuning
      ret.dashcamOnly = is_release  # TODO: release from dashcam when there's enough driving data for torqued/paramsd to converge

    # These cars use alternate user brake msg (0x1BE)
    if 0x1BE in fingerprint[CAN.pt] and (candidate in (CAR.HONDA_ACCORD, CAR.HONDA_HRV_3G, CAR.ACURA_RDX_3G, CAR.ACURA_MDX_4G, CAR.ACURA_ADX) or
                                          ret.flags & HondaFlags.BOSCH_CANFD):
      ret.flags |= HondaFlags.BOSCH_ALT_BRAKE.value

    if ret.flags & HondaFlags.BOSCH_ALT_BRAKE:
      ret.safetyConfigs[-1].safetyParam |= HondaSafetyFlags.ALT_BRAKE.value
    if ret.flags & HondaFlags.NIDEC_ALT_SCM_MESSAGES:
      ret.safetyConfigs[-1].safetyParam |= HondaSafetyFlags.NIDEC_ALT.value
    if ret.openpilotLongitudinalControl and ret.flags & HondaFlags.BOSCH:
      ret.safetyConfigs[-1].safetyParam |= HondaSafetyFlags.BOSCH_LONG.value
    if ret.flags & HondaFlags.BOSCH_RADARLESS:
      ret.safetyConfigs[-1].safetyParam |= HondaSafetyFlags.RADARLESS.value
    if ret.flags & HondaFlags.BOSCH_CANFD:
      ret.safetyConfigs[-1].safetyParam |= HondaSafetyFlags.BOSCH_CANFD.value

    # min speed to enable ACC. if car can do stop and go, then set enabling speed
    # to a negative value, so it won't matter. Otherwise, add 0.5 mph margin to not
    # conflict with PCM acc
    ret.autoResumeSng = bool(ret.flags & HondaFlags.BOSCH) or candidate == CAR.HONDA_CIVIC
    if ret.autoResumeSng:
      ret.minEnableSpeed = -1.
    elif candidate == CAR.HONDA_ODYSSEY_TWN:
      ret.minEnableSpeed = 19. * CV.MPH_TO_MS
    else:
      ret.minEnableSpeed = 25.51 * CV.MPH_TO_MS

    ret.steerLimitTimer = 0.8

    if not ret.radarDelay:
      ret.radarDelay = 0.1

    return ret

  @staticmethod
  def init(CP, can_recv, can_send, communication_control=None):
    if CP.flags & HondaFlags.BOSCH and not (CP.flags & HondaFlags.BOSCH_RADARLESS) and CP.openpilotLongitudinalControl:
      # 0x80 silences response
      if communication_control is None:
        communication_control = bytes([uds.SERVICE_TYPE.COMMUNICATION_CONTROL, 0x80 | uds.CONTROL_TYPE.DISABLE_RX_DISABLE_TX,
                                       uds.MESSAGE_TYPE.NORMAL_AND_NETWORK_MANAGEMENT])
      disable_ecu(can_recv, can_send, bus=CanBus(CP).pt, addr=0x18DAB0F1, com_cont_req=communication_control)

  @staticmethod
  def deinit(CP, can_recv, can_send):
    communication_control = bytes([uds.SERVICE_TYPE.COMMUNICATION_CONTROL, 0x80 | uds.CONTROL_TYPE.ENABLE_RX_ENABLE_TX,
                                   uds.MESSAGE_TYPE.NORMAL_AND_NETWORK_MANAGEMENT])
    CarInterface.init(CP, can_recv, can_send, communication_control)
