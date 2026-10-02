#pragma once

#include <Arduino.h>

namespace wifi_mgr {

bool begin();
bool ensure_connected();
bool is_connected();
bool connection_changed();  // true once after up/down transition; clears flag
String ip_address();
int8_t rssi();
const char* state_label();

}  // namespace wifi_mgr
