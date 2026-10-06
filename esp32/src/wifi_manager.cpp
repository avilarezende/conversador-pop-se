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

enum class State : uint8_t { Idle, Connecting, Connected, Backoff };

State state = State::Idle;
uint32_t state_since_ms = 0;
uint32_t last_log_ms = 0;
bool changed_flag = false;
bool was_connected = false;

void mark_changed(bool connected_now) {
    if (connected_now != was_connected) {
        changed_flag = true;
        was_connected = connected_now;
    }
}

void start_connect(uint32_t now) {
    Serial.printf("[wifi] Conectando a \"%s\"...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    state = State::Connecting;
    state_since_ms = now;
    last_log_ms = now;
}

}  // namespace

bool begin() {
    start_connect(millis());
    return WiFi.status() == WL_CONNECTED;
}

bool ensure_connected() {
    const uint32_t now = millis();
    const wl_status_t st = WiFi.status();

    if (st == WL_CONNECTED) {
        if (state != State::Connected) {
            Serial.printf("[wifi] OK  IP=%s  RSSI=%d dBm\n",
                          WiFi.localIP().toString().c_str(), WiFi.RSSI());
            state = State::Connected;
            state_since_ms = now;
        }
        mark_changed(true);
        return true;
    }

    if (state == State::Connected) {
        Serial.println("[wifi] Conexão perdida");
        state = State::Backoff;
        state_since_ms = now;
        mark_changed(false);
        return false;
    }

    mark_changed(false);

    if (state == State::Idle) {
        start_connect(now);
        return false;
    }

    if (state == State::Connecting) {
        if (now - last_log_ms >= 1000) {
            Serial.print('.');
            last_log_ms = now;
        }
        if (now - state_since_ms >= WIFI_CONNECT_TIMEOUT_MS) {
            Serial.println();
            Serial.println("[wifi] Timeout — nova tentativa em breve");
            WiFi.disconnect(false);
            state = State::Backoff;
            state_since_ms = now;
        }
        return false;
    }

    if (now - state_since_ms >= WIFI_RECONNECT_INTERVAL_MS) {
        start_connect(now);
    }
    return false;
}

bool is_connected() {
    return WiFi.status() == WL_CONNECTED;
}

bool connection_changed() {
    if (!changed_flag) {
        return false;
    }
    changed_flag = false;
    return true;
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

const char* state_label() {
    switch (state) {
        case State::Connecting:
            return "conectando";
        case State::Connected:
            return "ok";
        case State::Backoff:
            return "retry";
        case State::Idle:
        default:
            return "idle";
    }
}

}  // namespace wifi_mgr
