"""Build the self-contained November 13 firmware testing field guide.

Run from the repository root: python tools/build-firmware-learning-guide.py
Requires reportlab and Pillow. Reads retained evidence only; never opens hardware.
Final PDF goes in docs/learning; QA metadata goes in .agent-scratch/firmware-learning-guide.
Original screenshots are embedded unchanged. Annotation marks are PDF vectors.
"""
from pathlib import Path
import hashlib
import html
import json
import math
import textwrap
from collections import OrderedDict
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/verification/firmware-phase1/2026-11-13'
OUT=ROOT/'docs/learning/firmware-testing-field-guide-2026-11-13.pdf'
QA=ROOT/'.agent-scratch/firmware-learning-guide'
OUT.parent.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Mono','consola.ttf')]:
    path=Path('C:/Windows/Fonts')/file
    if path.exists():pdfmetrics.registerFont(TTFont(name,str(path)))
    else:
        fallback={'Body':'Helvetica','Bold':'Helvetica-Bold','Mono':'Courier'}[name]
        pdfmetrics.registerFont(pdfmetrics.Font(name,fallback,'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
W,H=792,612
BLACK=colors.HexColor('#161616');BLUE=colors.HexColor('#075e94')
GRAY=colors.HexColor('#616971');LIGHT=colors.HexColor('#e6eaed')
screens=OrderedDict();screen_paths={}
for p in sorted(BASE.rglob('*')):
    if p.suffix.lower() not in ('.png','.bmp'):continue
    with PILImage.open(p) as im:
        if im.size!=(800,480):continue
        key=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
    if key not in screens:screens[key]={'id':f'S{len(screens)+1:02}','path':p,'aliases':[]}
    screens[key]['aliases'].append(p.relative_to(BASE).as_posix())
    screen_paths[p.relative_to(BASE).as_posix()]=screens[key]['id']


class Book:
    def __init__(self):
        self.c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
        self.c.setTitle('Learning Arduino firmware testing at the bench')
        self.c.setAuthor('Prepared for Kyle Burns from the retained project evidence')
        self.c.setSubject('November 13 2026 Pro Micro firmware verification learning guide')
        self.pages=[];self.assets=set();self.toc=[]

    def page(self,title,sub='',chapter=None):
        if self.pages:self.c.showPage()
        n=len(self.pages)+1;self.pages.append(title)
        self.c.setFillColor(BLACK);self.c.setFont('Bold',21)
        self.c.drawString(36,568,title)
        self.c.setFont('Body',10);self.c.setFillColor(GRAY)
        self.c.drawString(36,548,sub or 'Arduino firmware testing  |  November 13 2026')
        self.c.setStrokeColor(LIGHT);self.c.line(36,537,756,537)
        self.c.setFont('Body',8);self.c.drawString(36,22,'Icom CTCSS board  |  Learning from the actual bench session')
        self.c.drawRightString(756,22,str(n))
        self.c.bookmarkPage(f'p{n}')
        self.c.addOutlineEntry(title,f'p{n}',0,False)
        if chapter:self.toc.append((chapter,n))
        return 523

    def p(self,text,x,y,w,size=10.6,leading=14.3,color=BLACK,gap=9):
        style=ParagraphStyle('p',fontName='Body',fontSize=size,leading=leading,textColor=color,
                             spaceAfter=0,allowWidows=0,allowOrphans=0)
        para=Paragraph(text,style);_,height=para.wrap(w,1000)
        if y-height<43:raise ValueError(f'Page {len(self.pages)} overflow at {text[:75]} ({y-height})')
        para.drawOn(self.c,x,y-height)
        return y-height-gap

    def section(self,title,paragraphs,x,y,w):
        y=self.p(f'<b>{title}</b>',x,y,w,12,15,gap=7)
        for text in paragraphs:y=self.p(text,x,y,w)
        return y-7

    def cols(self,left,right,y=519):
        for x,items in [(36,left),(410,right)]:
            yy=y
            for title,paras in items:yy=self.section(title,paras,x,yy,346)

    def code(self,lines,x,y,w,size=8.5):
        if isinstance(lines,str):lines=lines.splitlines()
        wrapped=[]
        for line in lines:
            wrapped+=textwrap.wrap(line,max(20,int((w-20)/(size*.60))),replace_whitespace=False,drop_whitespace=False) or ['']
        h=len(wrapped)*(size+3)+18
        if y-h<43:raise ValueError(f'Code overflow page {len(self.pages)}')
        self.c.setFillColor(colors.HexColor('#f2f4f6'));self.c.roundRect(x,y-h,w,h,5,fill=1,stroke=0)
        self.c.setFillColor(BLACK);self.c.setFont('Mono',size)
        for i,line in enumerate(wrapped):self.c.drawString(x+10,y-13-i*(size+3),line)
        return y-h-12

    def table(self,headers,rows,x,y,width,widths=None,size=9.4):
        if widths is None:widths=[width/len(headers)]*len(headers)
        style=ParagraphStyle('cell',fontName='Body',fontSize=size,leading=size+3,textColor=BLACK)
        def cell(v):return Paragraph(html.escape(str(v)).replace('\n','<br/>'),style)
        data=[[cell(v) for v in row] for row in [headers]+rows]
        t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LINEBELOW',(0,0),(-1,0),.8,GRAY),('LINEBELOW',(0,1),(-1,-1),.3,LIGHT),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        _,height=t.wrap(width,1000)
        if y-height<43:raise ValueError(f'Table overflow page {len(self.pages)}')
        t.drawOn(self.c,x,y-height);return y-height-13

    def image(self,path,x,y,w,h):
        self.c.drawImage(ImageReader(str(path)),x,y,width=w,height=h,mask='auto')
        self.assets.add(str(path.relative_to(ROOT)))

    def arrow(self,x1,y1,x2,y2):
        self.c.setStrokeColor(BLUE);self.c.setFillColor(BLUE);self.c.setLineWidth(1)
        self.c.line(x1,y1,x2,y2)
        angle=math.atan2(y2-y1,x2-x1)
        p=self.c.beginPath();p.moveTo(x2,y2)
        for a in [angle+2.65,angle-2.65]:p.lineTo(x2+6*math.cos(a),y2+6*math.sin(a))
        p.close();self.c.drawPath(p,fill=1,stroke=0)

    def screen(self,title,rel,notes,caption,lesson,marks):
        sid=screen_paths[rel];self.page(title,f'Annotated instrument screen {sid}  |  Original screen pixels retained')
        x,y,w,h=36,172,552,331.2;self.image(BASE/rel,x,y,w,h)
        for i,(target,bubble) in enumerate(marks,1):
            tx,ty=x+target[0]/800*w,y+h-target[1]/480*h
            bx,by=x+bubble[0]/800*w,y+h-bubble[1]/480*h
            self.arrow(bx,by,tx,ty);self.c.setFillColor(colors.white);self.c.setStrokeColor(BLUE)
            self.c.circle(bx,by,8,fill=1,stroke=1);self.c.setFillColor(BLUE);self.c.setFont('Bold',9)
            self.c.drawCentredString(bx,by-3,str(i))
        yy=503
        for i,note in enumerate(notes,1):yy=self.p(f'<b>{i}</b> {note}',610,yy,146,9.7,12.5,gap=12)
        yy=self.p(caption,36,153,720,10.2,13.4)
        yy=self.p('<b>What to learn</b> '+lesson,36,yy,720,10.2,13.4)
        self.p('Evidence: '+html.escape(rel),36,yy,720,7.5,9.4,color=GRAY)

    def plot(self,title,rel,notes,caption):
        self.page(title,'Analysis plot reconstructed from retained samples  |  Not an oscilloscope screen')
        path=BASE/rel
        with PILImage.open(path) as im:iw,ih=im.size
        scale=min(700/iw,383/ih);w,h=iw*scale,ih*scale
        self.image(path,36+(720-w)/2,516-h,w,h)
        y=516-h-10
        y=self.p(caption,36,y,720,10.2,13,gap=7)
        # Short parallel reading cues under the figure.
        for x,text in zip([36,282,528],notes):self.p(text,x,y,228,9.5,12)

    def finish(self):
        self.c.save()
        (QA/'book-structure.json').write_text(json.dumps({'pages':self.pages,'chapters':self.toc,
            'assets':sorted(self.assets),'screen_files':sum(len(x['aliases']) for x in screens.values()),
            'unique_screens':len(screens),'output':str(OUT)},indent=2)+'\n')


b=Book()
b.page('Learning Arduino firmware testing at the bench','A worked field guide for Kyle Burns  |  November 13 2026',chapter='Start here')
y=b.p('Today we built strong evidence that the Pro Micro firmware behaves correctly at its digital interfaces. This guide explains how you could plan, operate and evaluate the same tests yourself. It follows the actual session, including the measurements that changed our plan and the test assumptions we had to correct.',36,515,720,14,19,gap=18)
y=b.table(['What the final production image demonstrated','Observed result'],[
    ('Physical PTT input to output','12 transitions; worst 5.1478 ms against 25 ms'),
    ('Bypass to midpoint / return of modulation','Worst 10.2598 ms / 5.3940 ms'),
    ('Selected 151.4 Hz with COM port closed','151.39628797 Hz on nominal scope timebase'),
    ('Carrier continuity in that six-second record','59,998 complete periods; no missing periods detected'),
    ('Ending state','Production firmware, 151.4 Hz, display home, PTT released, fixture disarmed')],36,y,720,[360,360],10)
y=b.p('The working conclusion is readiness for <b>staged hardware integration</b>. Actual encoder behavior, power interruption, the deferred physical display-bus fault test, longer coverage and loaded audio/radio behavior remain separate checks.',36,y,720,11,15)
b.p('<b>How to use this book</b> Read the setup and measurement chapters first, then work through the annotated cases. Blue numbered markers are added guide annotations, not instrument readouts. The appendix contains all 38 distinct instrument screens retained in 41 files; duplicate paths are indexed once. Screen pictures and raw-data plots are always labeled separately.',36,y,720,10.6,14.3)

b.page('Contents','Use the PDF bookmarks for direct navigation; printed page numbers appear below')
b.c.doForm('GuideContents')

b.page('A test starts with a question','Choose the claim before choosing an instrument',chapter='Plan the evidence')
b.cols([
 ('Make the claim measurable',[
  'A useful question is: does a stable PTT press make D8 assert within 25 ms? It identifies the input, output, timing reference and limit. A weaker question is simply whether the board seems to work.',
  'For every experiment, write the starting state, stimulus, expected response, observation window and cleanup. Decide in advance what would fail the test. This prevents a pleasing trace from becoming its own acceptance criterion.']),
 ('Separate the evidence levels',[
  '<b>Host tests</b> exercise software logic against models. <b>USB replies</b> expose firmware state. <b>Measured pins</b> establish electrical behavior. <b>Loaded board and radio tests</b> establish the final interfaces. Each adds evidence the previous level cannot provide.',
  'We followed that order so a physical failure could be narrowed to software, fixture, power or acquisition instead of changing everything at once.'])
],[
 ('Classify the outcome honestly',[
  '<b>Pass:</b> complete evidence meets the stated limits. <b>Fail:</b> complete evidence contradicts them. <b>Inconclusive:</b> missing or unreliable evidence prevents a decision. <b>Not run:</b> the case was never performed.',
  'A trigger timeout is an acquisition failure, not proof the firmware failed. Conversely, a script exit code is not sufficient if its samples are partial or its evaluator is wrong.']),
 ('Use two different checks where practical',[
  'The Pro Micro could report tx=1 while a pin was incorrectly mapped. The scope independently measured D8. The tone estimator decoded pulse widths rather than copying the DDS sine table. The final preset save checked an independently counted number of encoder detents.',
  'Keep failures. Run A of the mixed test failed its count oracle, while its physical PTT measurements passed. Understanding that distinction was part of the testing.'])
])

b.page('The actual sequence we followed','Software first, then passive measurements, then controlled physical inputs')
y=b.table(['Stage','What we did','Why it came next'],[
 ('Software','Control, journal, display, actual tone ISR and actual-sketch host tests; AVR builds','Find logic defects before involving wiring'),
 ('USB only','Identity, saves, reset recovery, parser robustness','Establish a known responding image and a restorable setting'),
 ('Passive observation','D9 PWM and VCC; loose resistor measurements','Check electrical conditions without driving signal pins'),
 ('Minimal fixture','F767 open-drain PTT and bypass with pull-ups','Repeat real input stimulus without manual contact timing'),
 ('Electrical timing','D7/D8, save activity, bounce, watchdog; then D10/D9 bypass','Measure response from actual edges'),
 ('Real display and simulated controls','Grove driver, encoder/button UI, saves, Cancel, range error','Exercise actual AVR display work alongside control logic'),
 ('Mixed stress','80 accepted PTT pairs and detents, background saves, alternating bypass','Check interaction under repeated activity'),
 ('Production image','Verified upload, disabled bench commands, UI/PTT/bypass and closed-port tone','Check the configuration intended to remain installed')],36,516,720,[97,326,297],9.6)
b.p('The KA3005P supply and radio were never connected to the DUT. The Saleae was discovered but did not acquire Arduino evidence. The H743 was not used. Having an instrument at the bench is not evidence that its intended tests were performed.',36,y,720,10.3,14)

b.page('Know each tool and each pin','The device under test is the Pro Micro; the F767 supplies simulated contacts',chapter='Build and power the setup')
y=b.table(['Bench item','Role actually used','Important boundary'],[
 ('5 V / 16 MHz Pro Micro','Firmware under test; application COM14','ATmega32U4 board; Arduino pin labels used here'),
 ('NUCLEO F767ZI','Open-drain stimulus; ST-Link CN1 / COM5','Five-second arm lease; board power rails separate'),
 ('Rigol DS1202Z-E','Two-channel voltage, edge and raw-PWM capture','Two analog channels; no simultaneous observation of all pins'),
 ('OWON XDM1251','VCC and loose resistor measurements; COM15','User called it XDM125; exact USB identity was checked'),
 ('KA3005P, Saleae Logic 8, H743','Available or discovered, not used for DUT acceptance','No PSU stimulus, Saleae DUT record or H743 result')],36,517,720,[160,295,265],10)
b.table(['Pro Micro pin','Purpose','Pro Micro pin','Purpose'],[
 ('D2 / D3','Grove SDA / SCL','D4 / D5','Encoder A / B'),('D6','Encoder pushbutton','D7','PTT input, active LOW'),
 ('D8','PTT command, active HIGH','D9','Raw PWM output'),('D10','Bypass input, active LOW','A1 / A2','LED commands, not electrically timed here')],36,y,720,[95,265,95,265],10)

b.page('Wire the simulated contacts','Schematic connection view, not a breadboard hole map')
c=b.c
def box(x,y,w,h,label):
    c.setFillColor(colors.HexColor('#f4f6f7'));c.setStrokeColor(GRAY);c.roundRect(x,y,w,h,6,fill=1,stroke=1)
    c.setFillColor(BLACK);c.setFont('Bold',12);c.drawCentredString(x+w/2,y+h/2-4,label)
box(55,310,190,65,'NUCLEO open drain');box(528,310,205,65,'Arduino input node')
c.setStrokeColor(BLACK);c.setLineWidth(1.4);c.line(245,343,330,343);c.rect(330,335,65,16,fill=0,stroke=1);c.line(395,343,528,343)
c.setFont('Body',11);c.drawCentredString(362,365,'1 kOhm series')
c.circle(473,343,3,fill=1);c.line(473,343,473,400);c.rect(465,400,16,50,fill=0,stroke=1);c.line(473,450,473,478)
c.drawString(493,421,'10 kOhm pull-up');c.drawString(493,469,'Arduino VCC')
c.line(150,310,150,270);c.line(150,270,630,270);c.line(630,270,630,310);c.drawCentredString(390,251,'Common GND; do not join the two VCC rails')
b.p('Repeat this circuit once for each stimulus input. The NUCLEO closes the contact by sinking LOW; it releases the contact by becoming high impedance. HIGH comes from the Arduino-side pull-up. The series resistor is not a logic-level converter.',36,217,720,11,15)
b.p('The measured input LOW was around 0.48-0.50 V, not exactly zero. In the external-only ideal divider, 4.38 V through 10 kOhm and 1 kOhm gives about 0.40 V at the Arduino node. GPIO LOW voltage and the Arduino internal pull-up also affect the real result. Measure the node; do not assume every asserted input must be exactly 0 V.',36,147,720,10.6,14.3)
b.p('This session used no output-sense dividers on the F767. Consequently sense=6 and latency_valid=0 were floating/unqualified feedback, not valid Arduino output measurements. The scope supplied the independent output evidence.',36,77,720,10,13)

b.page('Exact drive connections and power order','These are the original working connections; the proposed SCL rewire was never made')
y=b.table(['NUCLEO F767ZI connector','Through 1 kOhm to Pro Micro','Pull-up at Arduino input'],[
 ('PF12 / D8, CN7 pin 20','D7 PTT','10 kOhm to Arduino VCC'),
 ('PF13 / D7, CN10 pin 2','D10 bypass','10 kOhm to Arduino VCC'),
 ('PF14 / D4, CN10 pin 8','D6 button','10 kOhm to Arduino VCC'),
 ('PF15 / D2, CN10 pin 12','D4 encoder A','10 kOhm to Arduino VCC'),
 ('PE13 / D3, CN10 pin 10','D5 encoder B','10 kOhm to Arduino VCC'),
 ('GND, CN10 pin 5','Arduino GND directly','No resistor')],36,516,720,[274,225,221],10)
b.cols([
 ('Power changes',[
  '1. STOP and verify armed=0, drive=0. Unplug Arduino USB first, then NUCLEO USB before moving probes or wires.',
  '2. Reconnect NUCLEO ST-Link CN1 first. Identify it and STOP/read back all released drives. Reconnect Arduino USB second.',
  '3. Check saved tone, tx=0, bypass=0, busy=0 and fault=0. Allow startup interlock to arm after released inputs qualify.'])
],[
 ('Probe configurations',[
  '<b>Idle or long tone:</b> D9 to the selected scope channel. <b>PTT timing:</b> CH1 D7, CH2 D8. <b>Bypass timing:</b> CH1 D10, CH2 D9.',
  'Both probe ground clips go to Arduino GND; both physical switches and scope channel ratios are x10. This is a ground-referenced circuit, not a floating measurement.',
  'Use pin labels for each board separately: NUCLEO D8 is not Pro Micro D8. Keep radio and external supply disconnected for these tests.'])
],y=y)

# Further chapters are appended below in reading order.

b.page('Measure the supply before interpreting a HIGH','A low output plateau led to a useful supply measurement',chapter='Use the meter deliberately')
b.cols([
 ('The observation and the follow-up',[
  'The first D9 HIGH plateau was about 4.35 V. That could have come from a low supply or from output/probe interpretation. The next discriminating measurement was VCC-to-GND at the board.',
  'You measured about <b>4.38 V</b>. That agreed with the output plateau and established a low rail. It did not establish whether the voltage drop was in the cable, host port or clone board power path.',
  'At 16 MHz the ATmega32U4 specified supply minimum is 4.5 V. A different cable/port was not available, and you explicitly chose to continue conditionally. We retained the supply qualification gap instead of calling that a firmware failure.']),
 ('How you would measure it',[
  'Set DC volts, math/relative off. Black lead in COM, red in the voltage jack. Put black on Arduino GND and red on VCC, not RAW. Read the value after it settles.',
  'Later, with the Grove attached, you reported about <b>4.5 V</b> both before and after enabling the backlight. That approximate reading is useful, but it gives little margin above the specified minimum.'])
],[
 ('What to record',[
  'Record the point measured, supply arrangement, display/backlight state, meter function, range or autorange, math state and units. A number with no measurement context is difficult to interpret later.',
  'A DMM gives a slow displayed voltage. It does not establish the minimum instantaneous rail during an EEPROM write, startup or backlight transition. A scope rail capture and a qualified power path would address that next.']),
 ('Do not change the power topology casually',[
  'We did not attach the KA3005P to USB-powered VCC or RAW. A controllable bench supply is useful for later power-cycle testing only after a single power path, current limit and backfeed behavior are established.',
  'Supply acceptance and digital behavior are separate claims. The observations remain valid at the measured rail; a passing functional test does not extend the MCU operating specification.'])
])

b.page('Identify the loose resistors with the meter','Five resistor checks supported the pull-up and series-resistor setup')
y=b.table(['Loose part','Settled mean','Nominal interpretation','Difference from nominal'],[
 ('First','10,016.205 ohms','10 kOhm','+0.162%'),('Second','10,075.412 ohms','10 kOhm','+0.754%'),
 ('Third','10,032.417 ohms','10 kOhm','+0.324%'),('Fourth','997.555 ohms','1 kOhm','-0.245%'),
 ('Fifth','99.8863 ohms','100 ohms','-0.114%')],36,516,720,[105,215,200,200],10)
b.cols([
 ('Procedure actually used',[
  '1. Confirm the isolated resistor is across the voltage/ohms and COM leads, with no external power. Check residual voltage in DCV before selecting resistance.',
  '2. Identify the function and math state. Select resistance/autorange, allow settling, then retain six polls rather than accepting the first displayed number.',
  '3. Restore DCV/autorange, rate S and math off afterward. Do not leave resistance mode selected when returning to a powered board.'])
],[
 ('Lessons from the readings',[
  'The first attempt included transient zeroes after a mode change. A later settled repeat established about 10 kOhm. Those initial zeroes were retained, not reclassified as a zero-ohm resistor.',
  'Nominal value is an interpretation of the settled magnitude; these readings do not independently establish the marked tolerance class. Several polls may repeat one displayed conversion.',
  'The meter can return a finite no-result sentinel near 9.9E37. Checking only whether a number is finite is insufficient. Function, units, settling and plausible range all matter.'])
],y=y)

b.page('Test the code before driving the board','The models exercised real modules, while retaining their physical limitations',chapter='Establish software and image identity')
b.cols([
 ('What the native tests covered',[
  'Control, debounce, interlock, presets, manual editing, TX latching, display behavior and the EEPROM journal were tested on the host. Coverage included 65,536 numerical inputs, 10,000 manual values, all 1,872 allowed tone values and 65,536 eight-event startup/input sequences.',
  'The actual tone.cpp ISR and setter ran against a host register model for all 1,872 settings. The worst nominal-clock frequency estimate error in that test was about 0.011875 Hz.',
  'Journal cases included 2,816 modeled torn-write scenarios. These tests explored corruption and commit ordering without wearing or power-cycling the physical EEPROM.']),
 ('Actual sketch integration',[
  'The unchanged .ino setup and loop were linked with actual control, tone, storage, journal and display modules. Host models replaced GPIO, USB, EEPROM and Wire boundaries.',
  'MSVC and Clang runs covered held inputs at boot, wraparound, absent LCD, no serial host, corrupted readback, display recovery, USB backpressure and upload-request release. Grove-specific cases were added after identifying the display.'])
],[
 ('What those passes do not establish',[
  'A model cannot qualify AVR instruction timing, interrupt deadlines, atomicity, real I2C faults, bootloader electrical behavior or a supply collapse during programming. Those are reasons to add physical tests, not reasons to discard useful model coverage.',
  'An AVR build checks compilation, linking and static RAM usage. It does not measure worst-case stack depth. Physical loaded-activity tests help, but do not turn the static RAM report into a stack measurement.']),
 ('How you would repeat the software gate',[
  'Run tools/test-firmware.ps1 in a configured C++ developer shell; retain the compiler version and output. Build AVR variants with tools/build-firmware.ps1. A build command does not implicitly flash.',
  'The explicit uint32 cast added to tone.cpp expressed an existing narrowing conversion for strict host compilation. All three earlier AVR HEX files stayed byte-identical. That was not a functional waveform correction.'])
])

b.page('Use USB replies as state evidence','115200 baud, newline commands, exact device identity and explicit units')
y=b.table(['STATUS field','How to read it','What it does not prove'],[
 ('bench=0 or 1','Production or bench command set','Source identity without a flashed-image comparison'),
 ('saved=1514 / active=1514','Tenths of hertz: 151.4 Hz','Actual measured output frequency'),
 ('tx=1 / bypass=1','Software TX command / qualified bypass state','Electrical D8 voltage or radio transmission'),
 ('armed=0','Release/new press interlock still required','A broken PTT input'),
 ('lcd=1','Driver initialized and communicating','Correct pixels or backlight appearance'),
 ('busy=1 / fault=0','Storage service active / no reported waveform fault','Power-loss endurance or absence of every fault'),
 ('loop_us / reset','Diagnostic maximum loop gap / post-bootloader reset byte','Pin latency / authoritative reset-cause history')],36,517,720,[138,300,282],9.5)
b.cols([
 ('Practical terminal workflow',[
  'Rediscover ports first. During this session the application was COM14, ST-Link COM5 and the meter COM15. Port numbers can change after reset/upload.',
  'With a terminal at 115200 and LF termination, send STATUS to the Arduino; send ID, STOP and STATUS to the fixture. Close other serial clients before using an automated runner. Normal operation does not use 1200 baud.'])
],[
 ('USB robustness actually exercised',[
  'Malformed and overlong lines, fragmented/CRLF commands, 200 consecutive STATUS requests, and recovery after 16 queued requests with a 0.5 s stalled reader passed.',
  'A separate concurrent test made 541 STATUS exchanges spanning the scope capture call; its retained 48 ms PWM window had no missing carrier periods. That is a specific finite traffic test, not coverage of every USB load.'])
],y=y)

b.page('From front panel readings to SCPI','Send only text before # in these examples  |  Comments explain replies and intent')
yl=b.section('The meter returns the current function',[
 'The XDM1251 used USB serial at 115200. Before interpreting MEAS1?, query the identity, function and math state. A bare scientific-notation value has no useful unit context by itself.'
],36,516,346)
yl=b.code(['*IDN?          # OWON,XDM1251,...,V1.0.1.0.4',
 'FUNC1?         # e.g. "VOLT" or "RES"',
 'CALC:FUNC?     # NONe when math is disabled',
 'RANGE?         # range text, including units',
 'MEAS1?         # e.g. +1.001582E+04',
 '', 'CONF:RES AUTO  # write only, isolated part only'],36,yl,346,8.3)
yl=b.p('In resistance mode that example means 10,015.82 ohms; in another mode the same numerical response would mean something else. The resistance unit text contains a UTF-8 ohm symbol, so an ASCII-only decoder failed on a range reply.',36,yl,346,10.4,14)
b.p('A setup command has no reply on this tested meter. Follow it with a state query rather than waiting for a response that will never arrive. After a mode change, allow settling; repeated polls may still show one displayed conversion. Meter commands here were never sent to arbitrary COM ports.',36,yl,346,10.4,14)
yr=b.section('The Rigol has a different USB interface',[
 'The scope used USBTMC through WinUSB, PyUSB and PyVISA-py, not a COM port. These are examples from the accepted setup sequence, not a replacement for its full cleanup and transfer logic.'
],410,516,346)
yr=b.code([':CHAN1:PROB 10',':ACQ:MDEP 600000',
 ':TRIG:EDG:SOUR CHAN1',':TRIG:EDG:SLOP NEG',
 ':TRIG:EDG:LEV 2',':SING',':TRIG:STAT?   # wait for STOP',
 ':WAV:MODE RAW',':WAV:FORM BYTE',':WAV:PRE?     # scaling and sample metadata'],410,yr,346,8.3)
yr=b.p('The waveform bytes are binary data, not newline-delimited text. The tested helper uses a 500-byte PyVISA chunk setting and waveform blocks of at most 250,000 samples, checking every returned length.',410,yr,346,10.4,14)
b.p('Arduino STATUS/SAVE/HANG and fixture ID/ARM/PTT commands are their own application protocols. They are not the meter or scope SCPI command set. Identify the device before choosing a command vocabulary.',410,yr,346,10.4,14)

b.page('Prove what image is on the device','A successful compilation and a matching STATUS string are not a flash comparison')
y=b.table(['Image or operation','Evidence actually obtained'],[
 ('Earlier display-disabled bench image','Read-only flash read matched all 11,470 application bytes named by the expected HEX; zero mismatch'),
 ('Grove bench image','15,118 application bytes programmed and verified; LCD online and visual home confirmed'),
 ('Grove production image left installed','14,260 application bytes programmed and verified; bench=0; SAVE and HANG rejected'),
 ('Clone bootloader discovery','Application USB 1B4F:9206; actual Caterina bootloader 2341:0036, observed on COM16'),
 ('What was not rewritten','No fuse or bootloader replacement was requested; upload operations did not request EEPROM programming')],36,517,720,[240,480],10)
b.cols([
 ('A useful discovery failure',[
  'The first readback attempt expected the bootloader to use SparkFun USB identity. It did not, so that attempt stopped before invoking avrdude. Observing the newly enumerated Caterina device resolved the incorrect assumption.',
  'The earlier read returned 32,730 bytes after erased trailing bytes were trimmed. The comparison covered the 11,470 application bytes specified by that HEX, not a verified source image for every bootloader byte.'])
],[
 ('Record the identity you can reproduce',[
  'Keep the build flags, tool versions, HEX hash, upload/readback log and the actual device signature. A file hash identifies bytes; the flash verification connects those bytes to the board.',
  'The final Grove production HEX SHA256 is printed in the final-results chapter. Firmware updates changed which evidence applied; older display-disabled captures remained historical, not validation of the later image.'])
],y=y)

b.page('Set up the scope to answer the question','Front-panel equivalents for settings we actually applied through SCPI',chapter='Read the oscilloscope')
b.cols([
 ('Start with a readable voltage view',[
  'Connect probe grounds to Arduino GND before interpreting a waveform. Set the physical probe switches and channel Probe settings to x10. Use DC coupling, 1 V/div and a vertical position that keeps both LOW and HIGH visible.',
  'For the PTT captures we used offsets near -2.5 V, Normal acquisition, bandwidth limit off and no inversion. An offset changes where zero appears; it is not subtraction of 2.5 V from the circuit.',
  'With CH1 and CH2 enabled, select 10 ms/div and 600 kpoints for a 120 ms record. Confirm the actual sample interval from the exported preamble.']),
 ('Front-panel sequence you can use',[
  'Press CH1 or CH2 to set each channel, including Probe and coupling. Use the vertical SCALE/POSITION and horizontal SCALE/POSITION controls to obtain the listed values.',
  'In the trigger menu choose Edge, the intended source channel, the required slope and the listed level. Press SINGLE, wait for it to arm, then apply the stimulus. After capture, confirm STOP before comparing the two channels.'])
],[
 ('Trigger on cause or on effect deliberately',[
  '<b>PTT press:</b> CH1 D7, falling edge, 2 V. <b>PTT release:</b> CH1 D7, rising edge, 2 V. <b>Bypass:</b> CH1 D10 with the corresponding edge.',
  '<b>Watchdog:</b> CH2 D8 falling, 2 V, 500 ms/div. This positions the actual output release in the record. A pre-HANG marker supplies a conservative reference on CH1.',
  'Normal/Single waits for a real event. AUTO or a forced trigger can produce a screen without proving that the intended event occurred. We rejected timeouts instead of forcing a pass.']),
 ('Use cursors as a first calculation',[
  'In Cursor manual mode, use time cursors to align A with the input threshold crossing and B with the output crossing; read the horizontal difference. At 10 ms/div, a half division is about 5 ms.',
  'The retained-data evaluator makes the more precise calculation, checks every transition and verifies sample alignment. Hand cursors are useful for understanding and independent sanity checking; pixel positions do not give the full stored-sample precision.'])
])

b.screen('Read the idle PWM screen','idle-pwm/scope.png',[
 'H 2.00 ms is the horizontal time per division. This is a broad view of many fast pulses.',
 'The upper readouts show 25.0 MSa/s and 1.20 Mpts for this screen state. Export metadata identifies the retained record.',
 'The HIGH plateau is near 4.35 V. Later VCC measurement near 4.38 V explains it.',
 'The lower plateau is near ground; the channel scale is 1.00 V/div with x10 interpretation.'
],
 'The yellow band is a 10 kHz rectangular waveform, not a 151.4 Hz analog sine. In the accepted idle RAW record, frequency was 9,999.7573 Hz, duty 50.04-50.08%, LOW about 0.051 V and HIGH about 4.353 V.',
 'This early screenshot was obtained after acquisition resumed. Use the saved preamble and samples for exact record dimensions; do not treat a later live screen as the identity of the stopped RAW buffer.',
 [((171,17),(171,-14)),((236,17),(276,-14)),((228,146),(430,98)),((222,359),(430,285))])

b.page('Calculate from samples rather than screen pixels','Sampling rate, record length and PWM duty answer different questions')
y=b.table(['Retained record','Samples and interval','Actual stored duration','Purpose'],[
 ('Early idle PWM','1,200,000 at 40 ns','48 ms','Carrier and midpoint check'),
 ('Paired PTT / bypass','600,000 per channel at 200 ns','120 ms','Fast input/output response'),
 ('Watchdog / mixed stress','600,000 per channel at 10 us','6 s','Longer event windows'),
 ('Long encoded-tone record','12,000,000 at 500 ns','6 s','Independent tone estimate')],36,516,720,[188,218,142,172],9.7)
b.cols([
 ('Three basic calculations',[
  '<b>Record duration = N times sample interval.</b> Thus 600,000 times 200 ns = 0.120 s. The advertised maximum sample rate is not automatically the rate used in a slow, deep capture.',
  '<b>Carrier frequency = 1 / period.</b> A 100 us period is 10,000 Hz. <b>Duty = HIGH time / period.</b> A 50 us HIGH in a 100 us period is 50%.',
  'In a 500 ns record, a 100 us carrier cycle has about 200 samples. This resolves its changing pulse width while a six-second record supplies many slow tone cycles.'])
],[
 ('Use the returned scaling',[
  'The saved BYTE data are ADC codes. Voltage = (code - yorigin - yreference) times yincrement. Time = (sample index - xreference) times xincrement + xorigin.',
  'For paired channels, compare N, xincrement, xorigin and xreference. Two separately acquired traces are not interchangeable with channels from one stopped acquisition.',
  'Smallest sample interval is resolution, not calibrated accuracy. A two-edge sample bound is about twice the interval: 0.4 us for the 200 ns records, 20 us for the mixed-stress records. Probe and timebase uncertainty remain additional.'])
],y=y)

b.page('Operate the NUCLEO as a repeatable switch','Fixture commands stimulate physical Arduino inputs; they do not bypass the control logic')
b.cols([
 ('The command sequence',[
  'Send ID and verify STANDIN1 / NUCLEO-F767ZI. Send STOP, then STATUS and require armed=0, drive=0 before Arduino power or before changing a test.',
  'ARM releases all drives and starts the five-second lease. PTT 1, BYPASS 1 or BUTTON 1 closes the corresponding contact. A value of 0 releases it. ENCA and ENCB use the same convention.',
  'The driver must receive commands within the lease. Automated runners refresh STATUS during long captures and verify the drive mask has not changed. Do not defeat the lease to make a manual test easier.']),
 ('Decode the drive mask',[
  'Bits are PTT=1, bypass=2, button=4, encoder A=8 and encoder B=16. For example drive=3 means PTT and bypass are asserted. This is commanded fixture state, not independent measurement of the Arduino input voltage.',
  'The NUCLEO has a watchdog as well. Neither closing a serial port nor issuing STOP alone proves the ending state; we requested STATUS and checked the returned mask.'])
],[
 ('Manual operation and automation have different jobs',[
  'A person can start with ARM, PTT 1 and PTT 0 and inspect the scope. That is a useful first functional check. It is poor evidence for precise contact-bounce timing or hundreds of repeatable transitions.',
  'Our fixture generated eight approximately 1 ms toggles for the bounce experiment. The scope observed the resulting edges. Scheduler lateness was checked separately; host typing speed was not used as the input timing reference.']),
 ('A practical manual capture',[
  '1. Configure and arm the scope on the released input. 2. ARM the fixture and assert PTT. 3. Confirm the scope stops. 4. Read the delay and inspect both traces. 5. Release PTT and STOP/read back the fixture.',
  'For a long capture, use the maintained runner so it refreshes the lease. If acquisition or communications fail, release inputs first, retain the failure and restore known settings before trying again.'])
])

b.page('Measure PTT response from the real edges','CH1 D7 input and CH2 D8 output, both x10',chapter='Measure timing and recovery')
b.cols([
 ('Prepare one press',[
  'Released baseline: D7 HIGH and D8 LOW. Set both channels to DC, 1 V/div; use 10 ms/div, 600 kpoints, Edge trigger CH1 falling at 2 V.',
  'Arm SINGLE before the press and allow arming to settle. The accepted runner waited 0.8 s. Apply the physical input through the F767, then require a completed STOP acquisition.',
  'Read both channels from that same stopped buffer. The evaluator rejects missing or extra edges and checks that the output transition follows the input within 25 ms.']),
 ('Prepare one release',[
  'Start with PTT held, so D7 is LOW and D8 HIGH. Change the trigger to CH1 rising, still at 2 V. Arm, release the contact, then measure D8 falling.',
  'It is not enough to test only assertion. Release latency, extra pulses and operation with bypass enabled are separate observable behaviors.'])
],[
 ('Interpret the actual results',[
  'The early display-disabled baseline had 12 edges at 4.3706-5.1580 ms. Save-active cases reached 5.2060 ms. The later Grove bench tests and production tests used their own image identities and records.',
  'On the final production image, all 12 measured press/release edges passed at 3.7508-5.1478 ms. The 25 ms limit leaves substantial observed margin, but only the retained windows support a no-extra-pulse claim.']),
 ('Do not substitute software timestamps',[
  'USB tx=1 tells you that the software requested transmit. It does not timestamp the physical D8 edge. The independent measurement is the difference between observed input and output crossings.',
  'D8 had only the x10 scope load. Its ability to control the actual Q1/transistor and radio load belongs to carrier integration testing. LED pin agreement was modeled but not independently timed on this two-channel setup.'])
])

b.screen('Read a captured PTT press','ptt-electrical/baseline/bypass-0-pair-1-press/scope.png',[
 'STOP means the displayed acquisition is stationary while we compare the two channels.',
 '10.0 ms/div, 5.00 MSa/s and 600 kpts match the fast paired-capture setup.',
 'Yellow D7 falls: the active-LOW microphone contact is asserted. Use its crossing as the cause.',
 'Cyan D8 rises about half a division later. The saved-data result for this example is 5.0654 ms.'
],
 'This is the early display-disabled bench example. Both channels share one acquisition. The screenshot gives an immediate scale check; the numeric result comes from the retained 200 ns samples.',
 'At 10 ms/div, roughly 0.5 division is about 5 ms, comfortably below 25 ms. The Vavg numbers at the bottom average changing signals; they are not the HIGH and LOW plateau voltages.',
 [((107,17),(105,-14)),((203,17),(250,-14)),((385,242),(308,241)),((410,251),(494,278))])

b.screen('Read a captured PTT release','ptt-electrical/baseline/bypass-0-pair-1-release/scope.png',[
 'The timebase is unchanged, making the release comparable with the press example.',
 'Trigger is on the D7 rising edge at 2 V for this case. A rising input means contact release.',
 'Yellow D7 returns HIGH. The fixture has released the active-LOW contact.',
 'Cyan D8 falls after the input. Retained samples measure 4.4584 ms for this example.'
],
 'A correct press trace does not establish correct release. Here the expected polarities reverse: D7 rises and D8 falls, with exactly one transition of each in the window.',
 'A brief unwanted second D8 rise would fail even if the first fall were fast enough. Always inspect the whole record, not just the first plausible edge.',
 [((170,17),(170,-14)),((736,17),(737,-14)),((385,240),(310,240)),((409,250),(490,279))])

b.page('Stress debounce and background saves','The acceptance criterion includes the interaction, not only a quiet idle loop')
b.cols([
 ('Make a save visibly active',[
  'On a bench image, issue SAVE with another valid tone and immediately poll STATUS until busy=1 is observed. The next physical edge must be applied while that observed save activity is still relevant; completion is checked afterward.',
  'The runner alternated 100.0 and 151.4 Hz, verified durable completion and restored the original selection. Power was not interrupted, so this is not a torn-write electrical test.',
  'With the Grove enabled, 12 save-active PTT edges passed with a worst delay of 5.3574 ms. The production image rejects the SAVE command; production settings are changed through the UI instead.']),
 ('Give bounce a defined shape',[
  'The fixture generated eight 1 ms toggles ending in the intended stable state. This produces nine observed input transitions when the first assertion or release is included.',
  'The required result is one appropriate D8 transition, timed from the <b>last stable input edge</b>. Measuring from the first bounce edge would answer a different question.'])
],[
 ('Read every edge',[
  'In the illustrated early bounce-plus-save case, D7 has nine transitions but D8 changes once, 5.3622 ms after the final stable edge. All four tested bounce cases passed.',
  'The evaluator checks approximately 0.8-1.2 ms spacing for this selected 1 ms pattern. A single successful pattern does not establish the exact rejection boundary for every real switch or encoder.']),
 ('Know the current evidence boundary',[
  'USB parser and stalled-reader tests exercised another background load. Later UI/PTT stress added actual display work and simulated encoder motion. Different loads answer different concurrency questions.',
  'No trace proves behavior in unobserved time between records. Pair bounded, repeatable captures with a longer soak when that additional confidence is worth the test time.'])
])

b.screen('Read the contact bounce screen','ptt-electrical/bounce-save/bypass-0-pair-1-press/scope.png',[
 '10 ms/div lets the group of short input disturbances fit around the trigger.',
 'The yellow group contains the programmed bounce. Zoomed RAW data confirm nine input transitions.',
 'The last D7 fall is the start of the stable asserted state, about 8.012 ms into the plotted raw time axis.',
 'D8 rises only once, about 13.3742 ms on that axis. Their difference is 5.3622 ms.'
],
 'The upper readout and the visible group provide orientation. Count and spacing come from the saved samples, not from trying to count compressed pixels on the screen.',
 'The debounce delay begins again when the candidate input changes. Use the final stable edge for the specified latency, and separately require no unwanted output response to the earlier bounces.',
 [((171,17),(171,-14)),((402,238),(323,204)),((424,239),(482,220)),((450,250),(532,281))])

b.plot('Measure the stable interval after bounce','ptt-electrical/bounce-with-save.png',[
 '<b>Blue</b> is the actual D7 input. The short disturbances occupy roughly the first 8 ms.',
 '<b>Orange</b> is D8. It remains LOW during the disturbances and changes once after the final stable edge.',
 '<b>5.3622 ms</b> is the difference between the two vertical references. This is digital PTT response, not radio RF timing.'
],
 'This enlarged analysis plot is reconstructed from the same retained raw samples. Its axes make the final stable edge and single output transition easier to evaluate than the compressed screen picture.')

b.page('Measure watchdog release rather than USB recovery','A physical marker supplied an upper bound when HANG had no electrical timestamp')
b.cols([
 ('The experiment',[
  'Key PTT and keep the physical D7 input held. Configure 500 ms/div and 600 kpoints, with CH2 D8 falling at 2 V as the real trigger. Fill about 3.5 s of prehistory while refreshing the fixture lease.',
  'Before HANG, generate four 1 ms release pulses on D7. They are too short for the tested qualification path to unkey the already held TX. Confirm TX is still active, then send HANG on the bench image.',
  'Wait for D8 to fall and keep D7 held through reset. Require no D8 rekey in the captured post-release interval, then verify armed=0, tx=0 after USB recovery. Release and make a new press to show normal operation can resume.']),
 ('Why the reference is an upper bound',[
  'The last physical marker fall happened before the host sent HANG. The interval from that marker to D8 LOW includes host/USB delay before HANG execution, so it bounds release conservatively. It is not an exact timestamp of entering the infinite loop.'])
],[
 ('Measured results',[
  'Early bench bounds were 328.58 ms with bypass off and 326.72 ms with bypass on. The Grove bench image gave 327.07 and 327.94 ms. All met the one-second target.',
  'D8 stayed LOW for about three seconds of observed held-input time after release in each electrical record. A separate held-reset check also observed suppressed D9 midpoint PWM and the required release/new-press interlock.']),
 ('USB is a second observation',[
  'Disappearance and re-enumeration show reset/recovery, but their duration includes the bootloader and host. The earlier roughly 0.84-0.92 s USB times were not substituted for D8 release latency.',
  'These were intentional bench HANG tests. The final production image does not accept HANG. No cold power cut, supply collapse or loaded radio PTT release was qualified by them.'])
])

b.screen('Read the electrical watchdog capture','ptt-electrical/watchdog/watchdog-bypass-0/scope.png',[
 '500 ms/div is 50 times slower than the PTT-edge setup. The six-second record uses 100 kSa/s.',
 'Trigger source 2 is D8, falling at 2 V. Its actual release is centered near the trigger position.',
 'The yellow pre-HANG marker is compressed here. Four 1 ms pulses cannot be counted reliably at this scale.',
 'Cyan D8 falls and remains LOW to the right while D7 stays held. Retained samples establish the no-rekey window.'
],
 'In this bypass-off example, the measured marker-to-release bound is 328.58 ms, with 3.00004 s of held input observed afterward. D8 is only scope-loaded.',
 'Do not use the average readouts as static levels. Do not label the marker as the exact instant the firmware entered HANG. A zoom of the RAW data verifies the short marker pulses.',
 [((170,17),(169,-14)),((735,17),(735,-14)),((351,235),(281,263)),((385,247),(488,250))])

b.page('Recover a slow tone from fast PWM','D9 voltage amplitude stays digital while its pulse width carries the sine',chapter='Understand PWM and bypass')
b.cols([
 ('Two frequencies share one signal',[
  'D9 switches at a nominal 10 kHz carrier, about 100 us per cycle. The selected tone changes its duty over many carrier cycles. At 151.4 Hz, a tone period is about 6.605 ms, containing roughly 66 carrier cycles.',
  'The digital HIGH remains near VCC and LOW near GND. The slow sine is encoded in pulse width, not in a slowly varying pin-voltage amplitude. A broad raw pulse band is therefore expected.',
  'Idle and bypass hold PWM near 50% duty. The carrier keeps running. They do not command a static zero-volt pin. The analog reconstruction and coupling network later turns the modulation into the intended audio signal.']),
 ('What we measured independently',[
  'For each carrier cycle, find the rising edge, falling edge and next rise. Compute HIGH time / period, then look for consistent upward crossings of midpoint duty.',
  'The estimator uses hysteresis around duty crossing and interpolation between samples. Many crossings over six seconds estimate the encoded tone without calling the firmware sine-table generator.'])
],[
 ('Check carrier integrity before accepting frequency',[
  'A plausible slow estimate is not enough. We required all complete carrier periods to be 98-102 us, no missing falling edges, duties within selected 11-89% bounds, and modulation reaching both selected extremes.',
  'The long captures used 12 million samples at 500 ns each. In the final production record, 59,998 complete periods and 908 tone crossings supported an estimate of 151.39628797 Hz.']),
 ('Separate resolution and reference uncertainty',[
  'All reported tone errors passed the selected +/-0.1 Hz check on the nominal scope timebase. Absolute calibrated reference accuracy was not established, so the numbers are observations with that qualification.',
  'These records do not measure filtered amplitude, distortion, carrier residue, keying clicks or radio deviation. A successful digital duty estimator cannot certify the analog network.'])
])

b.plot('See the transmission latch in the pulse widths','nucleo-minimal/ptt-bypass-duty.png',[
 '<b>Top left and right:</b> keying creates changing duty; bypass fixes the duty near 50%. The carrier still runs.',
 '<b>Bottom left:</b> saving 100.0 Hz during a 151.4 Hz transmission does not retune that transmission when bypass is released.',
 '<b>Bottom right:</b> release and make a fresh PTT press. The new transmission uses the saved 100.0 Hz selection.'
],
 'Each modulated source record is six seconds long. The plot shows short excerpts for readability. Earlier bench estimates were 151.396592 Hz, resumed 151.396642 Hz and then 99.997720 Hz; endpoints measured 66.998483 and 254.093936 Hz.')

b.page('Measure bypass by the input and the duty response','CH1 D10 and CH2 D9, with the real PTT held')
b.cols([
 ('Procedure',[
  '1. With power off, move tips to D10 and D9; retain common grounds and x10 settings. Reconnect NUCLEO first, then Arduino. Verify idle, arm the fixture and hold PTT.',
  '2. Use 10 ms/div and 600 kpoints, Edge trigger CH1 at 2 V. Falling D10 enables bypass; rising D10 disables it. Arm before each change.',
  '3. Read both raw channels from one stopped acquisition. Require the intended single D10 edge, continuous PWM, no clipping and the expected initial/final duty behavior.']),
 ('Define the metrics before reading them',[
  '<b>Suppression:</b> duty enters 49.5-50.5% and stays there for the remaining record, with at least 10 ms confirmation.',
  '<b>Return onset:</b> modulation begins again. <b>Additional span check:</b> duty has reached both 20% and 80% thresholds. This is not the instant exact nominal 12.5/87.5% peaks first occur.'])
],[
 ('Measured production results',[
  'Six ordinary transitions passed: midpoint settling no later than 10.2598 ms, modulation onset no later than 5.3940 ms, and the selected 20-80% span no later than 13.9942 ms.',
  'A further pair with the Arduino COM client closed passed at 9.3902 ms settling and 5.0488 ms onset. Each record had 1,199 complete carrier periods with no missing period detected.']),
 ('What this does and does not prove',[
  'During ordinary captures USB tx stayed asserted across bypass. The two scope channels did not simultaneously observe D8 in this configuration. Closed-port captures have no in-capture Arduino STATUS at all; the D9 records establish actual modulation behavior.',
  'Analog filter decay can add response after the PWM changes. Our digital timing excludes it. A new filter or radio load needs its own integrated measurement.'])
])

b.screen('Why the raw bypass band is hard to read','grove-ui/production/bypass-baseline/pair-1-enable-bypass/scope.bmp',[
 'STOP is useful, but a raw screen still compresses many carrier cycles into a few pixels.',
 '10 ms/div with 5 MSa/s and 600 kpoints gives the 120 ms paired record used for evaluation.',
 'Cyan D9 still switches across nearly the same voltage range at 50% duty. The broad band does not disappear in bypass.',
 'Yellow CH1 is D10 here, not D7. The trigger source/slope refers to bypass; dense cyan rendering obscures much of the yellow trace.'
],
 'The ordinary enable/release screenshots look very similar at this scale. They are orientation pictures; the raw input edge and decoded pulse widths carry the numerical suppression/resumption evidence.',
 'A voltage average near half VCC can occur both with balanced tone modulation and with 50% midpoint PWM. Do not use Vavg or the band height alone to decide whether the tone is enabled.',
 [((107,17),(105,-14)),((207,17),(260,-14)),((330,246),(460,250)),((738,17),(737,-14))])

b.page('Add the actual display without changing the test question','The identified Grove needed its own protocol, while the UI layout stayed the same',chapter='Exercise the real UI')
b.cols([
 ('Identify before connecting',[
  'The 1602A marking described a character display, not an I2C interface. A and K normally identify backlight terminals; those extra contacts were not treated as SDA/SCL. The GME12864-12 was considered but not used.',
  'You then identified a Grove-LCD V4.0 with GND, VCC, SDA and SCL. That was a useful 16x2 I2C candidate, but not a drop-in PCF8574 protocol match.']),
 ('The actual Grove setup',[
  'Grove GND to Arduino GND; VCC to Arduino VCC; SDA to D2; SCL to D3. The driver uses LCD address 0x3E and backlight address 0x62 for V4.',
  'The added build option is -GroveV4. Setting only a different address on the PCF8574 driver would not work. The Grove path sends direct LCD command/data bytes and initializes its backlight controller.'])
],[
 ('Keep PTT responsive during display work',[
  'The driver uses a timed state machine with at most one I2C transaction per service call and a 1.5 ms Wire timeout. The main loop services PTT between transactions.',
  'We used a modest white backlight selection of 64/255 per channel. That is a selected bench default, not a measured brightness or current budget.']),
 ('Corroborate software with your eyes',[
  'Before the Grove upload the display was dark. After verified upload, lcd=1 and you confirmed Tone 151.4 Hz / RX Tone enabled. Supply readings before and after enabling the backlight were about 4.5 V.',
  'No LCD photograph was captured. Text examples in this guide transcribe your confirmations; they are not screen photographs. Communication success alone does not prove correct pixels.'])
])

b.page('Use a simulated EC11 to test repeatable gestures','The real bare EC11 was not connected; A, B and button contacts were emulated')
y=b.table(['Gesture or sequence','What we did physically','What we checked'],[
 ('One positive detent','AB 11 -> 01 -> 00 -> 10 -> 11','Presets menu moved to Manual'),
 ('One reverse detent and Select','Inverse four-transition path; short button press','Preset 151.4 Hz / Press=Save'),
 ('Short / long press','120 ms / 950 ms commanded closures','Short actions, long save and no extra short action on release'),
 ('Preset save and restore','151.4 -> 156.7 -> 151.4 Hz through controls','Saved value changed only on explicit save'),
 ('Four manual digits','1514 -> 2514 -> 2414 -> 2424 -> 2425; long press','242.5 Hz saved; inverse edits restored 151.4 Hz'),
 ('Cancel and invalid range','Edit, select Cancel and hold; later attempt 351.4 Hz','Cancel kept 151.4; invalid save rejected with range text')],36,516,720,[145,325,250],9.6)
b.cols([
 ('Run one gesture carefully',[
  'tools/exercise-ui-input.py sends one short, long, forward or reverse action and then STOPs/readbacks the fixture. Establish the current screen first: the same button action can browse, save or cancel depending on context.',
  'The individual-detent tool pauses 50 ms between states. Mixed stress used shorter selected host pauses. Those pauses are not measured electrical encoder-edge timestamps.'])
],[
 ('What remains for the actual EC11',[
  'Simulation made repeatable quadrature and button tests possible. It did not establish the real part\'s pin order, rotation direction, transitions per detent, bounce or mechanical feel.',
  'Connect and qualify the real encoder during integration. The firmware currently selects four transitions per detent and direction +1; a different EC11 variant can require a different setting.'])
],y=y)

b.page('A failed count check taught us about save gating','Keep the evidence and challenge the test oracle before changing the firmware')
b.cols([
 ('The mixed experiment',[
  'Ten batches each contained eight PTT press/release pairs with preset browsing. Bypass alternated, and two background saves occurred while TX was held. The scope retained every D7/D8 edge within each six-second window.',
  'A final physical UI save compared the browsed preset against an independent count. Starting at the 151.4 Hz preset, 80 forward detents including wrap should end at 77.0 Hz.']),
 ('Run A failed the count expectation',[
  'All 160 PTT transitions passed, but the final save was 71.9 Hz. That corresponds to 78 accepted detents. The test had begun two detents immediately after observing busy=1, one during each save.',
  'The actual sketch deliberately gates UI editing while storage is busy. Losing those two counted edits is consistent with that rule. The bracketing USB polls did not directly timestamp each final encoder edge, so the explanation is a supported inference, not a per-edge electrical proof.'])
],[
 ('Correct the experiment, not the acceptance limit',[
  'Run B kept PTT held through each background save and checked the old tone remained latched. It waited for observed busy=0 before issuing a detent counted by the final oracle.',
  'Now all <b>80 counted detents</b> ended at the expected <b>77.0 Hz</b>. All <b>160 PTT transitions</b> passed at 3.39-5.39 ms. The original 151.4 Hz was restored.',
  'No firmware correction or relaxed 25 ms criterion was needed. Run A and its exact source snapshot remain archived beside the accepted run.']),
 ('Do not overstate the campaign',[
  'Ten six-second windows provide 60 seconds of captured time, separated by transfer/setup gaps. This is a useful mixed-activity campaign, not a continuous one-hour soak or a frequency measurement at all 50 presets.'])
])

b.plot('Evaluate every edge in the mixed record','grove-ui/mixed-stress/mixed-ptt.png',[
 '<b>Top:</b> each dot is one physical input-to-output delay. Both bypass states remain far below the red 25 ms limit.',
 '<b>Bottom:</b> a complete batch contains eight key/release pairs. Every D7 transition is matched with one D8 transition.',
 '<b>Window:</b> 600 kpoints per channel at 10 us/sample. Fine enough for the 25 ms question; not a D9 carrier-integrity test.'
],
 'The accepted run B combines physical keying, real LCD work, counted preset browsing and held-TX saves. The independent detent oracle verifies final selection, while the scope evaluates PTT edges.')

b.page('Leave and test the production configuration','Bench diagnostics are useful test tools; they must not be mistaken for the final command set',chapter='Finish on the intended image')
b.cols([
 ('What changed on the board',[
  'After bench testing, the Grove production image was built without -Bench, uploaded and verified. All 14,260 application bytes compared successfully. Static RAM use was 1,370 bytes, leaving 1,190 bytes before stack/local use.',
  'STATUS reported bench=0, lcd=1, saved/active=1514 and idle healthy state. After checking bench=0, SAVE 1000 and HANG both returned ERR command. The saved value did not change and HANG did not reset the production application.',
  'We repeated physical UI save to 156.7 Hz and restore to 151.4 Hz. That uses the production UI, not the disabled USB SAVE path.']),
 ('Final image identity',[
  'Grove V4 production HEX SHA256:'])
],[
 ('Repeat the behavior that matters',[
  'Twelve production PTT transitions passed at 3.7508-5.1478 ms. Eight production bypass transitions passed, including a serial-port-closed pair. The six-second encoded-tone capture also passed with COM closed.',
  'The final scope record estimated 151.39628797 Hz for 151.4 Hz, carrier 9,999.75833 Hz, duty 12.5-88.0% and 59,998 complete carrier periods. No missing period was detected in that record.']),
 ('What closed serial really means',[
  'The Arduino COM client was closed before keying and throughout capture, then reopened for cleanup status. The scope independently observed PWM operation; the F767 lease stayed active.',
  'USB remained physically connected to the computer. This addresses dependence on an open terminal/client. It does not establish operation with USB data electrically detached or a different power source.'])
])
b.code('cbdd81b59ab4645b21e01b0dddfd0898f1fc502f9de407f76f385aabcf86deee',36,267,346,7.8)
b.p('Do not confuse HEX byte count with the text file size. The programmer verifies application addresses represented by the HEX. EEPROM programming and fuse/bootloader changes were not requested by these uploads.',36,217,346,9.8,13)

b.screen('When the screenshot is not the waveform evidence','grove-ui/production/tone-current-serial-closed/current-tone-1514/scope.bmp',[
 'RUN shows sampling had resumed when this picture was taken. It is not the retained STOP-buffer image.',
 'The display has no usable trace at this instant. Do not annotate an imaginary sine into the empty grid.',
 'The screen reports 2.00 MSa/s and 12.0 Mpts. The saved preamble and returned 12 million bytes identify the actual accepted record.',
 'CH2 is the D9 probe here. Its Vavg readout is not the selected tone frequency.'
],
 'The associated raw record was complete and passed independent duty decoding: 151.39628797 Hz, 59,998 complete carrier periods and no missing period detected. Several earlier long-tone screenshots had the same post-resume limitation.',
 'A blank or later screenshot is inconclusive as a waveform picture. The accepted numerical claim must come from the complete raw record, scaling, checks and restoration report. A good screenshot would additionally be taken from the intended stopped buffer after the display refreshes.',
 [((106,17),(105,-14)),((385,242),(500,242)),((235,17),(270,-14)),((165,465),(248,406))])

b.page('Read the production tone in the saved samples','Detail from a retained analysis plot  |  The empty live screen is not used as the waveform')
path=BASE/'grove-ui/production/production-bypass-tone.png'
with PILImage.open(path) as im:iw,ih=im.size
# Show the lower plot by clipping the PDF image; source raster is unchanged.
left,top,right,bottom=0,930,iw,ih
scale=720/(right-left);crop_h=(bottom-top)*scale;xx,yy=36,516-crop_h
b.c.saveState();clip=b.c.beginPath();clip.rect(xx,yy,720,crop_h);b.c.clipPath(clip,stroke=0)
b.image(path,xx-left*scale,yy-(ih-bottom)*scale,iw*scale,ih*scale);b.c.restoreState()
y=b.p('This is the lower panel of the production analysis figure, cropped only for page readability. Each point comes from one complete D9 carrier cycle. The plot shows 80 ms of a six-second record; it is duty percentage, not analog output volts.',36,yy-12,720,10.4,14)
b.cols([
 ('From sanity check to numerical estimate',[
  'About twelve slow cycles fit in 80 ms, putting the tone near 150 Hz. The selected 151.4 Hz period is about 6.605 ms. This checks scale and distinguishes tone from carrier; it does not establish +/-0.1 Hz accuracy.',
  'The decoder found 908 upward midpoint crossings: 907 complete intervals divided by the actual first-to-last crossing time. Dividing 908 by the nominal six seconds would include partial-cycle bias.'])
],[
 ('Accept the data without overstating precision',[
  'The estimate was 151.39628797 Hz, an error of -0.00371203 Hz on the nominal scope reference. Those digits describe the calculation, not calibrated accuracy to eight decimal places.',
  'The same buffer has 59,998 complete carrier periods, bounded duty/period values and no missing period detected. It was re-evaluated from retained bytes. Arduino COM was closed while the F767 held PTT; the previous RUN screenshot alone proves none of this.'])
],y=y)

b.page('The final measurements and their boundaries','Use this table when deciding what to test next')
y=b.table(['Layer and configuration','Evidence obtained','Remaining boundary'],[
 ('Host models and actual sketch','Exhaustive values/sequences; real modules under MSVC and Clang','Not AVR instruction timing or physical peripheral faults'),
 ('Early display-disabled bench','Tone/latch/endpoints; 28 PTT edges; watchdog and bypass records','Earlier image and about 4.38 V rail'),
 ('Grove bench','UI, four digits, Cancel, invalid range; 28 PTT edges; watchdog; 80-pair mixed run','Physical EC11 and display-bus faults not run'),
 ('Grove production','Verified image; disabled bench commands; UI save/restore; 12 PTT and eight bypass edges','Selected finite windows, not all loads or a long soak'),
 ('Production closed-port tone','6 s, 12 Mpoints, 151.3963 Hz and continuous observed carrier','Nominal scope reference; no analog audio/RF measurement')],36,516,720,[175,315,230],9.5)
b.cols([
 ('What we can reasonably conclude',[
  'The digital firmware is a strong candidate for staged carrier integration. We have complementary software, protocol, pin, UI and production-image evidence instead of one successful demonstration.',
  'The final state was 151.4 Hz, correct home display confirmed by you, PTT released, no fault and fixture disarmed. The production image remains installed.'])
],[
 ('What we cannot conclude yet',[
  'We have not qualified the loaded transistor/PTT path, reconstruction filter, microphone interaction, audio distortion or radio deviation. The approximately 4.5 V rail has not been margin-qualified.',
  'A particular finite capture cannot guarantee absence of every future glitch. More test time adds evidence within a defined envelope; it does not create an unlimited guarantee.'])
],y=y)

b.page('Treat acquisition problems as experiments too','Preserve the failed attempt and change one demonstrated cause',chapter='Troubleshoot the measurement')
b.cols([
 ('No trigger or unexpected depth',[
  'The early captures hit timeouts and a memory-depth mismatch. Channel-enable changes alter valid depth choices asynchronously. The corrected sequence waited for channel configuration, read it back, then selected and verified depth.',
  'For PTT, a longer 0.8 s one-shot arming wait resolved a missed event. A timed-out test stayed unaccepted; it was not converted into a forced-trigger pass.']),
 ('A setting changed while restoring another',[
  'Changing channel offset/scale can move the trigger level. Restoring the old level first and then moving the channel left a different effective level.',
  'The fix applies/restores channel settings before trigger level, and verifies readback. It does not assume that writing the right SCPI strings necessarily produced the desired final settings.'])
],[
 ('An unnecessary STOP changed single-shot state',[
  'One captured event was rejected because another STOP on an already stopped single acquisition changed sweep behavior to AUTO. That could undermine reading two channels from the same buffer.',
  'The helper now queries state first and avoids a redundant STOP/RUN. Offline checks cover already-running and already-stopped cases. Accepted dual-channel runs confirm STOP between channel reads.']),
 ('Transport details are not DUT defects',[
  'A missing pyserial dependency prevented one concurrent test from starting. A project-local environment resolved it. No stimulus or accepted data resulted from that failed start.',
  'The USB helper uses the tested 500-byte PyVISA chunk setting and bounded waveform blocks. RAW binary data are not newline-delimited text. Incomplete transfers, no-result meter sentinels and malformed data must be rejected before evaluating firmware.'])
])

b.page('Keep a bench record you can trust later','The saved files make the reasoning repeatable')
b.cols([
 ('Minimum record for one accepted test',[
  'Record date, DUT/image configuration, physical wiring and probe ratio, instrument identity, channel settings, trigger source/slope/level, sample count/interval, stimulus, acceptance and observed result.',
  'Keep the original raw bytes and preamble, not only a picture. Preserve commands/status and source hashes where automation is involved. Record final release and restored settings explicitly.',
  'Use a new output directory for every run. The maintained tools refuse overwriting a previous run so an unsuccessful experiment cannot silently replace the accepted evidence.']),
 ('The data bundle',[
  '<b>waveform.u8 or .u8.gz:</b> unsigned BYTE samples, gzip lossless where used. <b>capture.json:</b> scaling and point metadata. <b>measurement.json:</b> evaluator result. <b>result.json:</b> whole run, identities, transcripts and cleanup.',
  '<b>manifest.json:</b> file and raw-buffer SHA256 values. <b>sources:</b> snapshots tied to the actual run. <b>scope PNG/BMP:</b> screen picture with its timing/provenance limitation.'])
],[
 ('Re-evaluate, do not merely reopen',[
  'For the accepted archives, compressed buffers were decompressed and evaluated again, reproducing the recorded measurements. We also checked file hashes and relative evidence links.',
  'A file opening successfully does not prove its sample count, trigger or settings. A hash proves bytes have not changed relative to a recorded digest; it does not by itself prove a correct measurement.']),
 ('Restore behavior as well as settings',[
  'Every handled run releases inputs, verifies fixture armed=0/drive=0, restores saved tone where needed and checks Arduino idle state. Scope settings/run state are read back.',
  'Restoring scope settings does not restore the old acquisition buffer. Termination or transport loss can bypass cleanup, so retain the initial settings and use the documented recovery procedure before the next experiment.'])
])

b.page('A practical workflow you can follow yourself','Use this checklist for the next firmware feature or board revision')
b.cols([
 ('Before connecting a new signal',[
  '1. Write the claim and limit. Identify which part needs a software model, protocol reply, pin measurement or loaded test.',
  '2. Identify the exact board, firmware and instrument. Read the existing pin map. Measure power and choose one defined reference ground.',
  '3. Run relevant host tests and builds. Record what was actually flashed, not just what was compiled.',
  '4. Draw the minimum fixture. Work with both DUT/fixture unpowered; use defined inactive states, resistor values and a bounded source.',
  '5. Start with one ordinary case. Check visible levels and polarity before expanding to stress or faults.'])
],[
 ('Before accepting a result',[
  '6. Trigger on the real event and preserve enough pre/posthistory. Check count, resolution, clipping and channel alignment.',
  '7. Calculate from actual samples. Inspect the trace for every relevant unwanted event, not just the intended transition.',
  '8. Challenge the oracle with deliberately bad synthetic data. Check that extra pulses, late edges and incomplete records cannot pass.',
  '9. Add interactions: saves, UI traffic, bounce, held inputs and recovery. Preserve any failed attempt and its explanation.',
  '10. Repeat the important behavior on the production image. Restore settings, verify inactive outputs and record the remaining gates before integrating the next hardware layer.'])
])

b.page('Use the maintained runners for repetition','Run from the repository root in the bench environment; choose fresh output paths')
y=b.table(['Runner','Use and setup','Configuration restriction'],[
 ('test-firmware.ps1','Host logic and actual-sketch tests; developer shell','No hardware qualification'),
 ('build-firmware.ps1','AVR production/bench and F767 builds','Build does not flash; Grove requires -GroveV4'),
 ('usb-diagnostics-test.py','Parser and USB robustness','Read its required image/setup before use'),
 ('check-ptt-timing.py','CH1 D7, CH2 D8; press/release, bounce, watchdog','SAVE/HANG modes bench-only'),
 ('check-bypass-timing.py','CH1 D10, CH2 D9; midpoint/return timing','Production must already select 151.4 Hz; --serial-closed is production-only'),
 ('exercise-ui-input.py','One A/B/button gesture, known screen','Original encoder wiring; may save depending on screen'),
 ('check-ui-ptt-stress.py','Mixed browsing, keying and saves; CH1 D7, CH2 D8','Bench image; freshly reset home/default menu'),
 ('nucleo-tone-test.py','Held PTT and long D9 scope capture','--current-only supports production and closes COM during capture')],36,516,720,[185,296,239],9.2)
b.p('Python bench dependencies: pyserial 3.5, PyVISA 1.16.2, PyVISA-py 0.8.1, PyUSB 1.3.1 and libusb-package 1.0.30.0. Close other instrument/serial clients. The project-owned requirements and bench README preserve the tested setup and recovery commands.',36,y,720,10.2,13.5)

b.page('Example commands for the installed production image','These are repeatable procedures, not an instruction to change the present setup')
y=b.p('These examples assume the identified COM14 application and COM5 fixture, healthy idle production status, original five drive connections and no radio or bench supply. Rediscover ports first. Replace each NEW directory with a previously unused path.',36,516,720,10.8,14.3)
y=b.code(['# CH1 D7 and CH2 D8, both x10',
 'python tools/check-ptt-timing.py --pro COM14 --standin COM5 `',
 '  --pairs 3 --output NEW_PTT',
 '', '# Move tips with power off: CH1 D10 and CH2 D9',
 'python tools/check-bypass-timing.py --pro COM14 --standin COM5 `',
 '  --pairs 3 --output NEW_BYPASS',
 'python tools/check-bypass-timing.py --pro COM14 --standin COM5 `',
 '  --pairs 1 --serial-closed --output NEW_CLOSED',
 '', '# CH2 stays on D9; measures the currently selected tone without SAVE/HANG',
 'python tools/nucleo-tone-test.py --pro COM14 --standin COM5 `',
 '  --current-only --scope-channel 2 --output NEW_TONE'],36,y,720,9)
b.p('The line-ending backtick shown here is PowerShell continuation. Use the project bench Python environment if python on PATH lacks the pinned packages. These commands temporarily key PTT; retain the bounded fixture setup and stop/readback recovery behavior.',36,y,720,10.4,14)

b.page('What to test when the physical setup allows it','Unrun cases stay visible instead of being converted into passes',chapter='Plan the next integration stage')
y=b.table(['Remaining case','Why it still matters','Next useful evidence'],[
 ('Actual EC11','Variants differ in pin order, direction, detents and bounce','Representative real rotations/presses using the intended wiring'),
 ('Display-bus fault','Host models do not qualify a physically stuck I2C bus','Qualified LOW/NACK fault, continued PTT/tone and visible recovery'),
 ('Power path and interrupted save','4.38 V, then about 4.5 V, do not qualify operating margin or power loss','Single controlled power path; rail capture; cold/held startup; swept write interruptions'),
 ('Coverage and soak','Selected physical frequencies and 60 s of mixed windows are finite','Broader preset/non-preset measurements and longer mixed operation'),
 ('Loaded carrier and radio','Scope-only D8 and raw D9 exclude the real interfaces','Q1/load, filter amplitude/distortion/clicks, microphone interaction and RF deviation')],36,516,720,[170,280,270],9.7)
b.cols([
 ('The physical fault test was deferred',[
  'We prepared an SCL clamp using a reassigned encoder-A drive through its 1 kOhm resistor, plus meter qualification. You could not fit that change on the breadboard. No wiring change was made and no physical clamp was applied.',
  'Seven offline qualifier/cleanup tests pass, but they are not physical display-fault evidence. The prepared procedure can be used when carrier/fixture access is available.'])
],[
 ('How to proceed on the board',[
  'Start with the intended regulated power path and controlled load checks. Then add the PTT transistor/load and reconstruction filter, rechecking the affected digital behavior.',
  'Keep analog and radio limits explicit. A digital firmware pass supports the next stage; the final solution is accepted only after its actual interfaces are measured.'])
],y=y)

b.page('Reference points for further learning','Primary equipment references and the project records behind this guide')
b.cols([
 ('Manufacturer references',[
  '<b>RIGOL DS1000Z-E user and programming guides.</b> Use the model-specific Probe, Trigger, Cursor, Acquire and waveform-transfer sections. Front-panel steps here are a reproducible equivalent; the session itself configured the scope through SCPI.',
  '<link href="https://www.rigol.com/intl/products/oscilloscope/DS1000Z-E.html" color="#075e94">rigol.com - DS1000Z-E product and documentation</link>',
  '<b>Microchip ATmega16U4 and ATmega32U4 datasheet.</b> Consult maximum-frequency versus supply voltage, GPIO thresholds and EEPROM/reset behavior before setting a power-fault campaign.',
  '<link href="https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Summary.pdf" color="#075e94">Microchip datasheet summary</link>']),
 ('Display and meter references',[
  '<link href="https://wiki.seeedstudio.com/Grove-LCD_RGB_Backlight/" color="#075e94">Seeed Grove LCD RGB Backlight documentation</link> and <link href="https://github.com/Seeed-Studio/Grove_LCD_RGB_Backlight" color="#075e94">vendor driver source</link> distinguish V4/V5 addresses and the direct command/data protocol.',
  '<link href="https://www.owon.co.jp/support/download/" color="#075e94">OWON programming-manual download catalog</link>. The project inventory records tested XDM1251 firmware V1.0.1.0.4 tokens and range behavior; do not substitute another model\'s command table.'])
],[
 ('Project reading order',[
  'docs/implementation/firmware-verification-plan.md defines the campaign and limits. docs/implementation/firmware-phase1-guide.md gives the original fixture procedure. tools/bench/README.md gives maintained runners and recovery.',
  'The evidence root is docs/verification/firmware-phase1/2026-11-13/. Its README starts with the latest result and then preserves the sequence of earlier stages.',
  'Within that root, read nucleo-minimal, ptt-electrical, bypass-electrical, grove-ui/mixed-stress and grove-ui/production. Their manifests and per-run source snapshots tie observations to the correct setup and image.']),
 ('What this single document preserves',[
  'All prose, wiring diagrams, annotations and selected analysis plots are embedded here. All 38 distinct retained instrument screens appear in the following appendix. The source index identifies all 41 screen files, including duplicate paths.',
  'No new bench stimulus, firmware upload or power change was performed to create this guide. The original evidence files were read without alteration. Figures labeled analysis are derived plots already retained from the test campaign.'])
])

# Complete instrument-screen archive, without altering the source pixels.
items=list(screens.values())
def screen_caption(item):
    rel=item['aliases'][0];parts=rel.split('/')
    if rel.startswith('grove-ui/production/'):stage='Production Grove'
    elif rel.startswith('grove-ui/'):stage='Grove bench'
    elif rel.startswith('ptt-electrical/'):stage='Early PTT'
    elif rel.startswith('bypass-electrical/'):stage='Early bypass'
    elif rel.startswith('nucleo-minimal/'):stage='Early tone'
    else:stage='Idle PWM'
    case=parts[-2].replace('-',' ')
    return f"{item['id']}  |  {stage}  |  {case}"

for start in range(0,len(items),4):
    b.page(f'Instrument screen archive {start//4+1}',
           '1 time per division  |  2 sample rate and memory  |  3 channel scale  |  Zoom to inspect native detail',
           chapter='All retained instrument screens' if start==0 else None)
    for index,item in enumerate(items[start:start+4]):
        col=index%2;row=index//2;x=36+col*374;top=520-row*238;w=336;h=201.6;y=top-h
        b.image(item['path'],x,y,w,h)
        for number,(tx,ty,bx,by) in enumerate([(170,17,170,-14),(235,17,258,-14),(59,465,130,493)],1):
            xx,yy=x+tx/800*w,y+h-ty/480*h;px,py=x+bx/800*w,y+h-by/480*h
            b.arrow(px,py,xx,yy);b.c.setFillColor(colors.white);b.c.setStrokeColor(BLUE)
            b.c.circle(px,py,4.5,fill=1,stroke=1);b.c.setFillColor(BLUE);b.c.setFont('Bold',5.5);b.c.drawCentredString(px,py-1.8,str(number))
        b.p(html.escape(screen_caption(item)),x,y-17,w,8.3,10,gap=0)

b.page('Instrument screen source index','Paths below are relative to docs/verification/firmware-phase1/2026-11-13/',chapter='Screen source index')
y=516
for item in items:
    for i,rel in enumerate(item['aliases']):
        label=item['id'] if i==0 else '  ='
        text=f'{label}  {rel}'
        b.c.setFillColor(BLACK);b.c.setFont('Mono',7.1);b.c.drawString(36,y,text);y-=10.5
if y<43:raise ValueError('Screen index overflow')
b.p('An equals sign identifies another retained file with identical RGB screen pixels. No empty or inconvenient screen has been removed from this index. The detailed chapters explain why the raw samples, not every screenshot, supported the numerical conclusions.',36,y-7,720,9.6,12.5)

# Resolve the contents form after all page numbers are known.
b.c.beginForm('GuideContents',0,0,W,H)
y=514
for title,page in b.toc:
    b.c.setFillColor(BLACK);b.c.setFont('Body',12);b.c.drawString(48,y,title)
    b.c.drawRightString(738,y,str(page));b.c.setStrokeColor(LIGHT);b.c.line(48,y-8,738,y-8);y-=29
b.p('Read the main chapters in order for the worked reasoning. In the appendix, the small blue markers identify the same three control areas on every screen. Several pictures show dense PWM, a post-resume view or a blank grid; their value and limitations are explained rather than hidden.',48,y-6,690,11,15)
b.c.endForm()
b.finish()
print(f'Created {OUT} with {len(b.pages)} pages and {len(screens)} distinct instrument screens.')
