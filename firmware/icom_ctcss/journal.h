#pragma once
#include <stdint.h>
#include "control.h"

namespace Ctcss {
// Two 10-byte slots. Commit marker is invalidated FIRST and written LAST.
// CRC covers schema, sequence and tone; reserved bytes must be zero.
constexpr uint8_t recordSize = 10, recordMarker = 0xA5;
uint16_t crc16(const uint8_t *bytes, uint8_t length);
void encodeRecord(uint8_t *bytes, uint16_t sequence, uint16_t tone);
bool decodeRecord(const uint8_t *bytes, uint16_t &sequence, uint16_t &tone);
int8_t newestRecord(const uint8_t *a, const uint8_t *b);
}
