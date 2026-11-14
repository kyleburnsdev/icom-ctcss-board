#pragma once
#include <stdint.h>

// Fixed PCB allocation. These are Arduino pin names, not socket pad numbers.
namespace Pins {
constexpr uint8_t encoderA = 4, encoderB = 5, button = 6, micPtt = 7;
constexpr uint8_t radioPtt = 8, tone = 9, bypass = 10;
}
// Identify the actual backpack before enabling the display. Common PCF8574
// wiring is configurable in display.cpp; 1602 alone does not establish it.
#ifndef CTCSS_LCD_ADDRESS
#define CTCSS_LCD_ADDRESS 0
#endif
// Grove LCD RGB Backlight V4: direct LCD at 0x3e, PCA9632 at 0x62.
// Default retains the PCF8574 backpack protocol.
#ifndef CTCSS_LCD_GROVE_V4
#define CTCSS_LCD_GROVE_V4 0
#endif
#if CTCSS_LCD_GROVE_V4 && CTCSS_LCD_ADDRESS != 0x3e
#error Grove V4 requires CTCSS_LCD_ADDRESS=0x3e
#endif
#ifndef CTCSS_BENCH
#define CTCSS_BENCH 0
#endif
constexpr int8_t encoderDirection = 1;
constexpr int8_t encoderTransitionsPerDetent = 4;
constexpr uint16_t inputQualificationMs = 5;
constexpr uint16_t buttonQualificationMs = 15;
constexpr uint16_t longPressMs = 750;
// Positive measured clock error (fast oscillator) needs a positive correction.
constexpr int32_t clockCorrectionPpm = 0;
constexpr uint16_t pwmTop = 1599;       // Timer1, 16 MHz / 1600 = 10 kHz
constexpr uint16_t pwmMidpoint = 800;
constexpr uint16_t tonePeakCounts = 600; // fixed amplitude: +/-37.5% duty
