#include "storage.h"
#include "journal.h"
#include <avr/io.h>
#include <avr/eeprom.h>
#include <util/atomic.h>
#include <string.h>

namespace Storage {
static uint8_t records[2][Ctcss::recordSize], pending[Ctcss::recordSize];
static int8_t active=-1, step=-1;
static uint8_t target;
static uint16_t sequence=0;
static uint8_t readByte(uint16_t address) {
  return eeprom_read_byte(reinterpret_cast<const uint8_t *>(address));
}
uint16_t begin() {
  for (uint8_t s=0;s<2;++s) for (uint8_t i=0;i<Ctcss::recordSize;++i)
    records[s][i]=readByte(s*Ctcss::recordSize+i);
  active=Ctcss::newestRecord(records[0],records[1]);
  uint16_t tone=Ctcss::defaultTone;
  if (active>=0) Ctcss::decodeRecord(records[active],sequence,tone);
  return tone;
}
bool busy() { return step>=0; }
bool request(uint16_t tone) {
  if (busy() || !Ctcss::validTone(tone)) return false;
  target=active==0 ? 1 : 0;
  Ctcss::encodeRecord(pending,sequence+1,tone);
  step=0;
  return true;
}
static void launchByte(uint16_t address,uint8_t value) {
  // Nonblocking erase/write: hardware takes ~3.4 ms; loop polls EEPE.
  // No other module owns EEPROM. Interrupts masked only for the launch sequence.
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    EEAR=address; EEDR=value;
    EECR &= ~(_BV(EEPM1)|_BV(EEPM0));
    EECR |= _BV(EEMPE);
    EECR |= _BV(EEPE);
  }
}
int8_t service(uint16_t &tone) {
  if (!busy() || (EECR & _BV(EEPE))) return 0;
  uint16_t base=target*Ctcss::recordSize;
  if (step==0) launchByte(base,0); // invalidate destination, preserving prior slot
  else if (step<Ctcss::recordSize) launchByte(base+step,pending[step]);
  else if (step==Ctcss::recordSize) launchByte(base,Ctcss::recordMarker);
  else {
    for (uint8_t i=0;i<Ctcss::recordSize;++i) records[target][i]=readByte(base+i);
    step=-1;
    uint16_t seq;
    if (memcmp(pending,records[target],Ctcss::recordSize) ||
        !Ctcss::decodeRecord(records[target],seq,tone)) return -1;
    sequence=seq; active=target; return 1;
  }
  ++step;
  return 0;
}
}
