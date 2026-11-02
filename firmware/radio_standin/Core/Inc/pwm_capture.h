#ifndef PWM_CAPTURE_H
#define PWM_CAPTURE_H
#include <stdint.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
  uint32_t rises, periods, period_sum, period_min, period_max;
  uint32_t high_min,high_max,cycles,first_cycle,last_cycle,errors;
  uint32_t rise_us,previous_rise_us;
  bool have_rise,have_period,positive_half;
} PwmCapture;
void PwmCapture_Reset(volatile PwmCapture *capture);
void PwmCapture_Edge(volatile PwmCapture *capture,uint32_t at_us,bool high);
#ifdef __cplusplus
}
#endif
#endif
