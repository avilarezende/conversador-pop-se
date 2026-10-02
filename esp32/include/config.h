#pragma once

#ifndef LED_GPIO
#define LED_GPIO 4
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

#ifndef GROK_HTTP_TIMEOUT_MS
#define GROK_HTTP_TIMEOUT_MS 60000
#endif

#ifndef HAS_DISPLAY
#define HAS_DISPLAY 1
#endif

#ifndef HAS_TOUCH
#define HAS_TOUCH 1
#endif

#ifndef CYD_ROTATION
#define CYD_ROTATION 1
#endif

#ifndef CYD_TOUCH_CLK
#define CYD_TOUCH_CLK 25
#endif
#ifndef CYD_TOUCH_MOSI
#define CYD_TOUCH_MOSI 32
#endif
#ifndef CYD_TOUCH_MISO
#define CYD_TOUCH_MISO 39
#endif
#ifndef CYD_TOUCH_CS
#define CYD_TOUCH_CS 33
#endif
#ifndef CYD_TOUCH_IRQ
#define CYD_TOUCH_IRQ 36
#endif

#ifndef TOUCH_MAP_X1
#define TOUCH_MAP_X1 200
#endif
#ifndef TOUCH_MAP_X2
#define TOUCH_MAP_X2 3700
#endif
#ifndef TOUCH_MAP_Y1
#define TOUCH_MAP_Y1 240
#endif
#ifndef TOUCH_MAP_Y2
#define TOUCH_MAP_Y2 3800
#endif
