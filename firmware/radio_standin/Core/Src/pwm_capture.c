#include "pwm_capture.h"
#include <string.h>

void PwmCapture_Reset(volatile PwmCapture *c) {
  memset((void *)c,0,sizeof *c);
  c->period_min=UINT32_MAX; c->high_min=UINT32_MAX;
}
void PwmCapture_Edge(volatile PwmCapture *c,uint32_t at,bool high) {
  if (high) {
    if (c->have_rise) ++c->errors;
    if (c->have_period) {
      uint32_t period=at-c->previous_rise_us;
      if (period<80 || period>120) ++c->errors;
      else {
        ++c->periods; c->period_sum+=period;
        if (period<c->period_min) c->period_min=period;
        if (period>c->period_max) c->period_max=period;
      }
    }
    c->previous_rise_us=c->rise_us=at;
    c->have_rise=true; c->have_period=true; ++c->rises;
  } else if (c->have_rise) {
    uint32_t width=at-c->rise_us; c->have_rise=false;
    if (width<5 || width>95) { ++c->errors; return; }
    if (width<c->high_min) c->high_min=width;
    if (width>c->high_max) c->high_max=width;
    // Hysteresis rejects duty quantization at the midpoint. Crossing times
    // are carrier-quantized; average many tone cycles, never a single pair.
    if (width<47) c->positive_half=false;
    if (width>53 && !c->positive_half) {
      c->positive_half=true;
      if (c->cycles==0) c->first_cycle=at;
      c->last_cycle=at; ++c->cycles;
    }
  } else if (c->have_period) ++c->errors;
}
