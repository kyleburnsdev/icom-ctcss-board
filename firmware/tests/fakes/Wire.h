#pragma once
#include <stdint.h>
#include <string.h>
// Host-only transaction model, not an electrical bus simulator.
struct FakeWire {
  bool fail=false, timedOut=false;
  uint32_t calls=0, timeout=0;
  uint8_t bytes[8]={}, length=0, address=0;
  char ddram[128]={};
  void begin() { memset(ddram,' ',sizeof ddram); }
  void setClock(uint32_t) {}
  void setWireTimeout(uint32_t value,bool) { timeout=value; }
  void clearWireTimeoutFlag() { timedOut=false; }
  bool getWireTimeoutFlag() { return timedOut; }
  void beginTransmission(uint8_t) { length=0; }
  void write(uint8_t value) { bytes[length++]=value; }
  uint8_t endTransmission() {
    ++calls;
    if (fail) { timedOut=true; return 4; }
    if (length==6) {
      uint8_t value=(bytes[0]&0xf0)|(bytes[3]>>4);
      if (bytes[0]&1) { ddram[address]=char(value); address=(address+1)&127; }
      else if (value&0x80) address=value&127;
      else if (value==1) { memset(ddram,' ',sizeof ddram); address=0; }
    }
    return 0;
  }
};
extern FakeWire Wire;
