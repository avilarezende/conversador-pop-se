#pragma once

#include <Arduino.h>

enum class AvatarMood : uint8_t {
    Idle,
    Listening,
    Thinking,
    Speaking,
    Happy,
    Concerned,
    Offline,
};

namespace ui {

bool begin();
void show_boot(const char* chip);
void set_mood(AvatarMood mood);
AvatarMood mood();
void set_status_line(const String& text);
void set_model_label(const String& model);
void set_wifi(bool ok, const String& ip, int8_t rssi);
void set_bubble(const String& text);
void set_input_preview(const String& text);
void tick();
void redraw();

enum class HitTarget : uint8_t {
    None,
    ChipHello,
    ChipJoke,
    ChipHelp,
    ChipWho,
    Send,
};

HitTarget hit_test(int16_t x, int16_t y);
const char* chip_prompt(HitTarget t);
AvatarMood mood_from_string(const String& s);

}  // namespace ui
