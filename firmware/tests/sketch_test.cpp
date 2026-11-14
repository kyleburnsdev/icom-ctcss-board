#include "Arduino.h"
#include "avr/io.h"
#include "Wire.h"
#include "journal.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

uint8_t TCCR1A=0,TCCR1B=0,TIMSK1=0,TIFR1=0,EEDR=0,MCUSR=0;
uint16_t TCNT1=0,ICR1=0,OCR1A=0,EEAR=0;
FakeEecr EECR;
FakeSerial Serial;
FakeWire Wire;
unsigned fakeWatchdogFeeds=0;
static uint64_t clockUs=0,eepromDue=0;
static uint8_t fakeInputs[32],outputs[32],modes[32],eeprom[1024];
static unsigned writes=0;
static bool corruptNextPayload=false;
static uint16_t pendingAddress;
static uint8_t pendingByte;
uint32_t millis() { return static_cast<uint32_t>(clockUs/1000); }
uint32_t micros() { return static_cast<uint32_t>(clockUs); }
void pinMode(uint8_t pin,int mode) { modes[pin]=static_cast<uint8_t>(mode); }
int digitalRead(uint8_t pin) { return fakeInputs[pin]; }
void digitalWrite(uint8_t pin,int value) { outputs[pin]=static_cast<uint8_t>(value); }
uint8_t eeprom_read_byte(const uint8_t *address) {
  uintptr_t offset=reinterpret_cast<uintptr_t>(address);
  assert(offset<sizeof eeprom); return eeprom[offset];
}
void fakeLaunchEeprom() {
  assert(eepromDue==0 && EEAR<sizeof eeprom);
  pendingAddress=EEAR; pendingByte=EEDR; eepromDue=clockUs+3400; ++writes;
}
void TIMER1_OVF_vect();

// Include the unmodified .ino to test its real setup/loop and diagnostics glue.
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wformat"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wformat"
#endif
#ifdef _MSC_VER
#pragma warning(push)
// AVR uint32_t is unsigned long; MSVC uses unsigned int. Both are 32 bits here.
// Original AVR sketch also uses range-checked narrowing conversions. Keep that
// source intact; strict warnings remain enabled for the host model itself.
#pragma warning(disable:4477 4244)
#endif
#include "../icom_ctcss/icom_ctcss.ino"
#ifdef _MSC_VER
#pragma warning(pop)
#endif
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

static void step() {
    clockUs+=100;
    if (eepromDue && clockUs>=eepromDue) {
      eeprom[pendingAddress]=pendingByte; eepromDue=0;
      if (corruptNextPayload && pendingAddress%Ctcss::recordSize==4) {
        eeprom[pendingAddress]^=1; corruptNextPayload=false;
      }
      EECR.value&=static_cast<uint8_t>(~(_BV(EEPE)|_BV(EEMPE)));
    }
    if (TIMSK1 & _BV(TOIE1)) TIMER1_OVF_vect();
    loop();
}
static void tick(unsigned ms) {
  for (unsigned i=0;i<ms*10;++i) step();
}
static void send(const char *text) {
  while (*text) Serial.input.push_back(*text++);
}
static std::string status() {
  Serial.output.clear(); send("STATUS\n"); tick(5);
  assert(Serial.output.find("CTCSS1 ")==0);
  return Serial.output;
}
static unsigned value(const std::string &line,const char *key) {
  size_t start=line.find(key); assert(start!=std::string::npos);
  return static_cast<unsigned>(strtoul(line.c_str()+start+strlen(key),nullptr,10));
}
static void check(bool tx,bool bypassOn,unsigned tone) {
  assert(bool(outputs[8])==tx && bool(outputs[A1])==tx && bool(outputs[A2])==bypassOn);
  std::string line=status();
  assert(bool(value(line,"tx="))==tx && bool(value(line,"bypass="))==bypassOn);
  assert(value(line,"active=")==tone && value(line,"fault=")==0);
}
static void idleWave() { tick(6); assert(OCR1A==800); }
static void activeWave(uint16_t tenthsHz) {
  tick(10);
  uint16_t low=1600,high=0;
  uint16_t previous=OCR1A;
  unsigned first=0,last=0,crossings=0;
  for (unsigned i=0;i<20000;++i) {
    step();
    if(OCR1A<low) low=OCR1A;
    if(OCR1A>high) high=OCR1A;
    if(previous<800 && OCR1A>=800) {
      if(!crossings) first=i;
      last=i; ++crossings;
    }
    previous=OCR1A;
  }
  assert(low<300 && high>1300);
  assert(crossings>100);
  double frequency=double(crossings-1)*10000/(last-first);
  assert(fabs(frequency-tenthsHz/10.0)<.1);
}

int main(int argc,char **argv) {
  const char *scenario=argc>1 ? argv[1] : "normal";
  bool held=strstr(scenario,"held")!=nullptr;
  bool bypassAtBoot=strstr(scenario,"bypass")!=nullptr;
  bool noLcd=!strcmp(scenario,"no-lcd");
  memset(fakeInputs,HIGH,sizeof fakeInputs); memset(eeprom,0xff,sizeof eeprom);
  fakeInputs[7]=held?LOW:HIGH; fakeInputs[10]=bypassAtBoot?LOW:HIGH;
  Wire.fail=noLcd;
  if (!strcmp(scenario,"standalone")) Serial.connected=false;
  if (!strcmp(scenario,"wrap")) clockUs=0xFFFFFFFCULL*1000;
  setup(); tick(200);
  assert(outputs[8]==0 && outputs[A1]==0);
  Serial.connected=true;
  assert(bool(value(status(),"armed="))==!held);
  idleWave();
  if (held) { tick(100); assert(outputs[8]==0); fakeInputs[7]=HIGH; tick(10); }
  fakeInputs[10]=HIGH; tick(10);
  check(false,false,1514);
  // Four-millisecond input glitches must not propagate; six ms stable does.
  fakeInputs[7]=LOW; tick(4); assert(outputs[8]==0);
  fakeInputs[7]=HIGH; tick(6); assert(outputs[8]==0);
  fakeInputs[7]=LOW; tick(6); check(true,false,1514); activeWave(1514);
  fakeInputs[10]=LOW; tick(4); assert(outputs[A2]==0 && outputs[8]==1);
  fakeInputs[10]=HIGH; tick(6); check(true,false,1514);
  fakeInputs[10]=LOW; tick(6); check(true,true,1514); idleWave();
  // Execute real SAVE parsing, asynchronous storage service, readback and commit.
  if (!strcmp(scenario,"write-fault")) {
    corruptNextPayload=true; send("SAVE 1000\n"); tick(150);
    assert(!Storage::busy() && writes==11);
    check(true,true,1514); assert(value(status(),"saved=")==1514);
  }
  unsigned expectedWrites=writes+11;
  Serial.output.clear(); send("SAVE 1000\nSAVE 670\n"); tick(150);
  assert(Serial.output.find("ERR save")!=std::string::npos);
  assert(!Storage::busy() && writes==expectedWrites);
  check(true,true,1514);
  assert(value(status(),"saved=")==1000);
  // Display-only failure does not unkey or change the transmission latch.
  // An unplug/NACK is discovered on the next attempted display transaction;
  // unchanged display content alone does not generate a bus heartbeat.
  Wire.fail=true; fakeInputs[10]=HIGH; tick(6); check(true,false,1514);
  tick(100);
  assert(value(status(),"lcd=")==0);
  fakeInputs[6]=LOW; tick(800); fakeInputs[6]=HIGH; tick(20);
  for (int ab : {1,0,2,3}) {
    fakeInputs[4]=static_cast<uint8_t>((ab>>1)&1); fakeInputs[5]=static_cast<uint8_t>(ab&1); tick(1);
  }
  assert(writes==expectedWrites && value(status(),"saved=")==1000);
  fakeInputs[10]=LOW; tick(6); check(true,true,1514); idleWave();
  fakeInputs[10]=HIGH; tick(6); check(true,false,1514); activeWave(1514);
  // A stalled diagnostic endpoint cannot stop input handling in the real loop.
  Serial.stalled=true; send("STATUS\n"); tick(5);
  fakeInputs[7]=HIGH; tick(6); assert(outputs[8]==0 && outputs[A1]==0);
  fakeInputs[7]=LOW; tick(6); assert(outputs[8]==1 && outputs[A1]==1);
  Serial.stalled=false; tick(10); check(true,false,1000); activeWave(1000);
  Serial.connected=false; send("STATUS\n"); tick(5);
  fakeInputs[7]=HIGH; tick(6); assert(outputs[8]==0);
  Serial.connected=true; tick(10); check(false,false,1000); idleWave();
  Wire.fail=false; tick(1200); assert(value(status(),"lcd=")==(CTCSS_LCD_ADDRESS?1U:0U));
  unsigned priorWrites=writes; send("SAVE 1000\n"); tick(150); assert(writes==priorWrites);
  // The upload path must release an actively keyed output and stop WDT feeds.
  fakeInputs[7]=LOW; tick(6); check(true,false,1000);
  unsigned feeds=fakeWatchdogFeeds;
  Serial.baudRate=1200; Serial.connected=false; tick(10);
  assert(outputs[8]==0 && outputs[A1]==0 && fakeWatchdogFeeds==feeds);
  Serial.baudRate=115200; Serial.connected=true; tick(10);
  assert(outputs[8]==0); // still held; a release/new press is required
  fakeInputs[7]=HIGH; tick(6); fakeInputs[7]=LOW; tick(6); check(true,false,1000);
  // Timer configuration failure is latched and stops PTT/waveform in the loop.
  TCCR1B^=_BV(CS10); tick(1);
  assert(outputs[8]==0 && outputs[A1]==0 && TIMSK1==0 && outputs[9]==LOW);
  TCCR1B^=_BV(CS10); tick(10); assert(outputs[8]==0);
  assert(value(status(),"fault=")==1);
  printf("PASS actual sketch loop (%s): boot/interlock, bounce, PTT/bypass, pending save/latch, EEPROM service, LCD loss/recovery, stalled/absent USB, timer fault, upload release\n",scenario);
}
