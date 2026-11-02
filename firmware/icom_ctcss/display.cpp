#include "display.h"
#include "config.h"
#include <Arduino.h>
#include <Wire.h>
#include <stdio.h>
#include <string.h>

namespace Display {
// Explicit common PCF8574 backpack mapping: P0 RS, P1 RW, P2 E, P3 BL,
// P4..P7 D4..D7. Change these constants after identifying a different backpack.
constexpr uint8_t rsMask=1, enableMask=4, backlightMask=8;
constexpr uint8_t dataPins[4]={4,5,6,7};
static bool online=false;
static uint8_t initStep=0, position=0, renderStep=0;
static uint32_t due=0, frameAt=0;
static char wanted[32], shown[32];
static uint8_t cursor=255, shownCursor=255;
static uint8_t packed(uint8_t nibble,bool data) {
  uint8_t result=backlightMask|(data?rsMask:0);
  for (uint8_t i=0;i<4;++i) if (nibble & (1<<i)) result|=1<<dataPins[i];
  return result;
}
static bool write(uint8_t value,bool data,bool half=false) {
  Wire.clearWireTimeoutFlag();
  Wire.beginTransmission(CTCSS_LCD_ADDRESS);
  uint8_t high=packed(value>>4,data), low=packed(value & 15,data);
  Wire.write(high); Wire.write(high|enableMask); Wire.write(high);
  if (!half) { Wire.write(low); Wire.write(low|enableMask); Wire.write(low); }
  uint8_t error=Wire.endTransmission();
  return error==0 && !Wire.getWireTimeoutFlag();
}
void begin() {
  memset(shown,0,sizeof shown);
  if (!CTCSS_LCD_ADDRESS) return;
  Wire.begin(); Wire.setClock(100000); Wire.setWireTimeout(1500,true);
  due=millis()+50;
}
bool available() { return online; }
static void row(uint8_t r,const char *text) {
  memset(wanted+r*16,' ',16);
  for (uint8_t i=0;i<16 && text[i];++i) wanted[r*16+i]=text[i];
}
static void render(const Ctcss::Control &c,const Ctcss::Ui &u,bool saving,bool error,bool fault) {
  char line[24]; cursor=255;
  uint16_t tone=c.activeTone();
  if (fault) { row(0,"Waveform fault"); row(1,"Reset required"); return; }
  if (!c.armed) { row(0,"Release PTT"); row(1,"To enable TX"); return; }
  switch (u.screen) {
    case Ctcss::Screen::Home:
      snprintf(line,sizeof line,"%s %03u.%u Hz",c.transmitting?"TX":"Tone",tone/10,tone%10); row(0,line);
      if (c.transmitting && c.saved!=c.latched) {
        snprintf(line,sizeof line,"Next %03u.%u %s",c.saved/10,c.saved%10,c.bypass?"BYP":"Hz"); row(1,line);
      } else row(1,c.bypass ? (c.transmitting?"TX  BYPASS":"RX  BYPASS") :
                                (c.transmitting?"TX  Tone enabled":"RX  Tone enabled"));
      break;
    case Ctcss::Screen::Menu:
      row(0,u.menu==0?">Presets":u.menu==1?">Manual":">Back");
      row(1,c.transmitting?"TX  Press=Select":"Press=Select"); break;
    case Ctcss::Screen::Presets:
      tone=Ctcss::presets[u.preset];
      snprintf(line,sizeof line,"Preset %03u.%u Hz",tone/10,tone%10); row(0,line);
      row(1,c.transmitting?"TX Press=Save":"Press=Save"); break;
    case Ctcss::Screen::Manual:
      snprintf(line,sizeof line,"Manual %03u.%u Hz",u.edit/10,u.edit%10); row(0,line);
      if (u.rangeError) {
        row(1,"Range 067-254.1");
        if (c.transmitting) { wanted[30]='T'; wanted[31]='X'; }
      } else if (u.digit==4) row(1,c.transmitting?"TX Hold=Cancel":">Cancel  Hold=OK");
      else row(1,c.transmitting?"TX Hold=Save":"Hold=Save");
      if (u.digit<4) cursor=7+u.digit+(u.digit==3?1:0);
      break;
  }
  if (saving) row(1,c.transmitting?"TX Saving...":"Saving...");
  if (error) row(1,c.transmitting?"TX Save failed":"Save failed");
}
void service(uint32_t now,const Ctcss::Control &c,const Ctcss::Ui &u,bool saving,bool error,bool fault) {
  if (!CTCSS_LCD_ADDRESS || int32_t(now-due)<0) return;
  due=now+1; // one transaction per loop; PTT is serviced between transactions
  bool ok=true;
  if (!online) {
    const uint8_t commands[]={0x30,0x30,0x30,0x20,0x28,0x08,0x01,0x06,0x0C};
    ok=write(commands[initStep],false,initStep<4);
    if (ok) {
      due=now+5;
      if (++initStep==sizeof commands) {
        initStep=0; online=true; memset(shown,0,sizeof shown); shownCursor=255;
        frameAt=now-50; renderStep=0;
      }
    }
  } else {
    if (uint32_t(now-frameAt)>=50 && renderStep==0) { render(c,u,saving,error,fault); frameAt=now; }
    if (renderStep==3) { ok=write(0x80+cursor,false); shownCursor=cursor; renderStep=0; }
    else if (renderStep==1) { ok=write(wanted[position],true); if (ok) shown[position]=wanted[position]; renderStep=0; shownCursor=254; }
    else {
      for (position=0;position<32 && wanted[position]==shown[position];++position) {}
      if (position<32) { ok=write(0x80+(position<16?position:0x40+position-16),false); renderStep=1; }
      else if (cursor!=shownCursor) {
        ok=write(cursor==255?0x0C:0x0E,false);
        if (ok && cursor!=255) { renderStep=2; } else shownCursor=cursor;
      }
    }
    // Cursor placement is its own bounded transaction on the next service.
    if (renderStep==2) renderStep=3;
  }
  if (!ok) { online=false; initStep=0; renderStep=0; due=now+1000; }
}
}
