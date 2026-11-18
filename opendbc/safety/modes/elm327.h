#ifndef SAFETY_MODES_ELM327_H
#define SAFETY_MODES_ELM327_H

#include "opendbc/safety/declarations.h"
#include "opendbc/safety/modes/defaults.h"

#define CAN_GATEWAY_INPUT 0x800U
#define CAN_GATEWAY_OUTPUT 0x801U
#define CAN_GATEWAY_SIZE 8
#define OTA_IN 0x1U

static bool elm327_tx_hook(const CANPacket_t *msg) {
  const unsigned int GM_CAMERA_DIAG_ADDR = 0x24BU;

  bool tx = true;
  uint32_t len = GET_LEN(msg);

  // All ISO 15765-4 messages must be 8 bytes long
  // TODO: Replace this with the check functionality from safety_honda
  bool is_body = (msg->addr == 0x16f118f0U) || (msg->addr == 0x0ef81218U) || (msg->addr == CAN_GATEWAY_INPUT);
  if (is_body) {
    if ((len != 8U) && (msg->addr == 0x16f118f0U)){ // honda bcm diag request
      tx = false;
    }
    else if ((len != 2U) && (msg->addr == 0x0ef81218U)){ // 2017 honda civic hatch keyfob replay
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
    if (len != 8U) {
      tx = false;
    }
  }

  // Check valid 29 bit send addresses for ISO 15765-4
  // Check valid 11 bit send addresses for ISO 15765-4
  if ((msg->addr != 0x18DB33F1U) && ((msg->addr & 0x1FFF00FFU) != 0x18DA00F1U) &&
      ((msg->addr & 0x1FFFFF00U) != 0x600U) && ((msg->addr & 0x1FFFFF00U) != 0x700U) &&
      (msg->addr != GM_CAMERA_DIAG_ADDR)) {
    tx = false;
  }

  // GM camera uses non-standard diagnostic address, this has no control message address collisions
  if ((msg->addr == GM_CAMERA_DIAG_ADDR) && (len == 8U)) {
    // Only allow known frame types for ISO 15765-2
    if ((msg->data[0] & 0xF0U) > 0x30U) {
      tx = false;
    }
  }

  return tx;
}

// If safety_param == 0, bus 1 is multiplexed to the OBD-II port
static const safety_hooks elm327_hooks = {
  .init = nooutput_init,
  .tx = elm327_tx_hook,
};

#endif  // SAFETY_MODES_ELM327_H
