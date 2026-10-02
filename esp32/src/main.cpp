#include <Arduino.h>

#include "avatar_ui.h"
#include "config.h"
#include "grok_client.h"
#include "touch_input.h"
#include "wifi_manager.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

static String serial_buf;
static bool ever_connected = false;

#if defined(BOARD_HAS_BOOT_BTN)
static const int BOOT_BTN = 0;
static bool boot_was_down = false;
#endif

static void refresh_connectivity_ui() {
    ui::set_wifi(wifi_mgr::is_connected(), wifi_mgr::ip_address(), wifi_mgr::rssi());
    ui::set_model_label(GROK_MODEL);
    if (!wifi_mgr::is_connected()) {
        ui::set_mood(AvatarMood::Offline);
        ui::set_status_line("Aguardando Wi-Fi...");
    } else if (!grok::configured()) {
        ui::set_mood(AvatarMood::Concerned);
        ui::set_status_line("Defina GROK_API_KEY em secrets.h");
    } else if (ui::mood() == AvatarMood::Offline || ui::mood() == AvatarMood::Concerned) {
        ui::set_mood(AvatarMood::Idle);
        ui::set_status_line(String("Pronto · ") + ASSISTANT_NAME + " + Grok");
    }
}

static void ask_bot(const String& message) {
    if (!message.length()) return;
    if (!wifi_mgr::is_connected()) {
        ui::set_mood(AvatarMood::Offline);
        ui::set_bubble("Sem Wi-Fi. Conecte a rede e tente de novo.");
        ui::redraw();
        return;
    }
    if (!grok::configured()) {
        ui::set_mood(AvatarMood::Concerned);
        ui::set_bubble("Falta GROK_API_KEY em include/secrets.h");
        ui::redraw();
        return;
    }

    Serial.printf("[cyd] ask: %s\n", message.c_str());
    ui::set_mood(AvatarMood::Listening);
    ui::set_bubble(String("> ") + message);
    ui::redraw();
    delay(180);

    ui::set_mood(AvatarMood::Thinking);
    ui::set_status_line("Falando com o Grok...");
    ui::redraw();

    const GrokReply reply = grok::ask(message);
    if (reply.ok) {
        ui::set_mood(ui::mood_from_string(reply.mood));
        if (ui::mood() == AvatarMood::Idle) ui::set_mood(AvatarMood::Speaking);
        ui::set_bubble(reply.reply);
        ui::set_status_line("Toque num atalho ou digite no Serial");
    } else {
        ui::set_mood(AvatarMood::Concerned);
        ui::set_bubble(String("Falha: ") + (reply.error.length() ? reply.error : "erro"));
    }
    ui::redraw();
}

static void handle_hit(ui::HitTarget t) {
    if (t == ui::HitTarget::None) return;
    if (t == ui::HitTarget::Send) {
        if (serial_buf.length()) {
            String msg = serial_buf;
            serial_buf = "";
            ui::set_input_preview("");
            ask_bot(msg);
        }
        return;
    }
    const char* prompt = ui::chip_prompt(t);
    if (prompt && prompt[0]) ask_bot(String(prompt));
}

static void handle_serial() {
    while (Serial.available()) {
        const char c = static_cast<char>(Serial.read());
        if (c == '\r') continue;
        if (c == '\n') {
            if (serial_buf.length()) {
                String msg = serial_buf;
                serial_buf = "";
                ui::set_input_preview("");
                ask_bot(msg);
            }
            return;
        }
        if (c == 0x08 || c == 0x7f) {
            if (serial_buf.length()) serial_buf.remove(serial_buf.length() - 1);
        } else if (serial_buf.length() < 240) {
            serial_buf += c;
        }
        ui::set_input_preview(serial_buf);
        ui::redraw();
    }
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

    Serial.println();
    Serial.println("ESP32-CYD — Calisto + Grok (standalone)");
    Serial.printf("Chip: %s\n", ESP.getChipModel());
    Serial.println("Digite no Serial + Enter, ou use os chips na tela.");

    ui::begin();
    touch::begin();
    ui::show_boot(ESP.getChipModel());

    wifi_mgr::begin();
    grok::begin();
    refresh_connectivity_ui();
    ui::redraw();
}

void loop() {
    const bool wifi_ok = wifi_mgr::ensure_connected();
    if (wifi_ok && !ever_connected) {
        ever_connected = true;
        refresh_connectivity_ui();
        ui::set_bubble(String("Oi! Sou ") + ASSISTANT_NAME +
                       ". Toque em Ola ou me diga algo pelo Serial.");
        ui::set_mood(AvatarMood::Happy);
        ui::redraw();
    }
    if (wifi_mgr::connection_changed()) {
        refresh_connectivity_ui();
        ui::redraw();
    }

    int16_t tx = 0, ty = 0;
    touch::read(tx, ty);
    if (touch::was_pressed()) handle_hit(ui::hit_test(tx, ty));

#if defined(BOARD_HAS_BOOT_BTN)
    const bool boot_down = digitalRead(BOOT_BTN) == LOW;
    if (boot_down && !boot_was_down) ask_bot("Ola! Como voce esta hoje?");
    boot_was_down = boot_down;
#endif

    handle_serial();
    ui::tick();
    delay(15);
}
