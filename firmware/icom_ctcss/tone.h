#pragma once
#include <stdint.h>
namespace Tone {
void begin();
void set(bool enabled,uint16_t tenthsHz);
bool healthy();
void stopFault();
}
