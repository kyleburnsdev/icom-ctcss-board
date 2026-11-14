#pragma once
#include <stdint.h>
#ifndef _BV
#define _BV(bit) (1U << (bit))
#endif
#ifdef _MSC_VER
// AVR EEPROM addresses are 16-bit integers cast to pointers by the real source.
// The fake read routine converts the pointer back to an integer, never dereferences it.
#pragma warning(disable:4312)
#endif
enum { EEPM1=5, EEPM0=4, EEMPE=2, EEPE=1 };
extern uint16_t EEAR;
extern uint8_t EEDR,MCUSR;
void fakeLaunchEeprom();
struct FakeEecr {
  uint8_t value=0;
  operator uint8_t() const { return value; }
  FakeEecr &operator&=(unsigned mask) { value&=mask; return *this; }
  FakeEecr &operator|=(unsigned bits) {
    value|=bits;
    if (bits & (1U<<EEPE)) fakeLaunchEeprom();
    return *this;
  }
};
extern FakeEecr EECR;
