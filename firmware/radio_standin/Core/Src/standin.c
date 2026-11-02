/* Phase-one radio stand-in. GPIO drive means sink LOW, never source 3.3 V.
 * TIM2 captures D9 PWM edges. USART3 carries an ASCII command protocol via
 * ST-Link VCP. Main owns commands/drive/measurements; ISRs own capture and RX.
 */
#include "standin.h"
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "iwdg.h"
#include "pwm_capture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

static uint8_t rx_byte;
static volatile uint16_t rx_head,rx_tail;
static volatile bool rx_lost,uart_error;
static uint8_t rx_ring[256];
static char tx[384];
static bool armed;
static uint32_t last_command_ms;
static char line[80];
static uint8_t line_length;
static bool line_overflow;
static uint8_t commanded; // bit 0 PTT, 1 bypass, 2 button, 3 A, 4 B
static uint32_t edge_at_us,latency_us;
static bool awaiting_edge,latency_valid;
static uint8_t wanted_ptt;
static bool bouncing, bounce_target;
static uint8_t bounce_step;
static uint32_t bounce_due_us, bounce_late_us;

static volatile PwmCapture capture;
static bool measuring;
static uint32_t measure_end_ms;
static uint32_t max_poll_us,previous_poll_us;

static uint32_t micros_now(void) { return __HAL_TIM_GET_COUNTER(&htim2); }
static uint8_t sense(void) {
  return (HAL_GPIO_ReadPin(SENSE_PTT_GPIO_Port,SENSE_PTT_Pin)==GPIO_PIN_SET) |
   ((HAL_GPIO_ReadPin(SENSE_PTT_LED_GPIO_Port,SENSE_PTT_LED_Pin)==GPIO_PIN_SET)<<1) |
   ((HAL_GPIO_ReadPin(SENSE_BYPASS_LED_GPIO_Port,SENSE_BYPASS_LED_Pin)==GPIO_PIN_SET)<<2);
}
static bool tx_ready(void) { return huart3.gState==HAL_UART_STATE_READY; }
static void reply(const char *text) {
  if (!tx_ready()) return; // Poll never consumes another command until TX completes.
  if (text!=tx) { strncpy(tx,text,sizeof tx-1); tx[sizeof tx-1]=0; }
  if (HAL_UART_Transmit_IT(&huart3,(uint8_t *)tx,(uint16_t)strlen(tx))!=HAL_OK) uart_error=true;
}
static void drive(uint8_t bit,bool pressed) {
  GPIO_TypeDef *ports[]={DRIVE_PTT_GPIO_Port,DRIVE_BYPASS_GPIO_Port,DRIVE_BUTTON_GPIO_Port,
                       DRIVE_ENC_A_GPIO_Port,DRIVE_ENC_B_GPIO_Port};
  const uint16_t pins[]={DRIVE_PTT_Pin,DRIVE_BYPASS_Pin,DRIVE_BUTTON_Pin,DRIVE_ENC_A_Pin,DRIVE_ENC_B_Pin};
  HAL_GPIO_WritePin(ports[bit],pins[bit],pressed?GPIO_PIN_RESET:GPIO_PIN_SET);
  if (pressed) commanded|=1U<<bit; else commanded&=~(1U<<bit);
}
void Standin_Release(void) {
  for (uint8_t i=0;i<5;++i) drive(i,false);
  armed=false; awaiting_edge=false; latency_valid=false; bouncing=false;
}
static void capture_reset(void) {
  __disable_irq();
  PwmCapture_Reset(&capture);
  __enable_irq();
}
void Standin_CaptureIrqCheck(void) {
  // Check BEFORE HAL reads CCR1/clears flags. Hardware overcapture or invalid
  // edge spacing invalidates the window; neither is a proof against all losses.
  if (__HAL_TIM_GET_FLAG(&htim2,TIM_FLAG_CC1OF)) {
    ++capture.errors; __HAL_TIM_CLEAR_FLAG(&htim2,TIM_FLAG_CC1OF);
  }
}
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *timer) {
  if (timer->Instance!=TIM2 || timer->Channel!=HAL_TIM_ACTIVE_CHANNEL_1) return;
  uint32_t at=HAL_TIM_ReadCapturedValue(timer,TIM_CHANNEL_1);
  bool high=HAL_GPIO_ReadPin(PWM_CAPTURE_GPIO_Port,PWM_CAPTURE_Pin)==GPIO_PIN_SET;
  PwmCapture_Edge(&capture,at,high);
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *uart) {
  if (uart->Instance!=USART3) return;
  uint16_t next=(rx_head+1)&255;
  if (next==rx_tail) rx_lost=true;
  else { rx_ring[rx_head]=rx_byte; rx_head=next; }
  if (HAL_UART_Receive_IT(&huart3,&rx_byte,1)!=HAL_OK) uart_error=true;
}
void HAL_UART_ErrorCallback(UART_HandleTypeDef *uart) {
  if (uart->Instance==USART3) uart_error=true;
}
void Standin_Init(void) {
  Standin_Release(); capture_reset();
  if (HAL_TIM_IC_Start_IT(&htim2,TIM_CHANNEL_1)!=HAL_OK) Error_Handler();
  if (HAL_UART_Receive_IT(&huart3,&rx_byte,1)!=HAL_OK) Error_Handler();
  previous_poll_us=micros_now();
}
static bool number(const char *text,unsigned long *value) {
  char *end; if (!*text || *text<'0' || *text>'9') return false;
  *value=strtoul(text,&end,10); return *end==0;
}
static void command(void) {
  unsigned long value;
  last_command_ms=HAL_GetTick();
  if (!strcmp(line,"ID")) reply("STANDIN1 phase=1 board=NUCLEO-F767ZI clock_hz=96000000 tick_hz=1000000\n");
  else if (!strcmp(line,"STOP")) { Standin_Release(); measuring=false; reply("OK stopped\n"); }
  else if (!strcmp(line,"ARM")) { Standin_Release(); armed=true; reply("OK armed lease_ms=5000\n"); }
  else if (!strcmp(line,"STATUS")) {
    snprintf(tx,sizeof tx,"STATUS armed=%u drive=%u sense=%u latency_valid=%u latency_us=%lu poll_us=%lu errors=%lu bouncing=%u bounce_late_us=%lu\n",
      armed,commanded,sense(),latency_valid,(unsigned long)latency_us,
      (unsigned long)max_poll_us,(unsigned long)capture.errors,bouncing,(unsigned long)bounce_late_us); reply(tx);
  } else if (!strncmp(line,"BOUNCE ",7) && number(line+7,&value) && value<=1 && armed && !bouncing) {
    bounce_target=value; bounce_step=0; bounce_late_us=0;
    latency_valid=false; awaiting_edge=false;
    drive(0,bounce_target); bouncing=true; bounce_due_us=micros_now()+1000;
    reply("OK bouncing\n");
  } else if (!strncmp(line,"MEASURE ",8) && number(line+8,&value) && value>=100 && value<=4000 && !measuring) {
    capture_reset(); measuring=true; measure_end_ms=HAL_GetTick()+value; reply("OK measuring\n");
  } else {
    static const char *names[]={"PTT ","BYPASS ","BUTTON ","ENCA ","ENCB "};
    for (uint8_t bit=0;bit<5;++bit) {
      size_t n=strlen(names[bit]);
      if (!strncmp(line,names[bit],n) && number(line+n,&value) && value<=1 && armed && !bouncing) {
        if (bit==0) {
          wanted_ptt=value; latency_valid=false;
          awaiting_edge=(sense()&1)!=wanted_ptt;
          edge_at_us=micros_now();
        }
        drive(bit,value); reply("OK drive\n"); return;
      }
    }
    reply("ERR command or not armed\n");
  }
}
static void report_measurement(void) {
  PwmCapture s;
  __disable_irq(); memcpy(&s,(const void *)&capture,sizeof s); __enable_irq();
  uint32_t span=s.last_cycle-s.first_cycle;
  // Millihertz, calculated outside the ISR. No float printf dependency.
  uint32_t carrier=s.period_sum?(uint64_t)s.periods*1000000000ULL/s.period_sum:0;
  uint32_t tone=(s.cycles>1 && span)?(uint64_t)(s.cycles-1)*1000000000ULL/span:0;
  snprintf(tx,sizeof tx,"MEAS periods=%lu carrier_mHz=%lu min_period_us=%lu max_period_us=%lu min_high_us=%lu max_high_us=%lu cycles=%lu tone_mHz=%lu errors=%lu sense=%u\n",
    (unsigned long)s.periods,(unsigned long)carrier,
    (unsigned long)(s.periods?s.period_min:0),(unsigned long)s.period_max,
    (unsigned long)(s.periods?s.high_min:0),(unsigned long)s.high_max,
    (unsigned long)s.cycles,(unsigned long)tone,(unsigned long)s.errors,sense());
  reply(tx); measuring=false;
}
void Standin_Poll(void) {
  HAL_IWDG_Refresh(&hiwdg);
  uint32_t now=micros_now(), elapsed=now-previous_poll_us; previous_poll_us=now;
  if (elapsed>max_poll_us) max_poll_us=elapsed;
  if (bouncing && (int32_t)(now-bounce_due_us)>=0) {
    uint32_t late=now-bounce_due_us;
    if (late>bounce_late_us) bounce_late_us=late;
    ++bounce_step;
    drive(0,(bounce_step&1)?!bounce_target:bounce_target);
    bounce_due_us=now+1000;
    if (bounce_step==8) {
      bouncing=false; wanted_ptt=bounce_target; edge_at_us=now;
      awaiting_edge=(sense()&1)!=wanted_ptt;
    }
  }
  if (awaiting_edge && (sense()&1)==wanted_ptt) {
    latency_us=now-edge_at_us; latency_valid=true; awaiting_edge=false;
  }
  if (armed && (uint32_t)(HAL_GetTick()-last_command_ms)>5000) Standin_Release();
  if (uart_error || rx_lost) {
    Standin_Release(); measuring=false;
    HAL_UART_AbortReceive_IT(&huart3);
    __disable_irq(); rx_tail=rx_head; rx_lost=false; uart_error=false; __enable_irq();
    line_length=0; line_overflow=false;
    if (HAL_UART_Receive_IT(&huart3,&rx_byte,1)!=HAL_OK) Error_Handler();
    if (tx_ready()) reply("ERR UART loss; outputs released\n");
  }
  HAL_GPIO_WritePin(LD1_GPIO_Port,LD1_Pin,armed?GPIO_PIN_SET:GPIO_PIN_RESET);
  HAL_GPIO_WritePin(LD2_GPIO_Port,LD2_Pin,(sense()&1)?GPIO_PIN_SET:GPIO_PIN_RESET);
  if (!tx_ready()) return;
  if (measuring && (int32_t)(HAL_GetTick()-measure_end_ms)>=0) { report_measurement(); return; }
  for (uint8_t n=0;n<32 && rx_tail!=rx_head;++n) {
    char ch=rx_ring[rx_tail]; rx_tail=(rx_tail+1)&255;
    if (ch=='\r') continue;
    if (ch!='\n') {
      if (line_length<sizeof line-1) line[line_length++]=ch; else line_overflow=true;
    } else {
      line[line_length]=0;
      if (line_overflow) { Standin_Release(); reply("ERR line too long; outputs released\n"); }
      else command();
      line_length=0; line_overflow=false; break;
    }
  }
}
