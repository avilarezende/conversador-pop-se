#pragma once

// GPIO do LED onboard (GPIO 2 na maioria dos DevKit).
// Use -1 para desabilitar (ex.: LilyGo T-Display-S3, onde GPIO 38 é backlight).
#ifndef LED_GPIO
#define LED_GPIO 2
#endif

#ifndef SERIAL_BAUD
#define SERIAL_BAUD 115200
#endif

#ifndef BLINK_INTERVAL_MS
#define BLINK_INTERVAL_MS 500
#endif

#ifndef WIFI_CONNECT_TIMEOUT_MS
#define WIFI_CONNECT_TIMEOUT_MS 20000
#endif

#ifndef WIFI_RECONNECT_INTERVAL_MS
#define WIFI_RECONNECT_INTERVAL_MS 10000
#endif

#ifndef POPSE_POLL_INTERVAL_MS
#define POPSE_POLL_INTERVAL_MS 30000
#endif

#ifndef POPSE_HTTP_TIMEOUT_MS
#define POPSE_HTTP_TIMEOUT_MS 8000
#endif

// 1 = cliente HTTP do Conversador PoP-SE ativo
#ifndef POPSE_ENABLED
#define POPSE_ENABLED 1
#endif

// 1 = UI gráfica (LilyGo T-Display-S3)
#ifndef POPSE_HAS_DISPLAY
#define POPSE_HAS_DISPLAY 0
#endif
