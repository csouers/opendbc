#pragma once

#include "opendbc/safety/safety_declarations.h"
#include "opendbc/safety/modes/defaults.h"

#define CAN_GATEWAY_INPUT 0x800
#define CAN_GATEWAY_OUTPUT 0x801
#define CAN_GATEWAY_SIZE 8
#define OTA_IN 0x1

static bool elm327_tx_hook(const CANPacket_t *to_send) {
  const int GM_CAMERA_DIAG_ADDR = 0x24B;

  bool tx = true;
  int addr = GET_ADDR(to_send);
  int len = GET_LEN(to_send);

  // All ISO 15765-4 messages must be 8 bytes long
  // TODO: Replace this with the check functionality from safety_honda
  bool is_body = (addr == 0x16f118f0) || (addr == 0x0ef81218) || (addr == CAN_GATEWAY_INPUT);
  if (is_body) {
    if ((len != 8) && (addr == 0x16f118f0)){ // honda bcm diag request
      tx = false;
    }
    else if ((len != 2) && (addr == 0x0ef81218)){ // 2017 honda civic hatch keyfob replay
      tx = false;
    }
    // // not yet implemented
    // else if ((len != CAN_GATEWAY_SIZE) && (addr == CAN_GATEWAY_INPUT)){ // body harness heartbeat frame
    //   tx = false;
    // }
    else {
      tx = false; // we shouldn't end up here if we did things correctly
    }
   }
  // // allow OTA flashing
  // else if (addr == OTA_IN){
  //   tx = true;
  // }
  else {
    //All ISO 15765-4 messages must be 8 bytes long
    if (len != 8) {
      tx = false;
    }
  }

  // Check valid 29 bit send addresses for ISO 15765-4
  // Check valid 11 bit send addresses for ISO 15765-4
  if ((addr != 0x18DB33F1) && ((addr & 0x1FFF00FF) != 0x18DA00F1) &&
      ((addr & 0x1FFFFF00) != 0x600) && ((addr & 0x1FFFFF00) != 0x700) &&
      (addr != GM_CAMERA_DIAG_ADDR)) {
    tx = false;
  }

  // GM camera uses non-standard diagnostic address, this has no control message address collisions
  if ((addr == GM_CAMERA_DIAG_ADDR) && (len == 8)) {
    // Only allow known frame types for ISO 15765-2
    if ((GET_BYTE(to_send, 0) & 0xF0U) > 0x30U) {
      tx = false;
    }
  }
  return tx;
}

// If current_board->has_obd and safety_param == 0, bus 1 is multiplexed to the OBD-II port
const safety_hooks elm327_hooks = {
  .init = nooutput_init,
  .rx = default_rx_hook,
  .tx = elm327_tx_hook,
};
