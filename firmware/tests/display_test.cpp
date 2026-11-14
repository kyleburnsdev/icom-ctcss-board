#include "display.h"
#include "config.h"
#include "Wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
uint32_t fakeMillis=0;
FakeWire Wire;
static Ctcss::Control control;
static Ctcss::Ui ui;
static void run(unsigned ms) {
  for (unsigned i=0;i<ms;++i) {
    ++fakeMillis; uint32_t calls=Wire.calls;
    Display::service(fakeMillis,control,ui,false,false,false);
    assert(Wire.calls-calls<=1);
  }
}
static void row(unsigned n,const char *prefix) {
  assert(!memcmp(Wire.ddram+(n?64:0),prefix,strlen(prefix)));
}
int main() {
  Display::begin(); assert(Wire.timeout==1500);
  run(200); assert(Display::available()); row(0,"Release PTT"); row(1,"To enable TX");
  control.inputs(false,false,true); run(200); row(0,"Tone 151.4 Hz"); row(1,"RX  Tone enabled");
  control.inputs(true,false,true); control.commit(1000); run(200);
  row(0,"TX 151.4 Hz"); row(1,"Next 100.0 Hz");
  ui.screen=Ctcss::Screen::Manual; ui.edit=1514; ui.digit=4; run(200);
  row(1,"TX Hold=Cancel");
  Wire.fail=true; ui.digit=1; run(200); assert(!Display::available());
  assert(control.transmitting && control.activeTone()==1514 && control.saved==1000);
  Wire.fail=false; ui.unavailable(); run(1300); assert(Display::available()); row(0,"TX 151.4 Hz");
#if CTCSS_LCD_GROVE_V4
  assert(Wire.rgb[0]==0 && Wire.rgb[1]==0 && Wire.rgb[8]==0xaa);
  assert(Wire.rgb[2]==64 && Wire.rgb[3]==64 && Wire.rgb[4]==64);
  Wire.fail=true; ui.screen=Ctcss::Screen::Menu; run(200); assert(!Display::available());
  Wire.fail=false; Wire.failBacklight=true; run(1300); assert(!Display::available());
  Wire.failBacklight=false; ui.unavailable(); run(1500); assert(Display::available());
  row(0,"TX 151.4 Hz");
#endif
  puts("PASS display: 16x2 content, TX/pending, Cancel, bounded calls, fault/recovery");
}
