#!/usr/bin/env python3
from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.interfaces import RadarInterfaceBase
from opendbc.car.honda.values import DBC, HondaFlags
from opendbc.car.honda import hondacan


def _create_nidec_can_parser(car_fingerprint):
  radar_messages = [0x400] + list(range(0x430, 0x43A)) + list(range(0x440, 0x446))
  messages = [(m, 20) for m in radar_messages]
  return CANParser(DBC[car_fingerprint][Bus.radar], messages, 1)


# This is the Tesla Radar interface brought back from dead.

class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.CAN = hondacan.CanBus(CP)
    self.radar_fault = False
    self.radar_wrong_config = False
    # trackIds the sensor classifies as vehicles. Carried out-of-band (radarTrackClass event) so
    # opendbc/car/car.capnp needs no fork-specific RadarPoint field.
    self.vehicle_track_ids: set[int] = set()
    self.tesla_radar = bool(CP.flags & HondaFlags.TESLA_RADAR)

    if self.tesla_radar:
      messages = [('TeslaRadarSguInfo', 9)]
      self.num_points = 32
      self.trigger_msg = 878 # dec

      for i in range(self.num_points):
        messages.extend([
          (f'RadarPoint{i}_A', 16),
          (f'RadarPoint{i}_B', 16),
        ])

      self.rcp = CANParser(DBC[CP.carFingerprint][Bus.radar], messages, self.CAN.radar)
    else:
      # Nidec only. With Bosch radar we're only steering for now, so radard gets no points
      self.rcp = None if CP.radarUnavailable else _create_nidec_can_parser(CP.carFingerprint)
      self.trigger_msg = 0x445

  def update(self, can_strings):
    if not self.tesla_radar:
      return super().update(can_strings)

    if self.rcp is None:
      return super().update(None)

    vls = self.rcp.update(can_strings)
    self.updated_messages.update(vls)

    if self.trigger_msg not in self.updated_messages:
      return None

    ret = structs.RadarData()

    radar_status = self.rcp.vl['TeslaRadarSguInfo']
    # TODO: bring back sgufail. would need to add a lot to the can gateway. \
    # idk if its even possible to fake enough of the tesla on that board to make it happen.
    # maybe put it in OP
    self.radar_fault = bool(radar_status['RADC_HWFail'] or radar_status['RADC_SensorDirty'])

    # Errors
    if not self.rcp.can_valid:
      ret.errors.canError = True
    if self.radar_fault:
      ret.errors.radarFault = True
    if self.radar_wrong_config:
      ret.errors.wrongConfig = True

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
          self.vehicle_track_ids.discard(self.pts[i].trackId)
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
      # Bosch object class: 1=car, 2=truck, 3=pedestrian, 4=motorcycle, 5=bicycle, 6=wide, 0=unknown
      if int(msg_b['Class']) in (1, 2, 4, 5, 6):
        self.vehicle_track_ids.add(self.pts[i].trackId)
      else:
        self.vehicle_track_ids.discard(self.pts[i].trackId)

    ret.points = list(self.pts.values())
    self.updated_messages.clear()

    return ret

  def _update(self, rcp, updated_messages):
    ret = structs.RadarData()

    for ii in sorted(updated_messages):
      cpt = rcp.vl[ii]
      if ii == 0x400:
        # check for radar faults
        self.radar_fault = cpt['RADAR_STATE'] != 0x79
        self.radar_wrong_config = cpt['RADAR_STATE'] == 0x69
      elif cpt['LONG_DIST'] < 255:
        if ii not in self.pts or cpt['NEW_TRACK']:
          self.pts[ii] = structs.RadarData.RadarPoint()
          self.pts[ii].trackId = self.track_id
          self.track_id += 1
        self.pts[ii].dRel = cpt['LONG_DIST']  # from front of car
        self.pts[ii].yRel = -cpt['LAT_DIST']  # in car frame's y axis, left is positive
        self.pts[ii].vRel = cpt['REL_SPEED']
      else:
        if ii in self.pts:
          del self.pts[ii]

    if not rcp.can_valid:
      ret.errors.canError = True
    if self.radar_fault:
      ret.errors.radarFault = True
    if self.radar_wrong_config:
      ret.errors.wrongConfig = True

    ret.points = list(self.pts.values())

    return ret
