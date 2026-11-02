#include "control.h"
#include "config.h"

namespace Ctcss {
const uint16_t presets[50] = {
  670,693,719,744,770,797,825,854,885,915,948,974,1000,1035,1072,
  1109,1148,1188,1230,1273,1318,1365,1413,1462,1514,1567,1598,1622,
  1655,1679,1713,1738,1773,1799,1835,1862,1899,1928,1966,1995,
  2035,2065,2107,2181,2257,2291,2336,2418,2503,2541
};
bool validTone(uint16_t tone) { return tone >= minimumTone && tone <= maximumTone; }
uint8_t nearestPreset(uint16_t tone) {
  uint8_t best = 0;
  uint16_t distance = 65535;
  for (uint8_t i = 0; i < 50; ++i) {
    uint16_t d = tone > presets[i] ? tone - presets[i] : presets[i] - tone;
    if (d < distance) { distance = d; best = i; }
  }
  return best;
}
void Control::inputs(bool micPressed, bool bypassOn, bool qualified) {
  bypass = bypassOn;
  if (!qualified) return;
  if (!armed) { if (!micPressed) armed = true; return; }
  if (micPressed && !transmitting) latched = saved;
  transmitting = micPressed;
}
bool Control::commit(uint16_t tone) {
  if (!validTone(tone)) return false;
  saved = tone;
  return true;
}
void Debouncer::begin(bool value, uint32_t now) {
  stable = candidate = value; since = now; qualified = false;
}
void Debouncer::update(bool value, uint32_t now, uint16_t interval) {
  if (value != candidate) { candidate = value; since = now; }
  if (uint32_t(now - since) >= interval) { stable = candidate; qualified = true; }
}
Gesture Button::update(bool pressed, uint32_t now) {
  if (pressed && !down) { pressedAt = now; longSent = false; }
  Gesture result = Gesture::None;
  if (pressed && !longSent && uint32_t(now - pressedAt) >= longPressMs) {
    longSent = true; result = Gesture::Long;
  }
  if (!pressed && down && !longSent) result = Gesture::Short;
  down = pressed;
  return result;
}
void Button::suppress(bool pressed, uint32_t now) {
  down = pressed; longSent = true; pressedAt = now;
}
int8_t Encoder::update(uint8_t ab) {
  // Gray-code sequence 11,01,00,10,11 is positive; diagonals reset partial motion.
  static const int8_t steps[16] = {0,-1,1,0, 1,0,0,-1, -1,0,0,1, 0,1,-1,0};
  if ((previous ^ ab) == 3) transitions = 0;
  else transitions += steps[(previous << 2) | ab];
  previous = ab;
  if (transitions >= encoderTransitionsPerDetent) { transitions = 0; return encoderDirection; }
  if (transitions <= -encoderTransitionsPerDetent) { transitions = 0; return -encoderDirection; }
  return 0;
}
static uint8_t wrap(int16_t value, uint8_t count) { return (value + count) % count; }
void Ui::rotate(int8_t delta) {
  rangeError = false;
  if (screen == Screen::Menu) menu = wrap(menu + delta, 3);
  if (screen == Screen::Presets) preset = wrap(preset + delta, 50);
  if (screen == Screen::Manual && digit < 4) {
    const uint16_t place[4] = {1000,100,10,1};
    uint8_t oldDigit = (edit / place[digit]) % 10;
    edit = edit - oldDigit * place[digit] + wrap(oldDigit + delta, 10) * place[digit];
  }
}
uint16_t Ui::gesture(Gesture event, uint16_t savedTone) {
  if (event == Gesture::None) return 0;
  switch (screen) {
    case Screen::Home:
      if (event == Gesture::Short) screen = Screen::Menu;
      break;
    case Screen::Menu:
      if (event == Gesture::Short) {
        if (menu == 0) { preset = nearestPreset(savedTone); screen = Screen::Presets; }
        if (menu == 1) { edit = savedTone; digit = 0; rangeError = false; screen = Screen::Manual; }
        if (menu == 2) screen = Screen::Home;
      }
      break;
    case Screen::Presets:
      if (event == Gesture::Long) screen = Screen::Menu;
      else return presets[preset];
      break;
    case Screen::Manual:
      if (event == Gesture::Short) { digit = (digit + 1) % 5; rangeError = false; }
      else if (digit == 4) screen = Screen::Menu;
      else if (validTone(edit)) return edit;
      else rangeError = true;
      break;
  }
  return 0;
}
}
