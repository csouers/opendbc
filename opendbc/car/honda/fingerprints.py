from opendbc.car.structs import CarParams
from opendbc.car.honda.values import CAR

Ecu = CarParams.Ecu

# Modified FW can be identified by the second dash being replaced by a comma
# For example: `b'39990-TVA,A150\x00\x00'`
#
# TODO: vsa is "essential" for fpv2 but doesn't appear on some CAR.FREED models


FW_VERSIONS = {
  CAR.HONDA_ACCORD: {
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TVC-A910\x00\x00',
      b'54008-TWA-A910\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-6A7-A220\x00\x00',
      b'28101-6A7-A230\x00\x00',
      b'28101-6A7-A320\x00\x00',
      b'28101-6A7-A330\x00\x00',
      b'28101-6A7-A410\x00\x00',
      b'28101-6A7-A510\x00\x00',
      b'28101-6A7-A610\x00\x00',
      b'28101-6A7-A710\x00\x00',
      b'28101-6A9-H140\x00\x00',
      b'28101-6A9-H420\x00\x00',
      b'28102-6B8-A560\x00\x00',
      b'28102-6B8-A570\x00\x00',
      b'28102-6B8-A700\x00\x00',
      b'28102-6B8-A800\x00\x00',
      b'28102-6B8-C560\x00\x00',
      b'28102-6B8-C570\x00\x00',
      b'28102-6B8-M520\x00\x00',
      b'28102-6B8-R700\x00\x00',
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'46114-TVA-A050\x00\x00',
      b'46114-TVA-A060\x00\x00',
      b'46114-TVA-A080\x00\x00',
      b'46114-TVA-A120\x00\x00',
      b'46114-TVA-A320\x00\x00',
      b'46114-TVE-H550\x00\x00',
      b'46114-TVE-H560\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TVA-B040\x00\x00',
      b'57114-TVA-B050\x00\x00',
      b'57114-TVA-B060\x00\x00',
      b'57114-TVA-B530\x00\x00',
      b'57114-TVA-C040\x00\x00',
      b'57114-TVA-C050\x00\x00',
      b'57114-TVA-C060\x00\x00',
      b'57114-TVA-C530\x00\x00',
      b'57114-TVA-E520\x00\x00',
      b'57114-TVE-H250\x00\x00',
      b'57114-TWA-A040\x00\x00',
      b'57114-TWA-A050\x00\x00',
      b'57114-TWA-A530\x00\x00',
      b'57114-TWA-B520\x00\x00',
      b'57114-TWA-C510\x00\x00',
      b'57114-TWB-H030\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TBX-H120\x00\x00',
      b'39990-TVA,A150\x00\x00',
      b'39990-TVA-A140\x00\x00',
      b'39990-TVA-A150\x00\x00',
      b'39990-TVA-A160\x00\x00',
      b'39990-TVA-A340\x00\x00',
      b'39990-TVA-X030\x00\x00',
      b'39990-TVA-X040\x00\x00',
      b'39990-TVE-H130\x00\x00',
      b'39990-TWB-H120\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TBX-H230\x00\x00',
      b'77959-TVA-A460\x00\x00',
      b'77959-TVA-F330\x00\x00',
      b'77959-TVA-H230\x00\x00',
      b'77959-TVA-L420\x00\x00',
      b'77959-TVA-X330\x00\x00',
      b'77959-TWA-A440\x00\x00',
      b'77959-TWA-L420\x00\x00',
      b'77959-TWB-H220\x00\x00',
    ],
    (Ecu.hud, 0x18da61f1, None): [
      b'78209-TVA-A010\x00\x00',
      b'78209-TVA-A110\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TBX-H140\x00\x00',
      b'36802-TVA-A150\x00\x00',
      b'36802-TVA-A160\x00\x00',
      b'36802-TVA-A170\x00\x00',
      b'36802-TVA-A180\x00\x00',
      b'36802-TVA-A330\x00\x00',
      b'36802-TVC-A330\x00\x00',
      b'36802-TVE-H070\x00\x00',
      b'36802-TWA-A070\x00\x00',
      b'36802-TWA-A080\x00\x00',
      b'36802-TWA-A210\x00\x00',
      b'36802-TWA-A330\x00\x00',
      b'36802-TWB-H060\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TBX-H130\x00\x00',
      b'36161-TVA-A060\x00\x00',
      b'36161-TVA-A330\x00\x00',
      b'36161-TVC-A330\x00\x00',
      b'36161-TVE-H050\x00\x00',
      b'36161-TWA-A070\x00\x00',
      b'36161-TWA-A330\x00\x00',
      b'36161-TWB-H040\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TVA-A010\x00\x00',
      b'38897-TVA-A020\x00\x00',
      b'38897-TVA-A230\x00\x00',
      b'38897-TVA-A240\x00\x00',
      b'38897-TWA-A120\x00\x00',
      b'38897-TWD-J020\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC: {
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5CG-A040\x00\x00',
      b'28101-5CG-A050\x00\x00',
      b'28101-5CG-A070\x00\x00',
      b'28101-5CG-A080\x00\x00',
      b'28101-5CG-A320\x00\x00',
      b'28101-5CG-A810\x00\x00',
      b'28101-5CG-A820\x00\x00',
      b'28101-5DJ-A040\x00\x00',
      b'28101-5DJ-A060\x00\x00',
      b'28101-5DJ-A510\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TBA-A540\x00\x00',
      b'57114-TBA-A550\x00\x00',
      b'57114-TBA-A560\x00\x00',
      b'57114-TBA-A570\x00\x00',
      b'57114-TEA-Q220\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TBA,A030\x00\x00',
      b'39990-TBA-A030\x00\x00',
      b'39990-TBG-A030\x00\x00',
      b'39990-TEA-T020\x00\x00',
      b'39990-TEG-A010\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TBA-A030\x00\x00',
      b'77959-TBA-A040\x00\x00',
      b'77959-TBG-A020\x00\x00',
      b'77959-TBG-A030\x00\x00',
      b'77959-TEA-Q820\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TBA-A020\x00\x00',
      b'36161-TBA-A030\x00\x00',
      b'36161-TBA-A040\x00\x00',
      b'36161-TBC-A020\x00\x00',
      b'36161-TBC-A030\x00\x00',
      b'36161-TED-Q320\x00\x00',
      b'36161-TEG-A010\x00\x00',
      b'36161-TEG-A020\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TBA-A010\x00\x00',
      b'38897-TBA-A020\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC_BOSCH: {
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5CG-A920\x00\x00',
      b'28101-5CG-AB10\x00\x00',
      b'28101-5CG-C110\x00\x00',
      b'28101-5CG-C220\x00\x00',
      b'28101-5CG-C320\x00\x00',
      b'28101-5CG-G020\x00\x00',
      b'28101-5CG-L020\x00\x00',
      b'28101-5CK-A130\x00\x00',
      b'28101-5CK-A140\x00\x00',
      b'28101-5CK-A150\x00\x00',
      b'28101-5CK-C130\x00\x00',
      b'28101-5CK-C140\x00\x00',
      b'28101-5CK-C150\x00\x00',
      b'28101-5CK-G210\x00\x00',
      b'28101-5CK-J710\x00\x00',
      b'28101-5CK-Q610\x00\x00',
      b'28101-5DJ-A610\x00\x00',
      b'28101-5DJ-A710\x00\x00',
      b'28101-5DV-E330\x00\x00',
      b'28101-5DV-E610\x00\x00',
      b'28101-5DV-E820\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TBG-A330\x00\x00',
      b'57114-TBG-A340\x00\x00',
      b'57114-TBG-A350\x00\x00',
      b'57114-TGG-A340\x00\x00',
      b'57114-TGG-C320\x00\x00',
      b'57114-TGG-G320\x00\x00',
      b'57114-TGG-L320\x00\x00',
      b'57114-TGG-L330\x00\x00',
      b'57114-TGH-L130\x00\x00',
      b'57114-TGK-T320\x00\x00',
      b'57114-TGL-G330\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TBA-C020\x00\x00',
      b'39990-TBA-C120\x00\x00',
      b'39990-TEA-T820\x00\x00',
      b'39990-TEZ-T020\x00\x00',
      b'39990-TGG,A020\x00\x00',
      b'39990-TGG,A120\x00\x00',
      b'39990-TGG-A020\x00\x00',
      b'39990-TGG-A120\x00\x00',
      b'39990-TGG-J510\x00\x00',
      b'39990-TGH-J530\x00\x00',
      b'39990-TGL-E130\x00\x00',
      b'39990-TGN-E120\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TBA-A060\x00\x00',
      b'77959-TBG-A050\x00\x00',
      b'77959-TEA-G020\x00\x00',
      b'77959-TGG-A020\x00\x00',
      b'77959-TGG-A030\x00\x00',
      b'77959-TGG-E010\x00\x00',
      b'77959-TGG-G010\x00\x00',
      b'77959-TGG-G110\x00\x00',
      b'77959-TGG-J320\x00\x00',
      b'77959-TGG-Z820\x00\x00',
      b'77959-TGH-J110\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TBA-A150\x00\x00',
      b'36802-TBA-A160\x00\x00',
      b'36802-TFJ-G060\x00\x00',
      b'36802-TGG-A050\x00\x00',
      b'36802-TGG-A060\x00\x00',
      b'36802-TGG-A070\x00\x00',
      b'36802-TGG-A130\x00\x00',
      b'36802-TGG-G040\x00\x00',
      b'36802-TGG-G130\x00\x00',
      b'36802-TGH-A140\x00\x00',
      b'36802-TGK-Q120\x00\x00',
      b'36802-TGL-G040\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TBA-A130\x00\x00',
      b'36161-TBA-A140\x00\x00',
      b'36161-TFJ-G070\x00\x00',
      b'36161-TGG-A060\x00\x00',
      b'36161-TGG-A080\x00\x00',
      b'36161-TGG-A120\x00\x00',
      b'36161-TGG-G050\x00\x00',
      b'36161-TGG-G070\x00\x00',
      b'36161-TGG-G130\x00\x00',
      b'36161-TGG-G140\x00\x00',
      b'36161-TGH-A140\x00\x00',
      b'36161-TGK-Q120\x00\x00',
      b'36161-TGL-G050\x00\x00',
      b'36161-TGL-G070\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TBA-A020\x00\x00',
      b'38897-TBA-A110\x00\x00',
      b'38897-TGH-A010\x00\x00',
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'39494-TGL-G030\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC_BOSCH_DIESEL: {
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-59Y-G220\x00\x00',
      b'28101-59Y-G620\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TGN-E320\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TFK-G020\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TFK-G210\x00\x00',
      b'77959-TGN-G220\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TFK-G130\x00\x00',
      b'36802-TGN-G130\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TGN-E010\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TFK-G130\x00\x00',
      b'36161-TGN-G130\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TBA-A020\x00\x00',
    ],
  },
  CAR.HONDA_CRV: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-T1W-A230\x00\x00',
      b'57114-T1W-A240\x00\x00',
      b'57114-TFF-A940\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T0A-A230\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T1W-A830\x00\x00',
      b'36161-T1W-C830\x00\x00',
      b'36161-T1X-A830\x00\x00',
    ],
  },
  CAR.HONDA_CRV_5G: {
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5RG-A020\x00\x00',
      b'28101-5RG-A030\x00\x00',
      b'28101-5RG-A040\x00\x00',
      b'28101-5RG-A120\x00\x00',
      b'28101-5RG-A220\x00\x00',
      b'28101-5RH-A020\x00\x00',
      b'28101-5RH-A030\x00\x00',
      b'28101-5RH-A040\x00\x00',
      b'28101-5RH-A120\x00\x00',
      b'28101-5RH-A220\x00\x00',
      b'28101-5RL-Q010\x00\x00',
      b'28101-5RM-F010\x00\x00',
      b'28101-5RM-K010\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TLA-A040\x00\x00',
      b'57114-TLA-A050\x00\x00',
      b'57114-TLA-A060\x00\x00',
      b'57114-TLB-A830\x00\x00',
      b'57114-TMC-Z040\x00\x00',
      b'57114-TMC-Z050\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TLA,A040\x00\x00',
      b'39990-TLA-A040\x00\x00',
      b'39990-TLA-A110\x00\x00',
      b'39990-TLA-A220\x00\x00',
      b'39990-TME-T030\x00\x00',
      b'39990-TME-T120\x00\x00',
      b'39990-TMT-T010\x00\x00',
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'46114-TLA-A040\x00\x00',
      b'46114-TLA-A050\x00\x00',
      b'46114-TLA-A930\x00\x00',
      b'46114-TMC-U020\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TLA-A010\x00\x00',
      b'38897-TLA-A110\x00\x00',
      b'38897-TNY-G010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TLA-A040\x00\x00',
      b'36802-TLA-A050\x00\x00',
      b'36802-TLA-A060\x00\x00',
      b'36802-TLA-A070\x00\x00',
      b'36802-TMC-Q040\x00\x00',
      b'36802-TMC-Q070\x00\x00',
      b'36802-TNY-A030\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TLA-A060\x00\x00',
      b'36161-TLA-A070\x00\x00',
      b'36161-TLA-A080\x00\x00',
      b'36161-TMC-Q020\x00\x00',
      b'36161-TMC-Q030\x00\x00',
      b'36161-TMC-Q040\x00\x00',
      b'36161-TNY-A020\x00\x00',
      b'36161-TNY-A030\x00\x00',
      b'36161-TNY-A040\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TLA-A240\x00\x00',
      b'77959-TLA-A250\x00\x00',
      b'77959-TLA-A320\x00\x00',
      b'77959-TLA-A410\x00\x00',
      b'77959-TLA-A420\x00\x00',
      b'77959-TLA-Q040\x00\x00',
      b'77959-TLA-Z040\x00\x00',
      b'77959-TMM-F040\x00\x00',
    ],
  },
  CAR.HONDA_CRV_EU: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-T1V-G920\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T1V-G520\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-T1V-G010\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5LH-E120\x00\x00',
      b'28103-5LH-E100\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T1G-G940\x00\x00',
    ],
  },
  CAR.HONDA_CRV_HYBRID: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TMB-H030\x00\x00',
      b'57114-TPA-G020\x00\x00',
      b'57114-TPG-A020\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TMA-H020\x00\x00',
      b'39990-TPA-G030\x00\x00',
      b'39990-TPG-A020\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TMA-H110\x00\x00',
      b'38897-TPG-A110\x00\x00',
      b'38897-TPG-A210\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TMB-H510\x00\x00',
      b'54008-TMB-H610\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TMB-H040\x00\x00',
      b'36161-TPA-E050\x00\x00',
      b'36161-TPG-A030\x00\x00',
      b'36161-TPG-A040\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TMB-H040\x00\x00',
      b'36802-TPA-E040\x00\x00',
      b'36802-TPG-A020\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TLA-C320\x00\x00',
      b'77959-TLA-C410\x00\x00',
      b'77959-TLA-C420\x00\x00',
      b'77959-TLA-G220\x00\x00',
      b'77959-TLA-H240\x00\x00',
    ],
  },
  CAR.HONDA_FIT: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-T5R-L020\x00\x00',
      b'57114-T5R-L220\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-T5R-C020\x00\x00',
      b'39990-T5R-C030\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-T5A-J010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T5R-A040\x00\x00',
      b'36161-T5R-A240\x00\x00',
      b'36161-T5R-A520\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T5R-A230\x00\x00',
    ],
  },
  CAR.HONDA_FREED: {
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TDK-J010\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TDK-J050\x00\x00',
      b'39990-TDK-N020\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TDK-J120\x00\x00',
      b'57114-TDK-J330\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TDK-J070\x00\x00',
      b'36161-TDK-J080\x00\x00',
      b'36161-TDK-J530\x00\x00',
    ],
  },
  CAR.HONDA_ODYSSEY: {
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-THR-A010\x00\x00',
      b'38897-THR-A020\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-THR-A020\x00\x00',
      b'39990-THR-A030\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-THR-A010\x00\x00',
      b'77959-THR-A110\x00\x00',
      b'77959-THR-X010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-THR-A020\x00\x00',
      b'36161-THR-A030\x00\x00',
      b'36161-THR-A110\x00\x00',
      b'36161-THR-A720\x00\x00',
      b'36161-THR-A730\x00\x00',
      b'36161-THR-A810\x00\x00',
      b'36161-THR-A910\x00\x00',
      b'36161-THR-C010\x00\x00',
      b'36161-THR-D110\x00\x00',
      b'36161-THR-K020\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5NZ-A110\x00\x00',
      b'28101-5NZ-A310\x00\x00',
      b'28101-5NZ-C310\x00\x00',
      b'28102-5MX-A001\x00\x00',
      b'28102-5MX-A600\x00\x00',
      b'28102-5MX-A610\x00\x00',
      b'28102-5MX-A700\x00\x00',
      b'28102-5MX-A710\x00\x00',
      b'28102-5MX-A900\x00\x00',
      b'28102-5MX-A910\x00\x00',
      b'28102-5MX-C001\x00\x00',
      b'28102-5MX-C610\x00\x00',
      b'28102-5MX-C910\x00\x00',
      b'28102-5MX-D001\x00\x00',
      b'28102-5MX-D710\x00\x00',
      b'28102-5MX-K610\x00\x00',
      b'28103-5NZ-A100\x00\x00',
      b'28103-5NZ-A300\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-THR-A040\x00\x00',
      b'57114-THR-A110\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-THR-A020\x00\x00',
    ],
  },
  CAR.HONDA_ODYSSEY_CHN: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-T6D-H220\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-T6A-J010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T6A-P040\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T6A-P110\x00\x00',
    ],
  },
  CAR.HONDA_ODYSSEY_BOSCH: {
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28102-5MX-A100\x00\x00',  # 2021 Touring, 2022 Elite - c443ca9eee127f66
      b'28102-5MX-A200\x00\x00',  # 2023 (unknown trim), 2024 Touring - 680f1d45486d2971
      b'28102-5MX-A410\x00\x00',  # 2025 Elite - e0c2250590b16ce0
      b'28102-5MX-C100\x00\x00',  # 2022 Touring
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'46114-THR-A530\x00\x00', # 2021+ - c443ca9eee127f66
      b'46114-THR-A540\x00\x00', # 2023 (unknown trim), 2024 Touring - 680f1d45486d2971
      b'46114-THR-A720\x00\x00', # 2025 Elite - e0c2250590b16ce0
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-THR-A130\x00\x00', # 2021+ - c443ca9eee127f66
      b'38897-THR-A320\x00\x00', # 2025 Elite - e0c2250590b16ce0
      b'38897-THR-A410\x00\x00', # 2024 Touring - 680f1d45486d2971
    ],
    (Ecu.eps, 0x18da30f1, None): [
        b'39990-THR-A050\x00\x00', #2021+ - 680f1d45486d2971
        b'39990-THR-A110\x00\x00', # 2025 Elite - e0c2250590b16ce0
        ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [b'36802-THR-A220\x00\x00'], # 2021+ - 680f1d45486d2971
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-THR-A220\x00\x00', # 2021+ - c443ca9eee127f66
      b'36161-THR-A230\x00\x00', # 2023 (unknown trim), 2024 Touring - 680f1d45486d2971
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [b'54008-THR-A310\x00\x00'], # 2021+ - 680f1d45486d2971
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-THR-A220\x00\x00', # 2021+
      b'77959-THR-A230\x00\x00', # 2023 (unknown trim), 2024 Touring - 680f1d45486d2971
      b'77959-THR-A320\x00\x00', # 2025 Elite - e0c2250590b16ce0
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-THR-A230\x00\x00', # 2021+
      b'57114-THR-A240\x00\x00', # 2022 Elite, 2024 Touring - 680f1d45486d2971
      b'57114-THR-A520\x00\x00', # 2025 Elite - e0c2250590b16ce0
    ],
  },
  CAR.HONDA_PILOT: {
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TG7-A520\x00\x00',
      b'54008-TG7-A530\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5EY-A040\x00\x00',
      b'28101-5EY-A050\x00\x00',
      b'28101-5EY-A100\x00\x00',
      b'28101-5EY-A430\x00\x00',
      b'28101-5EY-A500\x00\x00',
      b'28101-5EZ-A050\x00\x00',
      b'28101-5EZ-A060\x00\x00',
      b'28101-5EZ-A100\x00\x00',
      b'28101-5EZ-A210\x00\x00',
      b'28101-5EZ-A330\x00\x00',
      b'28101-5EZ-A430\x00\x00',
      b'28101-5EZ-A500\x00\x00',
      b'28101-5EZ-A600\x00\x00',
      b'28101-5EZ-A700\x00\x00',
      b'28103-5EY-A110\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TG7-A030\x00\x00',
      b'38897-TG7-A040\x00\x00',
      b'38897-TG7-A110\x00\x00',
      b'38897-TG7-A210\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TG7-A030\x00\x00',
      b'39990-TG7-A040\x00\x00',
      b'39990-TG7-A060\x00\x00',
      b'39990-TG7-A070\x00\x00',
      b'39990-TGS-A230\x00\x00',
      b'39990-TGS-A320\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TG7-A310\x00\x00',
      b'36161-TG7-A520\x00\x00',
      b'36161-TG7-A630\x00\x00',
      b'36161-TG7-A720\x00\x00',
      b'36161-TG7-A820\x00\x00',
      b'36161-TG7-A930\x00\x00',
      b'36161-TG7-C520\x00\x00',
      b'36161-TG7-D520\x00\x00',
      b'36161-TG7-D630\x00\x00',
      b'36161-TG7-Y630\x00\x00',
      b'36161-TG8-A410\x00\x00',
      b'36161-TG8-A520\x00\x00',
      b'36161-TG8-A630\x00\x00',
      b'36161-TG8-A720\x00\x00',
      b'36161-TG8-A830\x00\x00',
      b'36161-TGS-A030\x00\x00',
      b'36161-TGS-A130\x00\x00',
      b'36161-TGS-A220\x00\x00',
      b'36161-TGS-A320\x00\x00',
      b'36161-TGT-A030\x00\x00',
      b'36161-TGT-A130\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TG7-A020\x00\x00',
      b'77959-TG7-A110\x00\x00',
      b'77959-TG7-A210\x00\x00',
      b'77959-TG7-Y210\x00\x00',
      b'77959-TGS-A010\x00\x00',
      b'77959-TGS-A110\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TG7-A130\x00\x00',
      b'57114-TG7-A140\x00\x00',
      b'57114-TG7-A230\x00\x00',
      b'57114-TG7-A240\x00\x00',
      b'57114-TG7-A630\x00\x00',
      b'57114-TG7-A730\x00\x00',
      b'57114-TG8-A140\x00\x00',
      b'57114-TG8-A230\x00\x00',
      b'57114-TG8-A240\x00\x00',
      b'57114-TG8-A630\x00\x00',
      b'57114-TG8-A730\x00\x00',
      b'57114-TGS-A530\x00\x00',
      b'57114-TGT-A530\x00\x00',
    ],
  },
  CAR.ACURA_RDX: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TX4-A220\x00\x00',
      b'57114-TX5-A220\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TX4-A030\x00\x00',
      b'36161-TX5-A030\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TX4-B010\x00\x00',
      b'77959-TX4-C010\x00\x00',
      b'77959-TX4-C020\x00\x00',
    ],
  },
  CAR.ACURA_RDX_3G: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TJB-A030\x00\x00',
      b'57114-TJB-A040\x00\x00',
      b'57114-TJB-A120\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TJB-A040\x00\x00',
      b'36802-TJB-A050\x00\x00',
      b'36802-TJB-A540\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TJB-A040\x00\x00',
      b'36161-TJB-A530\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TJB-A520\x00\x00',
      b'54008-TJB-A530\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28102-5YK-A610\x00\x00',
      b'28102-5YK-A620\x00\x00',
      b'28102-5YK-A630\x00\x00',
      b'28102-5YK-A700\x00\x00',
      b'28102-5YK-A711\x00\x00',
      b'28102-5YK-A800\x00\x00',
      b'28102-5YL-A620\x00\x00',
      b'28102-5YL-A700\x00\x00',
      b'28102-5YL-A711\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TJB-A040\x00\x00',
      b'77959-TJB-A120\x00\x00',
      b'77959-TJB-A210\x00\x00',
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'46114-TJB-A040\x00\x00',
      b'46114-TJB-A050\x00\x00',
      b'46114-TJB-A060\x00\x00',
      b'46114-TJB-A120\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TJB-A040\x00\x00',
      b'38897-TJB-A110\x00\x00',
      b'38897-TJB-A120\x00\x00',
      b'38897-TJB-A220\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TJB-A030\x00\x00',
      b'39990-TJB-A040\x00\x00',
      b'39990-TJB-A070\x00\x00',
      b'39990-TJB-A130\x00\x00',
    ],
  },
  CAR.HONDA_RIDGELINE: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-T6Z-A020\x00\x00',
      b'39990-T6Z-A030\x00\x00',
      b'39990-T6Z-A050\x00\x00',
      b'39990-T6Z-A110\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T6Z-A020\x00\x00',
      b'36161-T6Z-A310\x00\x00',
      b'36161-T6Z-A420\x00\x00',
      b'36161-T6Z-A520\x00\x00',
      b'36161-T6Z-A620\x00\x00',
      b'36161-T6Z-A720\x00\x00',
      b'36161-TJZ-A120\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-T6Z-A010\x00\x00',
      b'38897-T6Z-A110\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T6Z-A020\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-T6Z-A120\x00\x00',
      b'57114-T6Z-A130\x00\x00',
      b'57114-T6Z-A520\x00\x00',
      b'57114-T6Z-A610\x00\x00',
      b'57114-TJZ-A520\x00\x00',
    ],
  },
  CAR.HONDA_INSIGHT: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TXM-A040\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TXM-A070\x00\x00',
      b'36802-TXM-A080\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TXM-A050\x00\x00',
      b'36161-TXM-A060\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TXM-A230\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TXM-A030\x00\x00',
      b'57114-TXM-A040\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TWA-A910\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TXM-A020\x00\x00',
    ],
  },
  CAR.HONDA_HRV: {
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-T7A-A010\x00\x00',
      b'38897-T7A-A110\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-THX-A020\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T7A-A040\x00\x00',
      b'36161-T7A-A140\x00\x00',
      b'36161-T7A-A240\x00\x00',
      b'36161-T7A-C440\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T7A-A230\x00\x00',
    ],
  },
  CAR.HONDA_HRV_3G: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-3M0-G110\x00\x00',
      b'39990-3W0-A030\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-3M0-M110\x00\x00',
      b'38897-3W1-A010\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-3M0-K840\x00\x00',
      b'77959-3V0-A820\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'8S102-3M6-P030\x00\x00',
      b'8S102-3W0-A060\x00\x00',
      b'8S102-3W0-AB10\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-3M6-M010\x00\x00',
      b'57114-3W0-A040\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-6EH-A010\x00\x00',
      b'28101-6JC-M310\x00\x00',
    ],
    (Ecu.electricBrakeBooster, 0x18da2bf1, None): [
      b'46114-3W0-A020\x00\x00',
    ],
  },
  CAR.ACURA_ILX: {
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TX6-A010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TV9-A140\x00\x00',
      b'36161-TX6-A030\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TX6-A230\x00\x00',
      b'77959-TX6-C210\x00\x00',
    ],
  },
  CAR.HONDA_E: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TYF-N030\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TYF-E140\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TYF-E010\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TYF-G430\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36802-TYF-E030\x00\x00',
    ],
    (Ecu.fwdCamera, 0x18dab5f1, None): [
      b'36161-TYF-E020\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TYF-E030\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC_2022: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-T24-T120\x00\x00',
      b'39990-T39-A130\x00\x00',
      b'39990-T43-J020\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-T20-A020\x00\x00',
      b'38897-T20-A210\x00\x00',
      b'38897-T20-A310\x00\x00',
      b'38897-T20-A510\x00\x00',
      b'38897-T21-A010\x00\x00',
      b'38897-T24-Z120\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-T20-A970\x00\x00',
      b'77959-T20-A980\x00\x00',
      b'77959-T20-M820\x00\x00',
      b'77959-T47-A940\x00\x00',
      b'77959-T47-A950\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-T20-A060\x00\x00',
      b'36161-T20-A070\x00\x00',
      b'36161-T20-A080\x00\x00',
      b'36161-T24-T070\x00\x00',
      b'36161-T47-A050\x00\x00',
      b'36161-T47-A070\x00\x00',
      b'8S102-T20-AA10\x00\x00',
      b'8S102-T47-AA10\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-T20-AB40\x00\x00',
      b'57114-T24-TB30\x00\x00',
      b'57114-T43-JB30\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-65D-A020\x00\x00',
      b'28101-65D-A120\x00\x00',
      b'28101-65H-A020\x00\x00',
      b'28101-65H-A120\x00\x00',
      b'28101-65J-N010\x00\x00',
    ],
  },
}
