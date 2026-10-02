#include "touch_input.h"

#include <SPI.h>
#include <XPT2046_Touchscreen.h>

#include "config.h"

namespace touch {
namespace {

SPIClass touch_spi(VSPI);
XPT2046_Touchscreen ts(CYD_TOUCH_CS, CYD_TOUCH_IRQ);
bool was_down = false;
bool click_pending = false;

int16_t map_x(int16_t raw) {
#if CYD_ROTATION == 1
    return map(raw, TOUCH_MAP_X1, TOUCH_MAP_X2, 0, 320);
#else
    return map(raw, TOUCH_MAP_Y1, TOUCH_MAP_Y2, 0, 240);
#endif
}

int16_t map_y(int16_t raw) {
#if CYD_ROTATION == 1
    return map(raw, TOUCH_MAP_Y1, TOUCH_MAP_Y2, 0, 240);
#else
    return map(raw, TOUCH_MAP_X1, TOUCH_MAP_X2, 0, 320);
#endif
}

}  // namespace

bool begin() {
    touch_spi.begin(CYD_TOUCH_CLK, CYD_TOUCH_MISO, CYD_TOUCH_MOSI, CYD_TOUCH_CS);
    ts.begin(touch_spi);
    ts.setRotation(CYD_ROTATION);
    return true;
}

bool read(int16_t& x, int16_t& y) {
    if (!ts.tirqTouched() || !ts.touched()) {
        if (was_down) {
            click_pending = true;
            was_down = false;
        }
        return false;
    }
    TS_Point p = ts.getPoint();
    x = map_x(p.x);
    y = map_y(p.y);
    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (x > 319) x = 319;
    if (y > 239) y = 239;
    was_down = true;
    return true;
}

bool was_pressed() {
    if (!click_pending) return false;
    click_pending = false;
    return true;
}

}  // namespace touch
