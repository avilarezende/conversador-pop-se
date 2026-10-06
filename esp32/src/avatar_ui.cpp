#include "avatar_ui.h"

#include <TFT_eSPI.h>

#include "config.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

namespace ui {
namespace {

TFT_eSPI tft;

AvatarMood g_mood = AvatarMood::Offline;
String g_status = "Iniciando...";
String g_model = "grok";
String g_ip = "-";
bool g_wifi = false;
String g_bubble;
String g_input;
uint32_t last_anim_ms = 0;
uint8_t blink_phase = 0;
uint8_t speak_phase = 0;
uint8_t think_dots = 0;
bool eye_closed = false;

constexpr int16_t AVATAR_CX = 56;
constexpr int16_t AVATAR_CY = 110;
constexpr int16_t BUBBLE_X = 110;
constexpr int16_t BUBBLE_Y = 28;
constexpr int16_t BUBBLE_W = 200;
constexpr int16_t BUBBLE_H = 130;

struct Chip {
    int16_t x, y, w, h;
    HitTarget id;
    const char* label;
};

const Chip CHIPS[] = {
    {8, 198, 70, 28, HitTarget::ChipHello, "Ola"},
    {82, 198, 70, 28, HitTarget::ChipJoke, "Piada"},
    {156, 198, 56, 28, HitTarget::ChipWho, "Quem?"},
    {216, 198, 50, 28, HitTarget::ChipHelp, "?"},
    {270, 198, 42, 28, HitTarget::Send, "OK"},
};

uint16_t bg_color() { return tft.color565(18, 42, 58); }
uint16_t panel_color() { return tft.color565(28, 64, 82); }
uint16_t accent() { return tft.color565(75, 179, 86); }
uint16_t beak() { return tft.color565(229, 57, 47); }
uint16_t soft() { return tft.color565(191, 233, 168); }
uint16_t text_col() { return tft.color565(240, 248, 244); }
uint16_t muted() { return tft.color565(140, 170, 180); }

void draw_wrapped(int16_t x, int16_t y, int16_t w, int16_t max_lines, const String& text) {
    tft.setTextColor(text_col(), panel_color());
    tft.setTextDatum(TL_DATUM);
    tft.setTextFont(2);
    const int line_h = 16;
    int line = 0;
    String remaining = text;
    while (remaining.length() && line < max_lines) {
        String chunk;
        int last_space = -1;
        for (int i = 0; i < static_cast<int>(remaining.length()); ++i) {
            chunk += remaining[i];
            if (remaining[i] == ' ') last_space = i;
            if (tft.textWidth(chunk) > w) {
                if (last_space > 0) {
                    chunk = remaining.substring(0, last_space);
                    remaining = remaining.substring(last_space + 1);
                } else {
                    chunk = remaining.substring(0, i);
                    remaining = remaining.substring(i);
                }
                break;
            }
            if (i == static_cast<int>(remaining.length()) - 1) {
                remaining = "";
            }
        }
        tft.drawString(chunk, x, y + line * line_h);
        ++line;
        if (remaining.length() && line == max_lines) {
            tft.drawString("...", x + w - 18, y + (line - 1) * line_h);
        }
    }
}

void draw_status_bar() {
    tft.fillRect(0, 0, 320, 24, panel_color());
    tft.setTextDatum(TL_DATUM);
    tft.setTextFont(2);
    tft.setTextColor(g_wifi ? accent() : beak(), panel_color());
    tft.drawString(g_wifi ? "WiFi" : "off", 6, 4);
    tft.setTextColor(muted(), panel_color());
    tft.drawString(g_ip, 42, 4);
    tft.setTextColor(text_col(), panel_color());
    tft.drawString(ASSISTANT_NAME, 130, 4);
    String model = g_model.length() ? g_model : "grok";
    if (model.length() > 10) model = model.substring(0, 10);
    tft.setTextColor(accent(), panel_color());
    tft.setTextDatum(TR_DATUM);
    tft.drawString(model, 314, 4);
}

void draw_avatar_body() {
    tft.fillRect(4, 28, 100, 160, bg_color());
    const uint16_t body = (g_mood == AvatarMood::Offline) ? muted() : accent();

    tft.fillCircle(AVATAR_CX, AVATAR_CY + 18, 34, body);
    tft.fillEllipse(AVATAR_CX, AVATAR_CY + 28, 22, 18, soft());
    tft.fillCircle(AVATAR_CX, AVATAR_CY - 18, 28, body);
    tft.fillEllipse(AVATAR_CX, AVATAR_CY - 8, 18, 12, soft());

    const int eye_y = AVATAR_CY - 22;
    if (eye_closed || g_mood == AvatarMood::Thinking) {
        tft.drawWideLine(AVATAR_CX - 12, eye_y, AVATAR_CX - 4, eye_y, 2, text_col(), bg_color());
        tft.drawWideLine(AVATAR_CX + 4, eye_y, AVATAR_CX + 12, eye_y, 2, text_col(), bg_color());
    } else {
        tft.fillCircle(AVATAR_CX - 10, eye_y, 7, TFT_WHITE);
        tft.fillCircle(AVATAR_CX + 10, eye_y, 7, TFT_WHITE);
        tft.fillCircle(AVATAR_CX - 10, eye_y + 1, 3, TFT_BLACK);
        tft.fillCircle(AVATAR_CX + 10, eye_y + 1, 3, TFT_BLACK);
    }

    int beak_open = 0;
    if (g_mood == AvatarMood::Speaking) beak_open = (speak_phase % 2) ? 6 : 2;
    if (g_mood == AvatarMood::Happy) beak_open = 3;
    tft.fillTriangle(AVATAR_CX - 8, AVATAR_CY - 8, AVATAR_CX + 8, AVATAR_CY - 8, AVATAR_CX,
                     AVATAR_CY + 2 + beak_open, beak());

    if (g_mood == AvatarMood::Thinking) {
        for (int i = 0; i < 3; ++i) {
            uint16_t c = (i <= think_dots) ? text_col() : muted();
            tft.fillCircle(AVATAR_CX - 10 + i * 10, AVATAR_CY + 58, 3, c);
        }
    }

    tft.setTextDatum(TC_DATUM);
    tft.setTextFont(2);
    tft.setTextColor(muted(), bg_color());
    tft.drawString(ASSISTANT_NAME, AVATAR_CX, 168);
}

void draw_bubble() {
    tft.fillRoundRect(BUBBLE_X, BUBBLE_Y, BUBBLE_W, BUBBLE_H, 10, panel_color());
    tft.drawRoundRect(BUBBLE_X, BUBBLE_Y, BUBBLE_W, BUBBLE_H, 10, accent());
    tft.fillTriangle(BUBBLE_X, BUBBLE_Y + 40, BUBBLE_X - 8, BUBBLE_Y + 48, BUBBLE_X, BUBBLE_Y + 56,
                     panel_color());
    draw_wrapped(BUBBLE_X + 8, BUBBLE_Y + 8, BUBBLE_W - 16, 7,
                 g_bubble.length() ? g_bubble : g_status);
}

void draw_chips() {
    tft.fillRect(0, 190, 320, 50, bg_color());
    for (const Chip& c : CHIPS) {
        tft.fillRoundRect(c.x, c.y, c.w, c.h, 8, panel_color());
        tft.drawRoundRect(c.x, c.y, c.w, c.h, 8, accent());
        tft.setTextDatum(MC_DATUM);
        tft.setTextFont(2);
        tft.setTextColor(text_col(), panel_color());
        tft.drawString(c.label, c.x + c.w / 2, c.y + c.h / 2);
    }
}

void draw_input_strip() {
    if (!g_input.length()) return;
    tft.fillRoundRect(BUBBLE_X, BUBBLE_Y + BUBBLE_H + 4, BUBBLE_W, 18, 4, panel_color());
    tft.setTextDatum(TL_DATUM);
    tft.setTextFont(1);
    tft.setTextColor(muted(), panel_color());
    String preview = g_input;
    if (preview.length() > 36) preview = preview.substring(preview.length() - 36);
    tft.drawString(preview, BUBBLE_X + 4, BUBBLE_Y + BUBBLE_H + 8);
}

}  // namespace

bool begin() {
    tft.init();
    tft.setRotation(CYD_ROTATION);
    tft.fillScreen(bg_color());
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, TFT_BACKLIGHT_ON);
    return true;
}

void show_boot(const char* chip) {
    g_status = String("Ola! Sou ") + ASSISTANT_NAME + ". Chip: " + chip;
    g_mood = AvatarMood::Happy;
    redraw();
}

void set_mood(AvatarMood mood) { g_mood = mood; }
AvatarMood mood() { return g_mood; }
void set_status_line(const String& text) { g_status = text; }
void set_model_label(const String& model) { g_model = model; }
void set_wifi(bool ok, const String& ip, int8_t /*rssi*/) {
    g_wifi = ok;
    g_ip = ip;
}
void set_bubble(const String& text) { g_bubble = text; }
void set_input_preview(const String& text) { g_input = text; }

void tick() {
    const uint32_t now = millis();
    if (now - last_anim_ms < 280) return;
    last_anim_ms = now;
    blink_phase = (blink_phase + 1) % 20;
    eye_closed = (blink_phase == 0 || blink_phase == 1);
    if (g_mood == AvatarMood::Speaking) speak_phase = (speak_phase + 1) % 4;
    if (g_mood == AvatarMood::Thinking) think_dots = (think_dots + 1) % 3;
    draw_avatar_body();
}

void redraw() {
    tft.fillScreen(bg_color());
    draw_status_bar();
    draw_avatar_body();
    draw_bubble();
    draw_input_strip();
    draw_chips();
}

HitTarget hit_test(int16_t x, int16_t y) {
    for (const Chip& c : CHIPS) {
        if (x >= c.x && x < c.x + c.w && y >= c.y && y < c.y + c.h) return c.id;
    }
    return HitTarget::None;
}

const char* chip_prompt(HitTarget t) {
    switch (t) {
        case HitTarget::ChipHello:
            return "Ola! Como voce esta hoje?";
        case HitTarget::ChipJoke:
            return "Me conte uma piada curta e leve.";
        case HitTarget::ChipWho:
            return "Quem e voce e o que consegue fazer neste display?";
        case HitTarget::ChipHelp:
            return "Como posso conversar com voce neste ESP32 CYD?";
        default:
            return "";
    }
}

AvatarMood mood_from_string(const String& s) {
    String m = s;
    m.toLowerCase();
    if (m == "listening") return AvatarMood::Listening;
    if (m == "thinking") return AvatarMood::Thinking;
    if (m == "speaking") return AvatarMood::Speaking;
    if (m == "happy") return AvatarMood::Happy;
    if (m == "concerned") return AvatarMood::Concerned;
    if (m == "offline") return AvatarMood::Offline;
    return AvatarMood::Idle;
}

}  // namespace ui
