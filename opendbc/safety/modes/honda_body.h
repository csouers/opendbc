#pragma once

// Honda body-harness mode (SAFETY_HONDA_BODY = 100).
//
// The aapi companion box runs this on the body bus: bus 0 is the powertrain side,
// bus 1 is the body side. It forwards all body traffic to powertrain, and a small
// allowlist of powertrain messages to body (security, IOC tester, wakeup, and the
// private OPNAV nav family from openpilot).
//
// TX is unrestricted, matching the original hondabody firmware's tx hook.

static void honda_body_rx_hook(const CANPacket_t *msg) {
  SAFETY_UNUSED(msg);
}

static bool honda_body_tx_hook(const CANPacket_t *msg) {
  SAFETY_UNUSED(msg);
  return true;
}

static safety_config honda_body_init(uint16_t param) {
  SAFETY_UNUSED(param);
  controls_allowed = false;
  // forwarding is the point of this mode
  return (safety_config){NULL, 0, NULL, 0, false};  // NOLINT(readability/braces)
}

static bool honda_body_fwd_hook(int bus_num, int addr) {
  bool block = true;
  if (bus_num == 0) {
    const bool security = (addr == 0xef81218);
    const bool ioc = (addr == 0x16f118f0);
    const bool wakeup = (addr == 0x1e12ff18);
    const bool opnav = (addr == 0x1A5A0001) || (addr == 0x1A5A0002) || (addr == 0x1A5A0003);
    block = !(security || ioc || wakeup || opnav);
  } else if (bus_num == 1) {
    block = false;
  }
  return block;
}

const safety_hooks honda_body_hooks = {
  .init = honda_body_init,
  .rx = honda_body_rx_hook,
  .tx = honda_body_tx_hook,
  .fwd = honda_body_fwd_hook,
};

// Test variant: same as body but no forwarding.
static bool honda_body_test_fwd_hook(int bus_num, int addr) {
  SAFETY_UNUSED(bus_num);
  SAFETY_UNUSED(addr);
  return true;
}

static safety_config honda_body_test_init(uint16_t param) {
  safety_config ret = honda_body_init(param);
  ret.disable_forwarding = true;
  return ret;
}

const safety_hooks honda_body_test_hooks = {
  .init = honda_body_test_init,
  .rx = honda_body_rx_hook,
  .tx = honda_body_tx_hook,
  .fwd = honda_body_test_fwd_hook,
};
