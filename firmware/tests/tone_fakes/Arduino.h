#pragma once
#include <stdint.h>
// Register model only: no claim about AVR interrupt timing or pin voltages.
#define F_CPU 16000000UL
#define OUTPUT 1
#define LOW 0
#define _BV(bit) (1U << (bit))
enum { COM1A1=7, WGM11=1, WGM13=4, WGM12=3, CS10=0, TOV1=0, TOIE1=0 };
extern uint8_t TCCR1A, TCCR1B, TIMSK1, TIFR1;
extern uint16_t TCNT1, ICR1, OCR1A;
extern uint8_t outputPin, lowPin;
inline void pinMode(uint8_t pin, int) { outputPin=pin; }
inline void digitalWrite(uint8_t pin, int value) { if (value==LOW) lowPin=pin; }
