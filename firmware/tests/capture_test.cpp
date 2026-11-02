#include "pwm_capture.h"
#include "control.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#define PROGMEM
#include "sine_table.h"

static PwmCapture synthesize(uint16_t tone,bool enabled,uint32_t start) {
  PwmCapture c; PwmCapture_Reset(&c);
  uint32_t phase=0;
  uint32_t increment=uint32_t((uint64_t(tone)*4294967296ULL+50000)/100000);
  for (uint32_t n=0;n<30000;++n) {
    phase+=increment;
    // Feed quantized 1 us captures of the actual checked-in waveform table.
    uint32_t high=uint32_t((800+(enabled?sineTable[phase>>24]:0)+8)/16);
    uint32_t at=start+n*100;
    PwmCapture_Edge(&c,at,true); PwmCapture_Edge(&c,at+high,false);
  }
  return c;
}
int main() {
  double worst=0;
  for (uint16_t tone:Ctcss::presets) {
    PwmCapture c=synthesize(tone,true,0xFFFF0000U); // includes timer rollover
    assert(c.errors==0 && c.periods==29999 && c.period_min==100 && c.period_max==100);
    assert(c.high_min<=13 && c.high_max>=87 && c.cycles>100);
    double hz=double(c.cycles-1)*1000000/(c.last_cycle-c.first_cycle);
    double error=fabs(hz-tone/10.0);
    assert(error<=.1); if (error>worst) worst=error;
  }
  PwmCapture idle=synthesize(1514,false,0);
  assert(idle.cycles==0 && idle.errors==0 && idle.high_min==50 && idle.high_max==50);
  PwmCapture c; PwmCapture_Reset(&c);
  PwmCapture_Edge(&c,0,true); PwmCapture_Edge(&c,100,true); assert(c.errors);
  PwmCapture_Reset(&c); PwmCapture_Edge(&c,0,true); PwmCapture_Edge(&c,99,false); assert(c.errors);
  PwmCapture_Reset(&c); PwmCapture_Edge(&c,0,true); PwmCapture_Edge(&c,50,false);
  PwmCapture_Edge(&c,200,true); assert(c.errors); // missed carrier
  printf("PASS capture: all 50 tones, idle, rollover, edge loss; worst synthetic error %.6f Hz\n",worst);
}
