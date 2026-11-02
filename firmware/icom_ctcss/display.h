#pragma once
#include <stdint.h>
#include "control.h"
namespace Display {
void begin();
void service(uint32_t now,const Ctcss::Control &control,const Ctcss::Ui &ui,
             bool saving,bool saveError,bool waveformFault);
bool available();
}
