#pragma once

// GPIO do LED onboard (GPIO 2 na maioria dos DevKit; ajuste se necessário).
#ifndef LED_GPIO
#define LED_GPIO 2
#endif

#ifndef SERIAL_BAUD
#define SERIAL_BAUD 115200
#endif

#ifndef BLINK_INTERVAL_MS
#define BLINK_INTERVAL_MS 500
#endif
