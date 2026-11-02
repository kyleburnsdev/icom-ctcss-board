#include <Arduino.h>
#include <avr/wdt.h>
#include <util/atomic.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "config.h"
#include "control.h"
#include "storage.h"
#include "tone.h"
#include "display.h"

uint8_t resetCause __attribute__((section(".noinit")));
void earlyWatchdogDisable() __attribute__((naked,used,section(".init3")));
void earlyWatchdogDisable() { resetCause=MCUSR; MCUSR=0; wdt_disable(); }

static Ctcss::Control control;
static Ctcss::Ui ui;
static Ctcss::Debouncer mic, bypass, buttonInput;
static Ctcss::Button button;
static Ctcss::Encoder encoder;
static bool waveformFault=false, saveError=false, saveFromUi=false;
static uint32_t previousLoop=0, maxLoopUs=0;
static char reply[160];
static uint8_t replyPosition=0;

static void requestSave(uint16_t tone,bool fromUi) {
  if (Storage::busy()) return;
  saveError=false;
  if (tone==control.saved) { if (fromUi) ui.saved(); return; }
  if (Storage::request(tone)) saveFromUi=fromUi;
}

// USB never waits for a host. Replies are drained only into available endpoint
// space, in short chunks, so an absent/stalled host cannot block PTT handling.
static void diagnostics() {
  static char input[40]; static uint8_t length=0; static bool overflow=false;
  if (reply[replyPosition]) {
    int space=Serial.availableForWrite();
    if (Serial.dtr() && space>0) {
      uint8_t count=0;
      while (count<16 && count<space && reply[replyPosition+count]) ++count;
      Serial.write(reinterpret_cast<const uint8_t *>(reply+replyPosition),count);
      replyPosition+=count;
    } else if (!Serial.dtr()) { reply[0]=0; replyPosition=0; }
    return;
  }
  for (uint8_t n=0;n<8 && Serial.available();++n) {
    char c=Serial.read();
    if (c=='\r') continue;
    if (c!='\n') {
      if (length<sizeof(input)-1) input[length++]=c; else overflow=true;
      continue;
    }
    input[length]=0; replyPosition=0;
    if (overflow) snprintf(reply,sizeof reply,"ERR line too long\n");
    else if (!strcmp(input,"STATUS")) {
      snprintf(reply,sizeof reply,"CTCSS1 bench=%u saved=%u active=%u tx=%u bypass=%u armed=%u lcd=%u busy=%u fault=%u loop_us=%lu reset=%u\n",
        CTCSS_BENCH,control.saved,control.activeTone(),control.transmitting,control.bypass,control.armed,
        Display::available(),Storage::busy(),waveformFault,maxLoopUs,resetCause);
    }
#if CTCSS_BENCH
    else if (!strncmp(input,"SAVE ",5)) {
      char *end; unsigned long value=strtoul(input+5,&end,10);
      if (end==input+5 || *end || value>65535 || !Ctcss::validTone(value) || Storage::busy())
        snprintf(reply,sizeof reply,"ERR save\n");
      else { requestSave(value,false); snprintf(reply,sizeof reply,"OK queued; poll STATUS busy=0 saved=%lu\n",value); }
    }
    else if (!strcmp(input,"HANG")) { while (true) {} } // hardware WDT acceptance, bench build only
#endif
    else snprintf(reply,sizeof reply,"ERR command\n");
    length=0; overflow=false; break;
  }
}

void setup() {
  digitalWrite(Pins::radioPtt,LOW); pinMode(Pins::radioPtt,OUTPUT);
  digitalWrite(A1,LOW); pinMode(A1,OUTPUT);
  digitalWrite(A2,LOW); pinMode(A2,OUTPUT);
  // Also support bare-module tests. PCB external pull-ups remain in place.
  const uint8_t inputs[]={Pins::encoderA,Pins::encoderB,Pins::button,Pins::micPtt,Pins::bypass};
  for (uint8_t pin:inputs) pinMode(pin,INPUT_PULLUP);
  uint32_t now=millis();
  mic.begin(digitalRead(Pins::micPtt)==LOW,now);
  bypass.begin(digitalRead(Pins::bypass)==LOW,now);
  buttonInput.begin(digitalRead(Pins::button)==LOW,now);
  encoder.previous=(digitalRead(Pins::encoderA)<<1)|digitalRead(Pins::encoderB);
  button.suppress(buttonInput.stable,now);
  control.saved=Storage::begin();
  Tone::begin(); Tone::set(false,control.saved);
  Serial.begin(115200);
  Display::begin();
  wdt_enable(WDTO_250MS);
  previousLoop=micros();
}

void loop() {
  // Arduino's 1200-baud touch requests a Caterina watchdog reset. Do not feed
  // that watchdog or key PTT while the core is waiting to enter the bootloader.
  // Use dtr(): Serial's bool conversion deliberately delays 10 ms in this core.
  if (Serial.baud()==1200 && !Serial.dtr()) {
    control.transmitting=false; control.armed=false;
    digitalWrite(Pins::radioPtt,LOW); digitalWrite(A1,LOW);
    Tone::set(false,control.saved);
    return;
  }
  uint32_t nowUs=micros();
  uint32_t duration=nowUs-previousLoop; previousLoop=nowUs;
  if (duration>maxLoopUs) maxLoopUs=duration;
  uint32_t now=millis();
  mic.update(digitalRead(Pins::micPtt)==LOW,now,inputQualificationMs);
  bypass.update(digitalRead(Pins::bypass)==LOW,now,inputQualificationMs);
  control.inputs(mic.stable,bypass.stable,mic.qualified && bypass.qualified);
  if (!waveformFault && !Tone::healthy()) { waveformFault=true; Tone::stopFault(); }
  if (waveformFault) { control.transmitting=false; control.armed=false; }
  digitalWrite(Pins::radioPtt,control.transmitting);
  digitalWrite(A1,control.transmitting);
  digitalWrite(A2,control.bypass);
  Tone::set(control.toneEnabled(),control.activeTone());

  uint16_t committed;
  int8_t result=Storage::service(committed);
  if (result==1) { control.commit(committed); if (saveFromUi && Display::available()) ui.saved(); }
  if (result<0) saveError=true;

  // Display failure disables gestures and discards the uncommitted edit buffer.
  // A write already explicitly requested may finish and become durable.
  Display::service(now,control,ui,Storage::busy(),saveError,waveformFault);
  buttonInput.update(digitalRead(Pins::button)==LOW,now,buttonQualificationMs);
  int8_t movement=encoder.update((digitalRead(Pins::encoderA)<<1)|digitalRead(Pins::encoderB));
  if (Display::available() && control.armed && !Storage::busy() && !waveformFault) {
    if (movement) ui.rotate(movement);
    uint16_t requested=ui.gesture(button.update(buttonInput.stable,now),control.saved);
    if (requested) requestSave(requested,true);
  } else {
    button.suppress(buttonInput.stable,now);
    if (!Display::available()) ui.unavailable();
  }
  diagnostics();
  wdt_reset();
}
