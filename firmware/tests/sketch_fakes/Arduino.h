#pragma once
#include <stdint.h>
#include <stddef.h>
#include <deque>
#include <string>
#ifdef _MSC_VER
// A compile-time disabled LCD intentionally makes its service guard constant.
#pragma warning(disable:4127)
#endif
// Host integration model; AVR sections, electrical behavior and instruction
// timing are deliberately not emulated. The original sketch is included intact.
#define __attribute__(attributes)
#define F_CPU 16000000UL
#define OUTPUT 1
#define INPUT_PULLUP 2
#define LOW 0
#define HIGH 1
#define A1 19
#define A2 20
#define _BV(bit) (1U << (bit))
enum { COM1A1=7, WGM11=1, WGM13=4, WGM12=3, CS10=0, TOV1=0, TOIE1=0 };
extern uint8_t TCCR1A,TCCR1B,TIMSK1,TIFR1;
extern uint16_t TCNT1,ICR1,OCR1A;
uint32_t millis();
uint32_t micros();
void pinMode(uint8_t pin,int mode);
int digitalRead(uint8_t pin);
void digitalWrite(uint8_t pin,int value);
struct FakeSerial {
  std::deque<char> input;
  std::string output;
  bool connected=true, stalled=false;
  uint32_t baudRate=115200;
  void begin(uint32_t rate) { baudRate=rate; }
  uint32_t baud() const { return baudRate; }
  bool dtr() const { return connected; }
  int available() const { return static_cast<int>(input.size()); }
  int availableForWrite() const { return stalled ? 0 : 64; }
  char read() { char value=input.front(); input.pop_front(); return value; }
  size_t write(const uint8_t *bytes,size_t count) {
    output.append(reinterpret_cast<const char *>(bytes),count); return count;
  }
};
extern FakeSerial Serial;
