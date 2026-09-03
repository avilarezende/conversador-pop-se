#include <Arduino.h>
#include "config.h"

static uint32_t last_toggle_ms = 0;
static bool led_on = false;

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(200);

    pinMode(LED_GPIO, OUTPUT);
    digitalWrite(LED_GPIO, LOW);

    Serial.println();
    Serial.println("ESP32 — firmware base");
    Serial.printf("Chip: %s  rev %d\n", ESP.getChipModel(), ESP.getChipRevision());
    Serial.printf("CPU: %u MHz  Flash: %u MB\n",
                  ESP.getCpuFreqMHz(),
                  ESP.getFlashChipSize() / (1024 * 1024));
    Serial.printf("LED GPIO: %d\n", LED_GPIO);
}

void loop() {
    const uint32_t now = millis();
    if (now - last_toggle_ms >= BLINK_INTERVAL_MS) {
        last_toggle_ms = now;
        led_on = !led_on;
        digitalWrite(LED_GPIO, led_on ? HIGH : LOW);
        Serial.printf("[%lu] LED %s\n", static_cast<unsigned long>(now), led_on ? "ON" : "OFF");
    }
}
