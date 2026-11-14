#include "control.h"
#include "journal.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <initializer_list>
using namespace Ctcss;

static void interlock() {
  for (bool bypassOn : {false,true}) {
    Control c;
    c.inputs(true,bypassOn,false); assert(!c.transmitting && !c.armed);
    c.inputs(true,bypassOn,true); assert(!c.transmitting && !c.armed);
    c.inputs(false,bypassOn,true); assert(!c.transmitting && c.armed);
    c.inputs(true,bypassOn,true); assert(c.transmitting && c.toneEnabled()!=bypassOn);
    assert(c.commit(1000)); assert(c.activeTone()==1514);
    c.inputs(true,true,true); assert(!c.toneEnabled());
    c.inputs(true,false,true); assert(c.toneEnabled() && c.activeTone()==1514);
    c.inputs(false,false,true); assert(!c.transmitting && c.activeTone()==1000);
    c.inputs(true,false,true); assert(c.latched==1000);
    assert(!c.commit(669) && !c.commit(2542));
  }
}
static void inputs() {
  Debouncer d; d.begin(true,0xFFFFFFFC);
  d.update(true,0,5); assert(!d.qualified);
  d.update(true,1,5); assert(d.qualified && d.stable);
  d.update(false,2,5); d.update(true,4,5); d.update(false,6,5);
  d.update(false,10,5); assert(d.stable); d.update(false,11,5); assert(!d.stable);
  Button b; assert(b.update(true,100)==Gesture::None);
  assert(b.update(true,849)==Gesture::None); assert(b.update(true,850)==Gesture::Long);
  assert(b.update(true,2000)==Gesture::None); assert(b.update(false,2001)==Gesture::None);
  b.update(true,2100); assert(b.update(false,2200)==Gesture::Short);
  b.suppress(true,2300); assert(b.update(false,2400)==Gesture::None);
  Encoder e;
  for (int s : {1,0,2}) assert(e.update(uint8_t(s))==0);
  assert(e.update(3)==1);
  e.update(1); e.update(3); e.update(1); e.update(0); e.update(2); assert(e.update(3)==1);
  e.update(0); assert(e.update(3)==0); // invalid diagonal cannot accumulate a detent
}
static void uiTest() {
  for (uint8_t i=0;i<50;++i) {
    assert(validTone(presets[i])); assert(nearestPreset(presets[i])==i);
    if (i) assert(presets[i]>presets[i-1]);
  }
  assert(nearestPreset(681)==0); // nearest low edge
  assert(nearestPreset(1755)==31);
  assert(nearestPreset(685)==1); // nearer 69.3 than 67.0
  assert(nearestPreset(706)==1); // exact midpoint 69.3/71.9 chooses lower
  Ui u; assert(u.gesture(Gesture::Short,1514)==0 && u.screen==Screen::Menu);
  u.gesture(Gesture::Short,1514); assert(u.screen==Screen::Presets && u.preset==24);
  u.rotate(1); assert(u.gesture(Gesture::Short,1514)==1567);
  u.saved(); u.rotate(1); u.gesture(Gesture::Short,1514);
  assert(u.screen==Screen::Manual && u.edit==1514);
  u.rotate(-1); assert(u.edit==514);
  assert(u.gesture(Gesture::Long,1514)==0 && u.rangeError);
  for (int i=0;i<4;++i) u.gesture(Gesture::Short,1514);
  assert(u.digit==4); u.gesture(Gesture::Long,1514); assert(u.screen==Screen::Menu);
  u.gesture(Gesture::Short,1514); assert(u.edit==1514);
  u.edit=670; assert(u.gesture(Gesture::Long,1514)==670);
  u.edit=2541; assert(u.gesture(Gesture::Long,1514)==2541);
  u.unavailable(); assert(u.screen==Screen::Home);
}
static void persistence() {
  uint8_t a[recordSize], b[recordSize], expected[recordSize];
  uint16_t seq,tone;
  memset(a,0xff,sizeof a); memset(b,0xff,sizeof b); assert(newestRecord(a,b)==-1);
  encodeRecord(a,65535,1514); encodeRecord(expected,0,1000);
  assert(newestRecord(a,b)==0);
  // Simulate interruption after every write, including an arbitrary torn byte.
  const uint8_t order[]={0,1,2,3,4,5,6,7,8,9,0};
  for (unsigned cut=0;cut<sizeof order;++cut) {
    for (unsigned torn=0;torn<256;++torn) {
      encodeRecord(b,65534,670);
      for (unsigned k=0;k<cut;++k) b[order[k]]=k==0 ? 0 : expected[order[k]];
      b[order[cut]]=uint8_t(torn);
      int8_t best=newestRecord(a,b); assert(best>=0);
      assert(decodeRecord(best==0?a:b,seq,tone)); assert(tone==1514 || tone==1000);
    }
  }
  memcpy(b,expected,sizeof b); assert(newestRecord(a,b)==1);
  for (uint8_t byte=0;byte<recordSize;++byte) for (uint8_t bit=0;bit<8;++bit) {
    memcpy(b,expected,sizeof b); b[byte]^=1<<bit; assert(!decodeRecord(b,seq,tone));
  }
}
static void exhaustiveSelections() {
  // Independently enumerate the accepted numerical contract, including every
  // invalid uint16_t value and every four-digit manual editor value.
  for (uint32_t value=0;value<=65535;++value) {
    bool valid=value>=670 && value<=2541;
    Control c;
    assert(c.commit(uint16_t(value))==valid);
    assert(c.saved==(valid ? value : 1514));
    if (value<10000) {
      Ui u; u.screen=Screen::Manual; u.edit=uint16_t(value);
      assert(u.gesture(Gesture::Long,1514)==(valid ? value : 0));
      assert(u.rangeError==!valid);
      u.digit=4;
      assert(u.gesture(Gesture::Long,1514)==0 && u.screen==Screen::Menu);
    }
  }
  for (uint16_t value=670;value<=2541;++value) {
    Control c; assert(c.commit(value));
    c.inputs(false,false,true); c.inputs(true,false,true);
    assert(c.transmitting && c.activeTone()==value && c.toneEnabled());
    uint16_t next=value==2541 ? 670 : uint16_t(value+1);
    assert(c.commit(next));
    c.inputs(true,true,true);
    assert(c.transmitting && !c.toneEnabled() && c.activeTone()==value);
    c.inputs(true,false,true);
    assert(c.transmitting && c.toneEnabled() && c.activeTone()==value);
    c.inputs(false,false,true);
    assert(!c.transmitting && c.activeTone()==next);
    c.inputs(true,false,true); assert(c.activeTone()==next);
  }
}

static void exhaustiveInputSequences() {
  // All 65,536 eight-event combinations of microphone/bypass levels after
  // reset, compared with a release-before-press reference state machine.
  for (uint32_t sequence=0;sequence<65536;++sequence) {
    Control c;
    bool released=false;
    for (unsigned event=0;event<8;++event) {
      unsigned levels=(sequence>>(2*event))&3;
      bool pressed=(levels&1)!=0, bypassOn=(levels&2)!=0;
      bool expectedTx=released && pressed;
      c.inputs(pressed,bypassOn,true);
      if (!pressed) released=true;
      assert(c.armed==released && c.transmitting==expectedTx);
      assert(c.toneEnabled()==(expectedTx && !bypassOn));
    }
  }
}
int main() {
  interlock(); inputs(); uiTest(); persistence(); exhaustiveSelections(); exhaustiveInputSequences();
  puts("PASS control, interlocks, bounce/wrap, UI, 50 presets, torn EEPROM writes, CRC corruption");
  puts("PASS exhaustive: 65,536 numeric inputs, 10,000 manual values, 1,872 TX latches, 65,536 eight-event input sequences");
}
