#ifndef STANDIN_H
#define STANDIN_H
#include <stdint.h>
void Standin_Init(void);
void Standin_Poll(void);
void Standin_CaptureIrqCheck(void);
void Standin_Release(void);
#endif
