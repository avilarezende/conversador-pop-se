#pragma once

#include <Arduino.h>

#include "popse_client.h"

namespace ui {

void begin();
void show_boot(const char* chip_model);
void show_status(bool wifi_ok, const String& ip, int8_t rssi, const PopseHealth& health,
                 const String& last_message);
void tick();

}  // namespace ui
