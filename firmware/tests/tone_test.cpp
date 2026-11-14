#include "Arduino.h"
#include "tone.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

uint8_t TCCR1A=0, TCCR1B=0, TIMSK1=0, TIFR1=0;
uint16_t TCNT1=0, ICR1=0, OCR1A=0;
uint8_t outputPin=255, lowPin=255;
void TIMER1_OVF_vect();

static void tick(unsigned count) {
  while (count--) TIMER1_OVF_vect();
}

int main() {
  Tone::begin();
  assert(outputPin==9 && ICR1==1599 && OCR1A==800 && Tone::healthy());
  Tone::set(false,1514); tick(100);
  assert(OCR1A==800);
  double worst=0;
  // Execute the production ISR/set implementation, not a duplicate DDS formula.
  // Frequency oracle: elapsed nominal carrier time between positive crossings.
  for (uint16_t tone=670;tone<=2541;++tone) {
    Tone::set(true,tone); tick(100);
    unsigned first=0,last=0,crossings=0;
    uint16_t previous=OCR1A, minimum=1600, maximum=0;
    for (unsigned sample=0;sample<20000;++sample) {
      TIMER1_OVF_vect();
      uint16_t value=OCR1A;
      assert(value>=200 && value<=1400);
      if (value<minimum) minimum=value;
      if (value>maximum) maximum=value;
      if (previous<800 && value>=800) {
        if (!crossings) first=sample;
        last=sample; ++crossings;
      }
      previous=value;
    }
    assert(crossings>100 && minimum<=201 && maximum>=1399);
    double measured=double(crossings-1)*10000/(last-first);
    double error=fabs(measured-tone/10.0);
    assert(error<=.1);
    if (error>worst) worst=error;
    Tone::set(false,tone);
    tick(49); // Envelope must be fully gone by the fiftieth carrier service.
    TIMER1_OVF_vect(); assert(OCR1A==800);
    tick(100); assert(OCR1A==800);
  }
  // Check the selected linear 50-service attack at a nonzero waveform sample.
  Tone::set(true,1514);
  for (int service=1;service<=50;++service) {
    TIMER1_OVF_vect();
    int deviation=int(OCR1A)-800;
    assert(abs(deviation)<=12*service);
  }
  // Every owned configuration bit is monitored; OCR1A/TCNT1 are dynamic.
  for (unsigned bit=0;bit<8;++bit) {
    TCCR1A^=uint8_t(1U<<bit); assert(!Tone::healthy()); TCCR1A^=uint8_t(1U<<bit);
    TCCR1B^=uint8_t(1U<<bit); assert(!Tone::healthy()); TCCR1B^=uint8_t(1U<<bit);
    TIMSK1^=uint8_t(1U<<bit); assert(!Tone::healthy()); TIMSK1^=uint8_t(1U<<bit);
  }
  ICR1=1598; assert(!Tone::healthy()); ICR1=1599; assert(Tone::healthy());
  Tone::stopFault();
  assert(TIMSK1==0 && TCCR1A==0 && TCCR1B==0 && lowPin==9 && !Tone::healthy());
  printf("PASS actual tone.cpp: 1,872 manual tones, bounds, idle/ramp, timer guards, fault stop; worst nominal-clock error %.6f Hz\n",worst);
}
