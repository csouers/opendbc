from opendbc.car import CanBusBase
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.honda.values import HondaFlags, CarControllerParams

# CAN bus layout with relay
# 0 = ACC-CAN - radar side
# 1 = F-CAN B - powertrain
# 2 = ACC-CAN - camera side
# 3 = F-CAN A - OBDII port


class CanBus(CanBusBase):
  def __init__(self, CP=None, fingerprint=None) -> None:
    # use fingerprint if specified
    super().__init__(CP if fingerprint is None else None, fingerprint)

    # powertrain bus is split instead of radar on radarless and CAN FD Bosch
    if CP is not None and CP.flags & HondaFlags.BOSCH and not (CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD)):
      self._pt, self._radar = self.offset + 1, self.offset
      # normally steering commands are sent to radar, which forwards them to powertrain bus
      # when radar is disabled, steering commands are sent directly to powertrain bus
      self._lkas = self._pt if CP.openpilotLongitudinalControl else self._radar
    else:
      self._pt, self._radar, self._lkas = self.offset, self.offset + 1, self.offset

  @property
  def pt(self) -> int:
    return self._pt

  @property
  def radar(self) -> int:
    return self._radar

  @property
  def camera(self) -> int:
    return self.offset + 2

  @property
  def lkas(self) -> int:
    return self._lkas

  @property
  def bcm(self) -> int:
    return self.offset

  # B-CAN is forwarded to ACC-CAN radar side (CAN 0 on fake ethernet port)
  @property
  def body(self) -> int:
    return self.offset


def create_brake_command(packer, CAN, apply_brake, pump_on, pcm_override, pcm_cancel_cmd, fcw, stock_brake):
  # TODO: do we loose pressure if we keep pump off for long?
  brakelights = apply_brake > 0
  brake_rq = apply_brake > 0
  pcm_fault_cmd = False

  values = {
    "COMPUTER_BRAKE": apply_brake,
    "BRAKE_PUMP_REQUEST": pump_on,
    "CRUISE_OVERRIDE": pcm_override,
    "CRUISE_FAULT_CMD": pcm_fault_cmd,
    "CRUISE_CANCEL_CMD": pcm_cancel_cmd,
    "COMPUTER_BRAKE_REQUEST": brake_rq,
    "SET_ME_1": 1,
    "BRAKE_LIGHTS": brakelights,
    "CHIME": stock_brake["CHIME"] if fcw else 0,  # send the chime for stock fcw
    "FCW": fcw << 1,  # TODO: Why are there two bits for fcw?
    "AEB_REQ_1": 0,
    "AEB_REQ_2": 0,
    "AEB_STATUS": 0,
  }
  return packer.make_can_msg("BRAKE_COMMAND", CAN.pt, values)


def create_acc_commands(packer, CAN, enabled, active, accel, gas, vego, stopping_counter, braking_counter, CP):
  commands = []
  min_gas_accel = CarControllerParams.BOSCH_GAS_LOOKUP_BP[0]
  # engine_brake_accel = CarControllerParams.BOSCH_GAS_LOOKUP_BP[1]
  stopped = stopping_counter > 4 * 50 # allow idle stop after 4 seconds (50 Hz)
  accel = accel if not stopped else CarControllerParams.BOSCH_ACCEL_MIN
  gas_command = gas if active and accel > min_gas_accel else -3000
  accel_command = accel if active else 0
  braking = active and braking_counter > 0 and accel < 0
  standstill = active and stopped
  standstill_release = active and accel > 0 and vego < 0.5 # Hold high briefly

  # common ACC_CONTROL values
  acc_control_values = {
    'ACCEL_COMMAND': accel_command,
    'STANDSTILL': standstill, #stopping_counter > 5 * 50, # needs safety when combined with BRAKE_REQUEST
  }

  if CP.flags & HondaFlags.BOSCH_RADARLESS:
    acc_control_values.update({
      "CONTROL_ON": enabled,
      "IDLESTOP_ALLOW": standstill,
    })
  else:
    acc_control_values.update({
      # setting CONTROL_ON causes car to set POWERTRAIN_DATA->ACC_STATUS = 1
      "CONTROL_ON": 5 if enabled else 0,
      "GAS_COMMAND": gas_command,  # used for gas
      "BRAKE_LIGHTS": braking,
      "BRAKE_REQUEST": braking, # needs safety. holds brake pressure when high
      "STANDSTILL_RELEASE": standstill_release,
    })
    acc_control_on_values = {
      "SET_TO_3": 0x3,
      "CONTROL_ON": enabled,
      "SET_TO_FF": 0xff,
      "SET_TO_75": 0x75,
      "SET_TO_30": 0x30,
      "COAST_BRAKE": active and accel < -0.2,  # 0.15
      # "ACCEL_KILL": 0x00, # ALWAYS ZERO! KILLS GAS PEDAL TOO! TAKES EFFECT AFTER ENABLING/MOVING FORWARD THE FIRST TIME
      # "POS_ACCEL": active and not braking,
    }
    commands.append(packer.make_can_msg("ACC_CONTROL_ON", CAN.pt, acc_control_on_values))

  commands.append(packer.make_can_msg("ACC_CONTROL", CAN.pt, acc_control_values))
  return commands


def create_steering_control(packer, CAN, apply_torque, lkas_active, tja_control):
  values = {
    "STEER_TORQUE": apply_torque if lkas_active else 0,
    "STEER_TORQUE_REQUEST": lkas_active,
    # "RDM": lkas_active,
    # "STEER_DOWN_TO_ZERO": lkas_active,
    # "SET_ME_X00": 0xff >> 1, # kills steering
    # "SET_ME_X00_2": 0xff,
  }

  if tja_control:
    values["STEER_DOWN_TO_ZERO"] = lkas_active

  return packer.make_can_msg("STEERING_CONTROL", CAN.lkas, values)


def create_bosch_supplemental_1(packer, CAN):
  # non-active params
  values = {
    "SET_ME_X04": 0x04,
    "SET_ME_X80": 0x80,
    "SET_ME_X10": 0x10,
  }
  return packer.make_can_msg("BOSCH_SUPPLEMENTAL_1", CAN.lkas, values)


def create_acc_hud(packer, bus, CP, enabled, pcm_speed, pcm_accel, hud_control, hud_v_cruise, is_metric, acc_hud, braking):
  acc_hud_values = {
    'CRUISE_SPEED': hud_v_cruise if not braking else 252,
    'ENABLE_MINI_CAR': 1 if enabled else 0,
    # only moves the lead car without ACC_ON
    'HUD_DISTANCE': hud_control.leadDistanceBars,  # wraps to 0 at 4 bars
    'IMPERIAL_UNIT': int(not is_metric),
    'HUD_LEAD': 2 if enabled and hud_control.leadVisible else 1 if enabled else 0,
    'SET_ME_X01_2': 1,
  }

  if CP.flags & HondaFlags.BOSCH:
    acc_hud_values['ACC_ON'] = int(enabled)
    acc_hud_values['FCM_OFF'] = 1
    acc_hud_values['FCM_OFF_2'] = 1
    acc_hud_values['ICONS'] = int(bool(hud_control.e2e) << 1)
  else:
    # Shows the distance bars, TODO: stock camera shows updates temporarily while disabled
    acc_hud_values['ACC_ON'] = int(enabled)
    acc_hud_values['PCM_SPEED'] = pcm_speed * CV.MS_TO_KPH
    acc_hud_values['PCM_GAS'] = pcm_accel
    acc_hud_values['SET_ME_X01'] = 1
    acc_hud_values['FCM_OFF'] = acc_hud['FCM_OFF']
    acc_hud_values['FCM_OFF_2'] = acc_hud['FCM_OFF_2']
    acc_hud_values['FCM_PROBLEM'] = acc_hud['FCM_PROBLEM']
    acc_hud_values['ICONS'] = acc_hud['ICONS']

  return packer.make_can_msg("ACC_HUD", bus, acc_hud_values)


def create_lkas_hud(packer, bus, CP, hud_control, lat_active, steering_available, alert_steer_required, lkas_hud, ldw):
  commands = []

  lkas_hud_values = {
    'LKAS_READY': 1,
    'LKAS_STATE_CHANGE': 1,
    'STEERING_REQUIRED': alert_steer_required,
    'SOLID_LANES': hud_control.lanesVisible,
    'BEEP': 0,
    'RDM_HUD': ldw,
    'LDW_ICON': hud_control.e2e,
  }

  if CP.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD):
    lkas_hud_values['LANE_LINES'] = 3
    lkas_hud_values['DASHED_LANES'] = hud_control.lanesVisible

    # car likely needs to see LKAS_PROBLEM fall within a specific time frame, so forward from camera
    # TODO: needed for Bosch CAN FD?
    if CP.flags & HondaFlags.BOSCH_RADARLESS:
      lkas_hud_values['LKAS_PROBLEM'] = lkas_hud['LKAS_PROBLEM']

  if not (CP.flags & HondaFlags.BOSCH_EXT_HUD):
    lkas_hud_values['RDM_OFF'] = 1
    lkas_hud_values['LANE_ASSIST_BEEP_OFF'] = 1

  # New HUD concept for selected Bosch cars, overwrites some of the above
  # TODO: make global across all Honda if feedback is favorable
  if CP.flags & HondaFlags.BOSCH_ALT_RADAR:
    lkas_hud_values['DASHED_LANES'] = steering_available
    lkas_hud_values['SOLID_LANES'] = lat_active

  if CP.flags & HondaFlags.BOSCH_EXT_HUD and not CP.openpilotLongitudinalControl:
    commands.append(packer.make_can_msg('LKAS_HUD_A', bus, lkas_hud_values))
    commands.append(packer.make_can_msg('LKAS_HUD_B', bus, lkas_hud_values))
  else:
    commands.append(packer.make_can_msg('LKAS_HUD', bus, lkas_hud_values))
  return commands


def create_radar_hud(packer, bus):
  radar_hud_values = {
    'CMBS_OFF': 0x01,
    'SET_TO_1': 0x01,
  }

  return packer.make_can_msg('RADAR_HUD', bus, radar_hud_values)


def create_legacy_brake_command(packer, bus, fcw):
  return packer.make_can_msg("LEGACY_BRAKE_COMMAND", bus, {'AEB_BRAKE_ALERT': fcw})


def spam_buttons_command(packer, CAN, button_val, CP):
  values = {
    'CRUISE_BUTTONS': button_val,
    'CRUISE_SETTING': 0,
  }
  # send buttons to camera on radarless (camera does ACC) cars
  bus = CAN.camera if CP.flags & HondaFlags.BOSCH_RADARLESS else CAN.pt
  return packer.make_can_msg("SCM_BUTTONS", bus, values)


def honda_checksum(address: int, sig, d: bytearray) -> int:
  s = 0
  extended = address > 0x7FF
  addr = address
  while addr:
    s += addr & 0xF
    addr >>= 4
  for i in range(len(d)):
    x = d[i]
    if i == len(d) - 1:
      x >>= 4
    s += (x & 0xF) + (x >> 4)
  s = 8 - s
  if extended:
    s += 3
  return s & 0xF


def create_kwp_can_msg(packer, cmd, bus):
  if cmd == 'left':
    values = {'D0': 0x30,
              'D1': 0x0a,
              'D2': 0x0f,
             }
  elif cmd == 'right':
    values = {'D0': 0x30,
              'D1': 0x0b,
              'D2': 0x0f,
             }
  elif cmd == 'fog':
    values = {'D0': 0x30,
              'D1': 0x20,
              'D2': 0x0f,
             }
    print('hondacan: should be sendng fog lamp')
  else:
    return [384899312, b' ', bus] # default is a special 1 byte cancel
  return packer.make_can_msg("Tester_16f118_KWP_Req_BCM", bus, values)
