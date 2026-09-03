#pragma once

#include <Arduino.h>

namespace wifi_mgr {

bool begin();
bool ensure_connected();
bool is_connected();
String ip_address();
int8_t rssi();

}  // namespace wifi_mgr
