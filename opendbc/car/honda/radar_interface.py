#!/usr/bin/env python3
from opendbc.can.parser import CANParser
from opendbc.car import structs
from opendbc.car.interfaces import RadarInterfaceBase
from opendbc.car.honda.values import DBC, HondaFlags
from opendbc.car.honda import hondacan


class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.CP = CP
    self.CAN = hondacan.CanBus(CP)
    self.rcp = None
    if self.CP.flags & HondaFlags.TESLA_RADAR:
      messages = [('TeslaRadarSguInfo', 10)]
      self.num_points = 32
      self.trigger_msg = 878 # dec

      for i in range(self.num_points):
        messages.extend([
          (f'RadarPoint{i}_A', 16),
          (f'RadarPoint{i}_B', 16),
        ])

      self.rcp = CANParser(DBC[CP.carFingerprint]['radar'], messages, self.CAN.radar)
      self.updated_messages = set()
      self.track_id = 0

      self.radar_fault = False
      self.radar_wrong_config = False

  def update(self, can_strings):
    if self.rcp is None:
      return super().update(None)

    values = self.rcp.update_strings(can_strings)
    self.updated_messages.update(values)

    if self.trigger_msg not in self.updated_messages:
      return None

    ret = structs.RadarData()

    # Errors
    errors = []
    if not self.rcp.can_valid:
      errors.append("canError")
    if self.radar_fault:
      errors.append("fault")
    if self.radar_wrong_config:
      errors.append("wrongConfig")

    radar_status = self.rcp.vl['TeslaRadarSguInfo']
    # TODO: bring back sgufail. would need to add a lot to the can gateway. \
    # idk if its even possible to fake enough of the tesla on that board to make it happen.
    # maybe put it in OP
    self.radar_fault = bool(radar_status['RADC_HWFail'] or radar_status['RADC_SensorDirty'])

    ret.errors = errors

# Radar tracks
    for i in range(self.num_points):
      msg_a = self.rcp.vl[f'RadarPoint{i}_A']
      msg_b = self.rcp.vl[f'RadarPoint{i}_B']

      # Make sure msg A and B are together
      if msg_a['Index'] != msg_b['Index2']:
        continue

      # Check if it's a valid track
      if not msg_a['Tracked']:
        if i in self.pts:
          del self.pts[i]
        continue

      # New track!
      if i not in self.pts:
        self.pts[i] = structs.RadarData.RadarPoint.new_message()
        self.pts[i].trackId = self.track_id
        self.track_id += 1

      # Parse track data
      self.pts[i].dRel = msg_a['LongDist']
      self.pts[i].yRel = msg_a['LatDist'] + 0.57 # 10th Gen Civic Hatchback
      self.pts[i].vRel = msg_a['LongSpeed']
      self.pts[i].aRel = msg_a['LongAccel']
      self.pts[i].yvRel = msg_b['LatSpeed']
      self.pts[i].measured = bool(msg_a['Meas'])

    ret.points = list(self.pts.values())
    self.updated_messages.clear()

    return ret
