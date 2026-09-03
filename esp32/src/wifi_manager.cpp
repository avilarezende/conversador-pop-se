#include "wifi_manager.h"

#include <WiFi.h>

#include "config.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

namespace wifi_mgr {
namespace {

uint32_t last_attempt_ms = 0;
bool started = false;

bool try_connect() {
    if (WiFi.status() == WL_CONNECTED) {
        return true;
    }

    Serial.printf("[wifi] Conectando a \"%s\"...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    const uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED &&
           (millis() - start) < WIFI_CONNECT_TIMEOUT_MS) {
        delay(250);
        Serial.print('.');
        yield();
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("[wifi] OK  IP=%s  RSSI=%d dBm\n",
                      WiFi.localIP().toString().c_str(), WiFi.RSSI());
        return true;
    }

    Serial.println("[wifi] Falha na conexão");
    WiFi.disconnect(true);
    return false;
}

}  // namespace

bool begin() {
    started = true;
    last_attempt_ms = millis();
    return try_connect();
}

bool ensure_connected() {
    if (!started) {
        return begin();
    }
    if (WiFi.status() == WL_CONNECTED) {
        return true;
    }

    const uint32_t now = millis();
    if (now - last_attempt_ms < WIFI_RECONNECT_INTERVAL_MS) {
        return false;
    }
    last_attempt_ms = now;
    Serial.println("[wifi] Reconectando...");
    return try_connect();
}

bool is_connected() {
    return WiFi.status() == WL_CONNECTED;
}

String ip_address() {
    if (!is_connected()) {
        return String("-");
    }
    return WiFi.localIP().toString();
}

int8_t rssi() {
    if (!is_connected()) {
        return 0;
    }
    return WiFi.RSSI();
}

}  // namespace wifi_mgr
