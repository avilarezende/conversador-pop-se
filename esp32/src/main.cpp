#include <Arduino.h>

#include "config.h"
#include "popse_client.h"
#include "status_ui.h"
#include "wifi_manager.h"

static uint32_t last_blink_ms = 0;
static uint32_t last_poll_ms = 0;
static bool led_on = false;
static String last_ui_message = "Pronto";

#if defined(BOARD_HAS_BOOT_BTN)
static const int BOOT_BTN = 0;
#endif

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

    Serial.println();
    Serial.println("ESP32 — PoP-SE companion");
    Serial.printf("Chip: %s  rev %d\n", ESP.getChipModel(), ESP.getChipRevision());
    Serial.printf("CPU: %u MHz  Flash: %u MB\n",
                  ESP.getCpuFreqMHz(),
                  ESP.getFlashChipSize() / (1024 * 1024));
    Serial.printf("LED GPIO: %d  display=%d\n", LED_GPIO, POPSE_HAS_DISPLAY);

    ui::begin();
    ui::show_boot(ESP.getChipModel());

    wifi_mgr::begin();
    popse::begin();

    const PopseHealth health = popse::fetch_health();
    ui::show_status(wifi_mgr::is_connected(), wifi_mgr::ip_address(), wifi_mgr::rssi(), health,
                    last_ui_message);
    last_poll_ms = millis();
}

void loop() {
    const uint32_t now = millis();

    wifi_mgr::ensure_connected();

#if LED_GPIO >= 0
    if (now - last_blink_ms >= BLINK_INTERVAL_MS) {
        last_blink_ms = now;
        led_on = !led_on;
        digitalWrite(LED_GPIO, led_on ? HIGH : LOW);
    }
#endif

    if (now - last_poll_ms >= POPSE_POLL_INTERVAL_MS) {
        last_poll_ms = now;
        const PopseHealth health = popse::fetch_health();
        if (health.ok) {
            last_ui_message = "health ok";
        } else if (health.error.length()) {
            last_ui_message = health.error;
        }
        ui::show_status(wifi_mgr::is_connected(), wifi_mgr::ip_address(), wifi_mgr::rssi(), health,
                        last_ui_message);
    }

#if defined(BOARD_HAS_BOOT_BTN)
    static bool prev_pressed = false;
    const bool pressed = digitalRead(BOOT_BTN) == LOW;
    if (pressed && !prev_pressed) {
        Serial.println("[ui] Botao: consultar PoP-SE");
        const PopseChatReply reply =
            popse::ask("Qual o status geral dos links monitorados agora?");
        if (reply.ok) {
            last_ui_message = reply.reply;
        } else {
            last_ui_message = "chat: " + reply.error;
        }
        ui::show_status(wifi_mgr::is_connected(), wifi_mgr::ip_address(), wifi_mgr::rssi(),
                        popse::last_health(), last_ui_message);
    }
    prev_pressed = pressed;
#endif

    ui::tick();
    delay(20);
}
