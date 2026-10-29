import numpy as np
from collections import defaultdict

from opendbc.can import CANDefine, CANParser
from opendbc.car import Bus, create_button_events, structs
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.values import CAR, DBC, STEER_THRESHOLD, HondaFlags, CruiseButtons, CruiseSettings, \
                                                 GearShifter, CarControllerParams
from opendbc.car.interfaces import CarStateBase

TransmissionType = structs.CarParams.TransmissionType
ButtonType = structs.CarState.ButtonEvent.Type

class BodyParsers:
  """B-CAN/DBC body messages, parsed on every bus they may arrive on.

  The Honda fork maps Bus.body to the radar/body slot (bus 0), but on the comma four harness the body
  bus physically reports as bus 2, so parse both and use whichever is actually delivering frames.
  Sending is unaffected (it still uses CanBus.bcm).
  """

  def __init__(self, dbc_name: str, messages: list[tuple[str, float]], buses: list[int]) -> None:
    self.dbc_name = dbc_name
    self.parsers = [CANParser(dbc_name, messages, bus) for bus in buses]
    # registering is lazy on vl access; do it for every message so "seen anything" works on all buses
    for parser in self.parsers:
      for name in parser.dbc.name_to_msg:
        parser.vl[name]

  def update(self, can_packets) -> None:
    for parser in self.parsers:
      parser.update(can_packets)

  @staticmethod
  def _seen(parser: CANParser) -> bool:
    return any(t > 0 for msg in parser.ts_nanos.values() for t in msg.values())

  @property
  def _active(self) -> CANParser:
    for parser in self.parsers:
      if self._seen(parser):
        return parser
    return self.parsers[0]

  @property
  def vl(self):
    return self._active.vl

  @property
  def vl_all(self):
    return self._active.vl_all

  @property
  def can_valid(self) -> bool:
    return all(parser.can_valid for parser in self.parsers)

  @property
  def bus_timeout(self) -> bool:
    return self._active.bus_timeout


BUTTONS_DICT = {CruiseButtons.RES_ACCEL: ButtonType.accelCruise, CruiseButtons.DECEL_SET: ButtonType.decelCruise,
                CruiseButtons.MAIN: ButtonType.mainCruise, CruiseButtons.CANCEL: ButtonType.cancel}
SETTINGS_BUTTONS_DICT = {CruiseSettings.DISTANCE: ButtonType.gapAdjustCruise, CruiseSettings.LKAS: ButtonType.lkas}


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    can_define = CANDefine(DBC[CP.carFingerprint][Bus.pt])

    if CP.transmissionType != TransmissionType.manual:
      self.gearbox_msg = "GEARBOX_AUTO"
      if CP.transmissionType == TransmissionType.cvt:
        self.gearbox_msg = "GEARBOX_CVT"
      self.shifter_values = can_define.dv[self.gearbox_msg]["GEAR_SHIFTER"]

    self.car_state_scm_msg = "SCM_FEEDBACK"
    if CP.flags & HondaFlags.NIDEC_ALT_SCM_MESSAGES:
      self.car_state_scm_msg = "SCM_BUTTONS"

    self.brake_error_msg = "HYBRID_BRAKE_ERROR" if CP.flags & HondaFlags.HYBRID else "STANDSTILL"

    self.steer_status_values = defaultdict(lambda: "UNKNOWN", can_define.dv["STEER_STATUS"]["STEER_STATUS"])

    if CP.flags & HondaFlags.ENABLE_BLINKERS.value:
      self.kwp_values = {v: k for k, v in can_define.dv["BCM_16f1f0_KWP_Resp_Tester"]["D0"].items()}

      # B-CAN lamp/stalk state, only valid once the body parser starts delivering
      self.leftBlinker_lamp = False
      self.rightBlinker_lamp = False
      self.leftBlinker_stalk = False
      self.rightBlinker_stalk = False
      self.fog = False
      self.headlights = False
      self.lighting_auto = False
      self.parking_lights_on = False  # car's parking lights = night/dark mode
      self.illumination_step = 0      # meter/dash illumination step, 1 (dim) .. 21 (full)
      self.lamp_seen = False  # B-CAN has actually delivered the lamp state at least once

    self.brake_error = False
    self.brake_switch_prev = False
    self.brake_switch_active = False
    self.low_speed_alert = False

    self.dynamic_v_cruise_units = bool(self.CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_ALT_RADAR | HondaFlags.BOSCH_CANFD))
    self.cruise_setting = 0
    self.v_cruise_pcm_prev = 0

    # When available we use cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] to populate vEgoCluster
    # However, on cars without a digital speedometer this is not always present (HRV, FIT, CRV 2016, ILX and RDX)
    self.dash_speed_seen = False
    self.is_metric = False
    self.v_cruise_factor = 1.

  def update(self, can_parsers) -> structs.CarState:
    cp = can_parsers[Bus.pt]
    cp_cam = can_parsers[Bus.cam]
    cp_body = can_parsers.get(Bus.body)

    ret = structs.CarState()

    # car params
    v_weight_v = [0., 1.]  # don't trust smooth speed at low values to avoid premature zero snapping
    v_weight_bp = [1., 6.]   # smooth blending, below ~0.6m/s the smooth speed snaps to zero

    # update prevs, update must run once per loop
    prev_cruise_buttons = self.cruise_buttons
    prev_cruise_setting = self.cruise_setting
    self.cruise_setting = cp.vl["SCM_BUTTONS"]["CRUISE_SETTING"]
    self.cruise_buttons = cp.vl["SCM_BUTTONS"]["CRUISE_BUTTONS"]

    # used for car hud message
    # TODO: find CAR_SPEED for HONDA_ODYSSEY_TWN or use ACC_HUD w/ detection
    self.is_metric = self.CP.carFingerprint in (CAR.HONDA_ODYSSEY_TWN,) or not cp.vl["CAR_SPEED"]["IMPERIAL_UNIT"]
    self.v_cruise_factor = CV.MPH_TO_MS if self.dynamic_v_cruise_units and not self.is_metric else CV.KPH_TO_MS

    # ******************* parse out can *******************

    # blend in transmission speed at low speed, since it has more low speed accuracy
    # STANDSTILL->WHEELS_MOVING bit can be noisy around zero, so use XMISSION_SPEED
    v_wheel = sum([cp.vl["WHEEL_SPEEDS"][f"WHEEL_SPEED_{s}"] for s in ("FL", "FR", "RL", "RR")]) / 4.0 * CV.KPH_TO_MS
    v_weight = float(np.interp(v_wheel, v_weight_bp, v_weight_v))
    ret.vEgoRaw = (1. - v_weight) * cp.vl["ENGINE_DATA"]["XMISSION_SPEED"] * CV.KPH_TO_MS * self.CP.wheelSpeedFactor + v_weight * v_wheel
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = cp.vl["ENGINE_DATA"]["XMISSION_SPEED"] < 1e-5

    # doorOpen is true if we can find any door open, but signal locations vary, and we may only see the driver's door
    # TODO: Test the eight Nidec cars without SCM signals for driver's door state, may be able to consolidate further
    if self.CP.flags & HondaFlags.HAS_ALL_DOOR_STATES:
      ret.doorOpen = any([cp.vl["DOORS_STATUS"]["DOOR_OPEN_FL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_FR"],
                          cp.vl["DOORS_STATUS"]["DOOR_OPEN_RL"], cp.vl["DOORS_STATUS"]["DOOR_OPEN_RR"]])
    elif "DRIVERS_DOOR_OPEN" in cp.vl["SCM_BUTTONS"]:
      ret.doorOpen = bool(cp.vl["SCM_BUTTONS"]["DRIVERS_DOOR_OPEN"])
    else:
      ret.doorOpen = bool(cp.vl["SCM_FEEDBACK"]["DRIVERS_DOOR_OPEN"])

    ret.seatbeltUnlatched = bool(cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LAMP"] or not cp.vl["SEATBELT_STATUS"]["SEATBELT_DRIVER_LATCHED"])

    steer_status = self.steer_status_values[cp.vl["STEER_STATUS"]["STEER_STATUS"]]
    ret.steerFaultPermanent = steer_status not in ("NORMAL", "NO_TORQUE_ALERT_1", "NO_TORQUE_ALERT_2", "LOW_SPEED_LOCKOUT", "TMP_FAULT")
    if self.CP.flags & HondaFlags.BOSCH_ALT_RADAR:
      # TODO: See if this logic works for all other Honda
      min_steer_speed = max(CarControllerParams.STEER_GLOBAL_MIN_SPEED, self.CP.minSteerSpeed)
      expected_low_speed_lockout = steer_status == "LOW_SPEED_LOCKOUT" and ret.vEgo < min_steer_speed
      ret.steerFaultTemporary = steer_status != "NORMAL" and not expected_low_speed_lockout
    else:
      # LOW_SPEED_LOCKOUT is not worth a warning
      # NO_TORQUE_ALERT_2 can be caused by bump or steering nudge from driver
      # FIXME: the stock camera stops steering on NO_TORQUE_ALERT_1
      ret.steerFaultTemporary = steer_status not in ("NORMAL", "LOW_SPEED_LOCKOUT", "NO_TORQUE_ALERT_2")

    if (self.CP.carFingerprint == CAR.ACURA_MDX_4G) and (steer_status == "TJA_LOW_SPEED_LOCKOUT"):
      ret.steerFaultPermanent = False
      ret.steerFaultTemporary = False

    # All Honda EPS cut off slightly above standstill, some much higher
    # Don't alert in the near-standstill range, but alert for per-vehicle configured minimums above that
    if CarControllerParams.STEER_GLOBAL_MIN_SPEED < ret.vEgo < (self.CP.minSteerSpeed + 0.5):
      self.low_speed_alert = True
    elif ret.vEgo > (self.CP.minSteerSpeed + 1.):
      # TODO: better handle delayed steering enablement on ALT_RADAR cars
      self.low_speed_alert = False
    ret.lowSpeedAlert = self.low_speed_alert

    if self.CP.flags & HondaFlags.BOSCH_RADARLESS:
      ret.accFaulted = bool(cp.vl["CRUISE_FAULT_STATUS"]["CRUISE_FAULT"])
    else:
      if self.CP.openpilotLongitudinalControl:
        if (self.CP.carFingerprint == CAR.ACURA_MDX_4G) and (self.CP.flags & HondaFlags.BOSCH_ALT_BRAKE):
          ret.accFaulted = bool(cp.vl["BRAKE_MODULE"]["CRUISE_FAULT"])
        else:
          ret.accFaulted = bool(cp.vl[self.brake_error_msg]["BRAKE_ERROR_1"] or cp.vl[self.brake_error_msg]["BRAKE_ERROR_2"])

      # Log non-critical stock ACC/LKAS faults if Nidec (camera)
      if not (self.CP.flags & HondaFlags.BOSCH):
        ret.carFaultedNonCritical = bool(cp_cam.vl["ACC_HUD"]["ACC_PROBLEM"] or cp_cam.vl["LKAS_HUD"]["LKAS_PROBLEM"])

    ret.espDisabled = cp.vl["VSA_STATUS"]["ESP_DISABLED"] != 0

    if self.CP.carFingerprint not in (CAR.HONDA_ODYSSEY_TWN,):
      self.dash_speed_seen = self.dash_speed_seen or cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] > 1e-3
      if self.dash_speed_seen:
        conversion = CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS
        ret.vEgoCluster = cp.vl["CAR_SPEED"]["ROUGH_CAR_SPEED_2"] * conversion

    ret.steeringAngleDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE"]
    ret.steeringRateDeg = cp.vl["STEERING_SENSORS"]["STEER_ANGLE_RATE"]

    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_stalk(
      250, cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"], cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"])
    ret.brakeHoldActive = cp.vl["VSA_STATUS"]["BRAKE_HOLD_ACTIVE"] == 1
    ret.parkingBrake = bool(cp.vl[self.car_state_scm_msg]["PARKING_BRAKE_ON"])

    if self.CP.transmissionType == TransmissionType.manual:
      ret.gearShifter = GearShifter.reverse if bool(cp.vl[self.car_state_scm_msg]["REVERSE_LIGHT"]) else GearShifter.drive
    else:
      gear_position = self.shifter_values.get(cp.vl[self.gearbox_msg]["GEAR_SHIFTER"], None)
      ret.gearShifter = self.parse_gear_shifter(gear_position)

    ret.gasPressed = cp.vl["POWERTRAIN_DATA"]["PEDAL_GAS"] > 1e-5

    ret.steeringTorque = cp.vl["STEER_STATUS"]["STEER_TORQUE_SENSOR"]
    ret.steeringPressed = abs(ret.steeringTorque) > STEER_THRESHOLD.get(self.CP.carFingerprint, 1200)

    if self.CP.flags & HondaFlags.BOSCH:
      # The PCM always manages its own cruise control state, but doesn't publish it
      if self.CP.flags & HondaFlags.BOSCH_RADARLESS:
        ret.cruiseState.nonAdaptive = cp_cam.vl["ACC_HUD"]["CRUISE_CONTROL_LABEL"] != 0

      if not self.CP.openpilotLongitudinalControl:
        # ACC_HUD is on camera bus on radarless cars
        acc_hud = cp_cam.vl["ACC_HUD"] if self.CP.flags & HondaFlags.BOSCH_RADARLESS else cp.vl["ACC_HUD"]
        ret.cruiseState.nonAdaptive = acc_hud["CRUISE_CONTROL_LABEL"] != 0
        ret.cruiseState.standstill = acc_hud["CRUISE_SPEED"] == 252.

        # On set, cruise set speed pulses between 254~255 and the set speed prev is set to avoid this.
        ret.cruiseState.speed = self.v_cruise_pcm_prev if acc_hud["CRUISE_SPEED"] > 160.0 else acc_hud["CRUISE_SPEED"] * self.v_cruise_factor
        self.v_cruise_pcm_prev = ret.cruiseState.speed
      else:
        # TODO: FIX DBC FACTOR
        self.engine_torque = cp.vl["GAS_PEDAL_2"]["ENGINE_TORQUE_ESTIMATE"] * 0.01
    else:
      ret.cruiseState.speed = cp.vl["CRUISE"]["CRUISE_SPEED_PCM"] * CV.KPH_TO_MS

    if self.CP.flags & HondaFlags.BOSCH_ALT_BRAKE:
      ret.brakePressed = cp.vl["BRAKE_MODULE"]["BRAKE_PRESSED"] != 0
    else:
      # brake switch has shown some single time step noise, so only considered when
      # switch is on for at least 2 consecutive CAN samples
      # brake switch rises earlier than brake pressed but is never 1 when in park
      brake_switch_vals = cp.vl_all["POWERTRAIN_DATA"]["BRAKE_SWITCH"]
      if len(brake_switch_vals):
        brake_switch = cp.vl["POWERTRAIN_DATA"]["BRAKE_SWITCH"] != 0
        if len(brake_switch_vals) > 1:
          self.brake_switch_prev = brake_switch_vals[-2] != 0
        self.brake_switch_active = brake_switch and self.brake_switch_prev
        self.brake_switch_prev = brake_switch
      ret.brakePressed = (cp.vl["POWERTRAIN_DATA"]["BRAKE_PRESSED"] != 0) or self.brake_switch_active

    ret.cruiseState.enabled = cp.vl["POWERTRAIN_DATA"]["ACC_STATUS"] != 0
    ret.cruiseState.available = bool(cp.vl[self.car_state_scm_msg]["MAIN_ON"])

    if self.CP.flags & HondaFlags.BOSCH:
      # TODO: find the radarless AEB_STATUS bit and make sure ACCEL_COMMAND is correct to enable AEB alerts
      if not (self.CP.flags & HondaFlags.BOSCH_RADARLESS):
        ret.stockAeb = (not self.CP.openpilotLongitudinalControl) and bool(cp.vl["ACC_CONTROL"]["AEB_STATUS"] and cp.vl["ACC_CONTROL"]["ACCEL_COMMAND"] < -1e-5)
    else:
      ret.stockAeb = bool(cp_cam.vl["BRAKE_COMMAND"]["AEB_REQ_1"] and cp_cam.vl["BRAKE_COMMAND"]["COMPUTER_BRAKE"] > 1e-5)

    self.acc_hud = False
    self.lkas_hud = False
    if not (self.CP.flags & HondaFlags.BOSCH):
      ret.stockFcw = cp_cam.vl["BRAKE_COMMAND"]["FCW"] != 0
      self.acc_hud = cp_cam.vl["ACC_HUD"]
      self.stock_brake = cp_cam.vl["BRAKE_COMMAND"]
    if self.CP.flags & HondaFlags.BOSCH_RADARLESS:
      self.lkas_hud = cp_cam.vl["LKAS_HUD"]

    if (self.CP.flags & HondaFlags.HAS_BSM) and cp_body is not None:
      # BSM messages are on B-CAN, requires a panda forwarding B-CAN messages to CAN 0
      # more info here: https://github.com/commaai/openpilot/pull/1867
      ret.leftBlindspot = cp_body.vl["BSI_L_12f8be_Status"]["BSM_ALERT"] == 1
      ret.rightBlindspot = cp_body.vl["BSI_R_12f8bf_Status"]["BSM_ALERT"] == 1

    if (self.CP.flags & HondaFlags.ENABLE_BLINKERS) and cp_body is not None:
      # Lamp state
      self.leftBlinker_lamp = cp_body.vl["12f810_Lighting"]["LEFTSIGNAL"]
      self.rightBlinker_lamp = cp_body.vl["12f810_Lighting"]["RIGHTSIGNAL"]
      self.fog = cp_body.vl["af811_Wipers_Lighting_Output"]["FRONT_FOG"]
      self.headlights = cp_body.vl["af811_Wipers_Lighting_Output"]["HEADLIGHTS"]

      # Unfiltered stalk state
      self.leftBlinker_stalk = cp.vl["SCM_FEEDBACK"]["LEFT_BLINKER"]
      self.rightBlinker_stalk = cp.vl["SCM_FEEDBACK"]["RIGHT_BLINKER"]
      self.lighting_auto = cp_body.vl["af870_LeftStalk_Input"]["AUTO"]

      # Meter illumination: the dash dimmer steps 1 (dimmest) .. 21 (full brightness), 22 = idle
      self.illumination_step = int(cp_body.vl["12f854_Lighting"]["ILLUMINATION"])

      # The real flasher output, so the UI can blink with the car.
      # Only claim it is valid once the body bus has actually delivered it, otherwise
      # a car without the B-CAN harness would never show the turn signal icon.
      self.lamp_seen = self.lamp_seen or len(cp_body.vl_all["12f810_Lighting"]["LEFTSIGNAL"]) > 0

      # BCM KWP reply
      # reset
      self.bcm_kwp_started = False
      self.bcm_kwp_stopped = False
      self.bcm_kwp_failed = False
      # get
      self.bcm_kwp_started = cp_body.vl["BCM_16f1f0_KWP_Resp_Tester"]["D0"] == self.kwp_values.get("START_ACCEPTED")
      self.bcm_kwp_stopped = cp_body.vl["BCM_16f1f0_KWP_Resp_Tester"]["D0"] == self.kwp_values.get("STOP_ACCEPTED")
      self.bcm_kwp_failed = cp_body.vl["BCM_16f1f0_KWP_Resp_Tester"]["D0"] == self.kwp_values.get("UNSUPPORTED")

    # Parking lights on = the car is in its night/dark mode (meter + interior illumination).
    # STALK_STATUS_2 is on the powertrain bus and present on every Honda; the B-CAN lighting
    # output is OR'd in as the actual lamp state.
    self.parking_lights_on = bool(cp.vl["STALK_STATUS_2"]["PARK_LIGHTS"])
    if cp_body is not None:
      self.parking_lights_on = self.parking_lights_on or \
        bool(cp_body.vl["af811_Wipers_Lighting_Output"]["PARKING_LIGHTS"]) or \
        bool(cp_body.vl["12f854_Lighting"]["PARKING_LIGHTS"])

    ret.buttonEvents = [
      *create_button_events(self.cruise_buttons, prev_cruise_buttons, BUTTONS_DICT),
      *create_button_events(self.cruise_setting, prev_cruise_setting, SETTINGS_BUTTONS_DICT),
    ]

    return ret

  def get_can_parsers(self, CP):
    body_messages = [
      ("BCM_16f1f0_KWP_Resp_Tester", float('nan')),
    ]
    parsers = {
      Bus.pt: CANParser(DBC[CP.carFingerprint][Bus.pt], [], CanBus(CP).pt),
      Bus.cam: CANParser(DBC[CP.carFingerprint][Bus.pt], [], CanBus(CP).camera),
    }
    if Bus.body in DBC[CP.carFingerprint]:
      # bus 0 is the fork's body/radar slot; the four's body harness reports on bus 2
      body_buses = sorted({CanBus(CP).bcm, 2})
      parsers[Bus.body] = BodyParsers(DBC[CP.carFingerprint][Bus.body], body_messages, body_buses)

    return parsers
