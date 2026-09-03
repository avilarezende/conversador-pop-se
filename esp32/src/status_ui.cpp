#include "status_ui.h"

#include "config.h"

#if POPSE_HAS_DISPLAY
#include <TFT_eSPI.h>
#include <SPI.h>
#endif

namespace ui {
namespace {

String g_line_wifi;
String g_line_health;
String g_line_msg;
bool g_dirty = true;

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
    tft.drawString("PoP-SE / ESP32", 6, 8, 2);

    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawString(g_line_wifi, 6, 40, 2);
    tft.drawString(g_line_health, 6, 70, 2);

    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.setCursor(6, 110);
    tft.setTextFont(2);
    tft.setTextWrap(true);
    tft.print(g_line_msg);
#else
    Serial.println("---- status ----");
    Serial.println(g_line_wifi);
    Serial.println(g_line_health);
    Serial.println(g_line_msg);
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
#endif
    g_line_wifi = "WiFi: --";
    g_line_health = "Engine: --";
    g_line_msg = "Aguardando...";
    g_dirty = true;
}

void show_boot(const char* chip_model) {
    g_line_msg = String("Boot ") + chip_model;
    g_dirty = true;
    paint();
}

void show_status(bool wifi_ok, const String& ip, int8_t rssi, const PopseHealth& health,
                 const String& last_message) {
    if (wifi_ok) {
        g_line_wifi = "WiFi OK " + ip + " " + String(rssi) + "dBm";
    } else {
        g_line_wifi = "WiFi OFFLINE";
    }

    if (health.ok) {
        g_line_health = "Engine OK llm=" + health.llm_provider;
    } else if (health.error.length()) {
        g_line_health = "Engine ERR " + health.error;
    } else {
        g_line_health = "Engine ?";
    }

    if (last_message.length()) {
        g_line_msg = last_message.substring(0, 160);
    }

    g_dirty = true;
}

void tick() {
    if (g_dirty) {
        paint();
    }
}

}  // namespace ui
