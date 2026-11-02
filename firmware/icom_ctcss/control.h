#pragma once
#include <stdint.h>

namespace Ctcss {
constexpr uint16_t defaultTone = 1514, minimumTone = 670, maximumTone = 2541;
extern const uint16_t presets[50];
bool validTone(uint16_t tone);
uint8_t nearestPreset(uint16_t tone);

// All application state belongs to loop(). No ISR accesses this object.
struct Control {
  uint16_t saved = defaultTone, latched = defaultTone;
  bool armed = false, transmitting = false, bypass = false;
  void inputs(bool micPressed, bool bypassOn, bool qualified);
  bool commit(uint16_t tone);
  bool toneEnabled() const { return transmitting && !bypass; }
  uint16_t activeTone() const { return transmitting ? latched : saved; }
};

struct Debouncer {
  bool stable = false, candidate = false, qualified = false;
  uint32_t since = 0;
  void begin(bool value, uint32_t now);
  void update(bool value, uint32_t now, uint16_t interval);
};

enum class Gesture : uint8_t { None, Short, Long };
struct Button {
  bool down = false, longSent = false;
  uint32_t pressedAt = 0;
  Gesture update(bool pressed, uint32_t now);
  void suppress(bool pressed, uint32_t now);
};

struct Encoder {
  uint8_t previous = 3;
  int8_t transitions = 0;
  int8_t update(uint8_t ab);
};

enum class Screen : uint8_t { Home, Menu, Presets, Manual };
struct Ui {
  Screen screen = Screen::Home;
  uint8_t menu = 0, preset = 0, digit = 0;
  uint16_t edit = defaultTone;
  bool rangeError = false;
  void rotate(int8_t delta);
  // Returns a requested save, or zero. Caller commits only after durable verify.
  uint16_t gesture(Gesture event, uint16_t saved);
  void saved() { screen = Screen::Menu; rangeError = false; }
  void unavailable() { screen = Screen::Home; rangeError = false; }
};
}
