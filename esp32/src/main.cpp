#include <Arduino.h>

#include "config.h"
#include "popse_client.h"
#include "status_ui.h"
#include "wifi_manager.h"

static uint32_t last_blink_ms = 0;
static uint32_t last_poll_ms = 0;
static bool led_on = false;
static bool ever_connected = false;
static String last_ui_message = "Aguardando Wi-Fi...";

#if defined(BOARD_HAS_BOOT_BTN)
static const int BOOT_BTN = 0;
#endif
#if defined(BOARD_HAS_KEY_BTN)
static const int KEY_BTN = 14;
#endif

static void refresh_ui(const PopseHealth& health) {
    ui::show_status(wifi_mgr::is_connected(), wifi_mgr::ip_address(), wifi_mgr::rssi(), health,
                    last_ui_message);
}

static void poll_health(bool force_message) {
    const PopseHealth health = popse::fetch_health();
    if (health.ok) {
        if (force_message || last_ui_message == "Aguardando Wi-Fi...") {
            last_ui_message = "health ok";
        }
    } else if (health.error.length()) {
        last_ui_message = health.error;
    }
    refresh_ui(health);
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(200);

#if LED_GPIO >= 0
    pinMode(LED_GPIO, OUTPUT);
    digitalWrite(LED_GPIO, LOW);
#endif

#if defined(BOARD_HAS_BOOT_BTN)
    pinMode(BOOT_BTN, INPUT_PULLUP);
#endif
#if defined(BOARD_HAS_KEY_BTN)
    pinMode(KEY_BTN, INPUT_PULLUP);
#endif

    Serial.println();
    Serial.println("ESP32 — PoP-SE companion");
    Serial.printf("Chip: %s  rev %d\n", ESP.getChipModel(), ESP.getChipRevision());
    Serial.printf("CPU: %u MHz  Flash: %u MB\n",
                  ESP.getCpuFreqMHz(),
                  ESP.getFlashChipSize() / (1024 * 1024));
    Serial.printf("LED GPIO: %d  display=%d wifi_state=%s\n", LED_GPIO, POPSE_HAS_DISPLAY,
                  wifi_mgr::state_label());

    ui::begin();
    ui::show_boot(ESP.getChipModel());

    wifi_mgr::begin();
    popse::begin();
    refresh_ui(popse::last_health());
    last_poll_ms = 0;  // poll ASAP after first Wi-Fi connect
}

void loop() {
    const uint32_t now = millis();
    const bool wifi_ok = wifi_mgr::ensure_connected();

#if LED_GPIO >= 0
    if (now - last_blink_ms >= BLINK_INTERVAL_MS) {
        last_blink_ms = now;
        led_on = !led_on;
        digitalWrite(LED_GPIO, led_on ? HIGH : LOW);
    }
#endif

    if (wifi_mgr::connection_changed()) {
        if (wifi_ok) {
            ever_connected = true;
            last_ui_message = "Wi-Fi conectado";
            poll_health(true);
            last_poll_ms = now;
        } else {
            last_ui_message = "Wi-Fi perdido";
            refresh_ui(popse::last_health());
        }
    }

    if (wifi_ok && (last_poll_ms == 0 || now - last_poll_ms >= POPSE_POLL_INTERVAL_MS)) {
        last_poll_ms = now;
        poll_health(false);
    } else if (!wifi_ok && !ever_connected && (now - last_poll_ms >= 2000)) {
        last_poll_ms = now;
        last_ui_message = String("Wi-Fi ") + wifi_mgr::state_label();
        refresh_ui(popse::last_health());
    }

#if defined(BOARD_HAS_KEY_BTN)
    static bool prev_key = false;
    const bool key_pressed = digitalRead(KEY_BTN) == LOW;
    if (key_pressed && !prev_key) {
        Serial.println("[ui] KEY: refresh /health");
        if (wifi_mgr::is_connected()) {
            poll_health(true);
            last_poll_ms = now;
        } else {
            last_ui_message = "Wi-Fi offline";
            refresh_ui(popse::last_health());
        }
    }
    prev_key = key_pressed;
#endif

#if defined(BOARD_HAS_BOOT_BTN)
    static bool prev_boot = false;
    const bool boot_pressed = digitalRead(BOOT_BTN) == LOW;
    if (boot_pressed && !prev_boot) {
        Serial.println("[ui] BOOT: consultar PoP-SE chat");
        if (!wifi_mgr::is_connected()) {
            last_ui_message = "Wi-Fi offline";
            refresh_ui(popse::last_health());
        } else {
            const PopseChatReply reply =
                popse::ask("Qual o status geral dos links monitorados agora?");
            if (reply.ok) {
                last_ui_message = reply.reply;
            } else {
                last_ui_message = "chat: " + reply.error;
            }
            refresh_ui(popse::last_health());
        }
    }
    prev_boot = boot_pressed;
#endif

    ui::tick();
    delay(20);
}
