#pragma once
#include <stdint.h>
namespace Storage {
uint16_t begin();
bool request(uint16_t tone);
// Returns 1 for verified commit, -1 for failure, 0 otherwise.
int8_t service(uint16_t &committedTone);
bool busy();
}
