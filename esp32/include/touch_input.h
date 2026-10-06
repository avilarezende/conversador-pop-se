#pragma once

#include <Arduino.h>

namespace touch {

bool begin();
bool read(int16_t& x, int16_t& y);
bool was_pressed();

}  // namespace touch
