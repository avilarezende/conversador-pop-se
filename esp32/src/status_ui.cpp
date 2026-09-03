#include "status_ui.h"

#include "config.h"

#if POPSE_HAS_DISPLAY
#include <SPI.h>
#include <TFT_eSPI.h>
#endif

namespace ui {
namespace {

String g_line_wifi;
String g_line_health;
String g_line_msg;
String g_line_hint;
bool g_dirty = true;
bool g_health_ok = false;
bool g_wifi_ok = false;

#if POPSE_HAS_DISPLAY
TFT_eSPI tft;
#ifndef PIN_POWER_ON
#define PIN_POWER_ON 15
#endif
#endif

void paint() {
#if POPSE_HAS_DISPLAY
    tft.fillScreen(TFT_BLACK);
    tft.setTextDatum(TL_DATUM);
    tft.setTextColor(TFT_CYAN, TFT_BLACK);
    tft.drawString("PoP-SE companion", 6, 6, 2);

    tft.setTextColor(g_wifi_ok ? TFT_GREEN : TFT_ORANGE, TFT_BLACK);
    tft.drawString(g_line_wifi, 6, 36, 2);

    tft.setTextColor(g_health_ok ? TFT_GREEN : TFT_RED, TFT_BLACK);
    tft.drawString(g_line_health, 6, 64, 2);

    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.setCursor(6, 100);
    tft.setTextFont(2);
    tft.setTextWrap(true);
    tft.print(g_line_msg);

    tft.setTextColor(TFT_DARKGREY, TFT_BLACK);
    tft.drawString(g_line_hint, 6, 150, 2);
#else
    Serial.println("---- status ----");
    Serial.println(g_line_wifi);
    Serial.println(g_line_health);
    Serial.println(g_line_msg);
    Serial.println(g_line_hint);
    Serial.println("----------------");
#endif
    g_dirty = false;
}

}  // namespace

void begin() {
#if POPSE_HAS_DISPLAY
    pinMode(PIN_POWER_ON, OUTPUT);
    digitalWrite(PIN_POWER_ON, HIGH);
    delay(50);
    tft.init();
    tft.setRotation(1);
    tft.fillScreen(TFT_BLACK);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("Iniciando...", 6, 8, 2);
    g_line_hint = "BOOT=chat  KEY=health";
#else
    g_line_hint = "Serial UI (sem display)";
#endif
    g_line_wifi = "WiFi: --";
    g_line_health = "Engine: --";
    g_line_msg = "Aguardando Wi-Fi...";
    g_dirty = true;
}

void show_boot(const char* chip_model) {
    g_line_msg = String("Boot ") + chip_model;
    g_dirty = true;
    paint();
}

void show_status(bool wifi_ok, const String& ip, int8_t rssi, const PopseHealth& health,
                 const String& last_message) {
    g_wifi_ok = wifi_ok;
    g_health_ok = health.ok;

    if (wifi_ok) {
        g_line_wifi = "WiFi " + ip + " " + String(rssi) + "dBm";
    } else {
        g_line_wifi = "WiFi offline";
    }

    if (health.ok) {
        g_line_health = "Engine OK (" + health.llm_provider + ")";
    } else if (health.error.length()) {
        g_line_health = "Engine " + health.error;
    } else if (!wifi_ok) {
        g_line_health = "Engine aguardando Wi-Fi";
    } else {
        g_line_health = "Engine ?";
    }

    if (last_message.length()) {
        g_line_msg = last_message.substring(0, 180);
    }

    g_dirty = true;
}

void tick() {
    if (g_dirty) {
        paint();
    }
}

}  // namespace ui
