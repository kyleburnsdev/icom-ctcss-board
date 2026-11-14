#include "tone.h"
#include "config.h"
#include <Arduino.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/atomic.h>
#include "sine_table.h"
static_assert(tonePeakCounts==600,"Regenerate sine_table.h when changing amplitude");

static volatile uint32_t phaseIncrement=0;
static volatile bool modulation=false;
static uint32_t phase=0;
static uint8_t envelope=0;

// Timer1 alone owns OC1A / PB5 / Arduino D9. No analogWrite(), Servo or tone().
// Overflow -> bounded DDS update -> next buffered OCR1A duty. No I/O or division.
ISR(TIMER1_OVF_vect) {
  phase+=phaseIncrement;
  if (modulation) { if (envelope<50) ++envelope; }
  else if (envelope) --envelope;
  int16_t sample=static_cast<int16_t>(pgm_read_word(&sineTable[phase>>24]));
  OCR1A=pwmMidpoint+(int32_t(sample)*envelope)/50;
}
namespace Tone {
void begin() {
  static_assert(F_CPU==16000000UL,"Use the 5 V / 16 MHz Pro Micro profile");
  pinMode(Pins::tone,OUTPUT);
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    TCCR1A=0; TCCR1B=0; TIMSK1=0; TCNT1=0;
    ICR1=pwmTop; OCR1A=pwmMidpoint;
    TCCR1A=_BV(COM1A1)|_BV(WGM11);
    TCCR1B=_BV(WGM13)|_BV(WGM12)|_BV(CS10);
    TIFR1=_BV(TOV1); TIMSK1=_BV(TOIE1);
  }
}
void set(bool enabled,uint16_t tenthsHz) {
  static uint16_t lastTone=0;
  if (tenthsHz!=lastTone) {
    // Actual sample clock = nominal * (1 + ppm / 1e6).
    uint64_t denominator=uint64_t(100000)*(1000000L+clockCorrectionPpm);
    uint32_t increment=static_cast<uint32_t>((uint64_t(tenthsHz)*4294967296ULL*1000000ULL+denominator/2)/denominator);
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { phaseIncrement=increment; }
    lastTone=tenthsHz;
  }
  modulation=enabled;
}
bool healthy() {
  bool ok;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    ok=TCCR1A==(_BV(COM1A1)|_BV(WGM11)) &&
      TCCR1B==(_BV(WGM13)|_BV(WGM12)|_BV(CS10)) && ICR1==pwmTop &&
      TIMSK1==_BV(TOIE1);
  }
  return ok;
}
void stopFault() {
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    TIMSK1=0; TCCR1A=0; TCCR1B=0; modulation=false;
  }
  digitalWrite(Pins::tone,LOW);
}
}
