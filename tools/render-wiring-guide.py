"""Render W1 wiring figures and schedule from the checked-in CSV/pad readback.

Run from any directory: python tools/render-wiring-guide.py
Requires Python 3.10+ and Pillow. Does not open or modify KiCad sources.
"""
from pathlib import Path
import csv
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images/wiring'
OUT.mkdir(parents=True, exist_ok=True)
ROWS = list(csv.DictReader((ROOT/'docs/reference/final-product-wire-list.csv').open(encoding='utf-8')))
PADS = json.loads((ROOT/'docs/verification/wiring-guide/header-readback.json').read_text())['headers']
FONT = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
INK = '#172b3b'
COLORS = {'White':'#82929e','Orange':'#d97706','Yellow':'#bd9900','Gray':'#737b85',
          'Blue':'#2563c0','Black':'#172b3b','Shield + black sleeve':'#586677',
          'Violet':'#864cc4','Red':'#cc3344','Green':'#228550','None':'#aab1b8'}

def font(size=26,bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT),size)

def canvas(title, subtitle, w=1800,h=1100):
    im=Image.new('RGB',(w,h),'#f8fafc');d=ImageDraw.Draw(im)
    d.text((45,28),title,font=font(38,True),fill=INK)
    d.text((45,84),subtitle,font=font(24),fill=INK)
    d.line((45,128,w-45,128),fill='#cbd5df',width=2)
    return im,d

def text(d,x,y,s,size=26,bold=False,color=INK):
    d.text((x,y),s,font=font(size,bold),fill=color)

def box(d,xy,fill='#edf3f7',outline='#5d7485'):
    d.rounded_rectangle(xy,radius=9,fill=fill,outline=outline,width=2)

def wire(d,x1,y1,x2,y2,color='Black',label=None):
    d.line((x1,y1,x2,y2),fill=COLORS[color],width=7)
    if label:text(d,(x1+x2)/2-55,(y1+y2)/2-32,label,22)

def save(im,name):
    im.save(OUT/name)
    print(name,im.size)

def board():
    im,d=canvas('Where each harness plugs into the board',
        'Component side up; saved KiCad coordinates. Locator omits other components and is not a machining drawing.',1600,1250)
    x0,y0,s=470,180,6.4
    xy=lambda x,y:(x0+(x-50)*s,y0+(y-50)*s)
    d.rectangle((*xy(50,50),*xy(150,200)),fill='#e0ede5',outline='#355d49',width=4)
    for x,y in [(56,56),(144,56),(56,194),(144,194)]:
        a,b=xy(x,y);d.ellipse((a-12,b-12,a+12,b+12),fill='#f8fafc',outline=INK,width=2)
    labels={'J1':'MIC / 8 positions','J2':'RADIO / 8 positions','J3':'ENCODER / 5 positions',
        'J4':'GROVE LCD / 4 positions','J5':'BYPASS / 2 positions','J6':'TWO LEDs / 4 positions'}
    for h in PADS:
        ref=h['reference'];ps=h['pads'];coords=[]
        for p in ps:
            a,b=xy(p['x'],p['y']);coords.append((a,b))
            if p['number']=='1':d.rectangle((a-8,b-8,a+8,b+8),fill='#f3b94f',outline=INK,width=2)
            else:d.ellipse((a-7,b-7,a+7,b+7),fill='#f3b94f',outline=INK,width=2)
        a,b=coords[0]
        if ref in ('J1','J2'):
            labely=b-47 if ref=='J1' else b+22
            text(d,a-25,labely,f'{ref}   1  →  8',25,True)
            d.line((coords[-1][0]+15,b,1175,b),fill=INK,width=2)
            text(d,1190,b-18,labels[ref],23)
        else:
            left=ref in ('J3','J4');tx=45 if left else 1170
            text(d,tx,b-30,ref,29,True);text(d,tx,b+8,labels[ref],22)
            d.line((300 if left else 1160,b+5,a-16 if left else a+16,b+5),fill=INK,width=2)
            text(d,a+18,b-15,'1',22,True)
            text(d,a+18,coords[-1][1]-10,str(len(ps)),22)
    text(d,540,210,'Board: 100 × 150 mm',26,True)
    text(d,555,530,'Other components omitted',24)
    text(d,555,580,'+X →     +Y ↓',28,True)
    text(d,45,1170,'Gold square = pin 1. Match the reference and pin-1 mark before inserting each unkeyed housing.',26,True)
    save(im,'board-headers.png')

def plug():
    im,d=canvas('Keep the same physical pin-1 cavity',
        'Schematic example: a 1×4 plug. Turn side to side to view the opposite end; keep the marked side uppermost.',1700,660)
    for x,title,nums in [(90,'WIRE-ENTRY END',[1,2,3,4]),(950,'MATING END',[4,3,2,1])]:
        text(d,x,175,title,30,True)
        box(d,(x,250,x+570,380))
        for i,n in enumerate(nums):
            a=x+65+i*140
            d.rectangle((a-28,275,a+28,340),fill='#f3b94f' if n==1 else 'white',outline=INK,width=3)
            text(d,a-8,290,str(n),28,True)
            if n==1:text(d,a-45,400,'MARK 1',23,True)
        d.rectangle((x+245,236,x+325,251),fill='#2563c0')
    text(d,735,285,'TURN',26,True)
    text(d,85,490,'Numbers name the PCB pins that the cavities mate to; the housing has not been electrically renumbered.',25)
    text(d,85,540,'The blue side mark stays at the top in this example. Actual latch geometry depends on the owned housing.',25)
    save(im,'plug-views.png')

def mic():
    im,d=canvas('H1 MIC and H2 RADIO: all eight contacts on each adapter',
        'Functional map only. External columns are Icom contact identities established by the adapter worksheet.',1800,1160)
    names={1:'MIC AUDIO',2:'+8 V / RAW supply',3:'UP/DOWN',4:'PIN 4 pass-through',5:'PTT',6:'PTT / power return',7:'Audio shield / return',8:'PIN 8 pass-through'}
    for offset,h,end in [(40,'J1','MIC'),(925,'J2','RADIO')]:
        text(d,offset,165,f'{h} / {end}',31,True)
        text(d,offset,212,'PCB cavity',23,True);text(d,offset+490,212,'External Icom contact',23,True)
        rs=[r for r in ROWS if r['header']==h]
        for i,r in enumerate(rs):
            y=280+i*86;p=int(r['pin'])
            box(d,(offset,y-8,offset+96,y+45));text(d,offset+28,y,str(p),29,True)
            wire(d,offset+100,y+18,offset+475,y+18,r['color'])
            label='Shield; 26 AWG pigtail' if p==7 else f'{r["color"]} / {r["awg"]} AWG'
            text(d,offset+125,y-15,label,21)
            text(d,offset+495,y,f'{p}  {names[p]}',24,True)
    text(d,60,1010,'J1-5 = microphone switch input. J2-5 = transistor-controlled radio PTT output. Do not join them directly.',27,True)
    text(d,60,1060,'Pin 1 uses shielded core; pin 7 carries shield/return. Keep pin 6 separate. No added metal-shell bond.',26)
    save(im,'mic-radio.png')

def encoder():
    im,d=canvas('H3: bare EC11 encoder and push switch',
        'Functional schematic, not a physical terminal layout. Identify C/A/B/S1/S2 with a meter before soldering.',1700,850)
    roles=[('1 CLK / D4','A','Blue',250),('2 DT / D5','B','Yellow',350),
           ('3 SW / D6','S1','Violet',450),('5 GND','C','Black',650)]
    text(d,65,170,'J3 PCB cavities',30,True);text(d,1090,170,'Identified EC11 contacts',30,True)
    for lhs,rhs,c,y in roles:
        box(d,(65,y-12,375,y+55));text(d,90,y,lhs,27,True)
        wire(d,375,y+20,1120,y+20,c);text(d,570,y-18,f'{c} / 26 AWG',24)
        box(d,(1120,y-12,1260,y+55));text(d,1160,y,rhs,30,True)
    box(d,(65,525,750,593),fill='#fff3d7');text(d,90,542,'4  +5 V: EMPTY cavity; no contact or wire',27,True)
    box(d,(1420,538,1560,605));text(d,1455,550,'S2',30,True)
    wire(d,1260,670,1490,670);wire(d,1490,670,1490,605)
    text(d,1130,718,'Local black C–S2 jumper',24,True)
    text(d,65,770,'One wire in J3-5 crimp. Join C and S2 at the encoder. No added pull-ups; no powered encoder module.',26,True)
    save(im,'encoder.png')

def ui():
    im,d=canvas('H4 display, H5 bypass and H6 status LEDs',
        'Functional schematics. Wire labels name signals; physical plug/lug views must be identified separately.',1800,1240)
    text(d,60,160,'J4 → factory Grove V4 plug',30,True)
    for i,(lhs,rhs,c) in enumerate([('1 GND','4 GND','Black'),('2 +5 V','3 VCC','Red'),('3 SDA / D2','2 SDA','White'),('4 SCL / D3','1 SCL','Yellow')]):
        y=230+i*85;box(d,(60,y-8,365,y+45));text(d,80,y,lhs,26,True)
        wire(d,365,y+18,1030,y+18,c);text(d,580,y-16,c+' / 26 AWG*',24)
        text(d,1060,y,'Grove '+rhs,28,True)
    text(d,60,580,'*Replacement-wire recommendation; retain compatible factory lead gauge. Never feed this plug +8 V.',25,True)
    text(d,60,650,'J5 → maintained bypass switch',30,True)
    wire(d,440,720,1030,720,'Violet');text(d,60,700,'1  BYPASS / D10',27,True);text(d,1060,700,'C common',27,True)
    wire(d,440,790,1030,790);text(d,60,770,'2  GND',27,True);text(d,1060,770,'T1 selected throw',27,True)
    text(d,65,835,'Closed C–T1 = BYPASS. Open = tone enabled. Insulate unused throw. 26 AWG violet + black.',25)
    text(d,60,910,'J6 → two separate bare LEDs; 26 AWG (R6/R7 already on PCB)',30,True)
    for i,(lhs,rhs,c) in enumerate([('1 PTT +','Red LED A (+)','Red'),('2 GND','Red LED K (−)','Black'),('3 BYPASS +','Green LED A (+)','Green'),('4 GND','Green LED K (−)','Black')]):
        y=970+i*55;text(d,65,y,lhs,25,True);wire(d,440,y+16,1030,y+16,c);text(d,1060,y,rhs,25,True)
    save(im,'display-switch-leds.png')

def gx16():
    im,d=canvas('GX16-8: contact numbers from the front and the solder side',
        'Reference: Renhotec standard male/female layout. Key stays at 12 o’clock in all four views. Not to scale.',1800,1510)
    # Seven perimeter contacts plus center contact 8; male front from source.
    # Explicit source positions, progressing down the left, then up the right.
    front={str(i+1):(-math.sin(math.radians(25+i*310/6))*132,
                    -math.cos(math.radians(25+i*310/6))*132) for i in range(7)} | {'8':(0,0)}
    for cx,cy,male,rear in [(440,440,True,False),(1320,440,True,True),
                            (440,1000,False,False),(1320,1000,False,True)]:
        label=('MALE PINS' if male else 'FEMALE SOCKETS')+(' — REAR / SOLDER' if rear else ' — FRONT / MATING')
        text(d,cx-340,cy-260,label,29,True)
        d.ellipse((cx-190,cy-190,cx+190,cy+190),fill='#d4dde4',outline=INK,width=4)
        d.ellipse((cx-160,cy-160,cx+160,cy+160),fill='#edf3f7',outline=INK,width=2)
        d.rectangle((cx-19,cy-195,cx+19,cy-166),fill='#f8fafc',outline=INK,width=2)
        text(d,cx-28,cy-235,'KEY',21,True)
        mirror=-1 if male==rear else 1
        for n,(x,y) in front.items():
            x=cx+mirror*x;y=cy+y
            d.ellipse((x-23,y-23,x+23,y+23),fill='#d7ad58' if male and not rear else 'white',outline=INK,width=3)
            if not male and not rear:d.ellipse((x-13,y-13,x+13,y+13),outline=INK,width=2)
            text(d,x-9,y-16,n,27,True)
        text(d,cx-330,cy+215,'Look into '+('solder cups inside the case' if rear else 'the external mating face'),25)
    text(d,60,1280,'Rear views are mirrored from the front of the SAME half. Male and female mating faces also mirror.',27,True)
    text(d,60,1335,'Numbers here are GX16 cavity numbers — not automatically the functional Icom/header numbers.',27,True)
    text(d,60,1390,'Use molded numbers + continuity worksheet. Do not color or solder a cup from its clock position alone.',26)
    save(im,'gx16-pinouts.png')

def ec11_physical():
    im,d=canvas('EC11: recognize the rotation terminals and push-switch pair',
        'Illustrative 3 + 2 terminal body. This is a reference layout, not an exact WWZMDiB terminal identification.',1800,1290)
    for cx,front in [(420,True),(1290,False)]:
        text(d,cx-330,165,'SHAFT / FRONT VIEW' if front else 'TERMINAL / REAR VIEW',31,True)
        text(d,cx-330,210,'Shaft points toward you' if front else 'Shaft points away from you',26)
        box(d,(cx-185,350,cx+185,690),fill='#c5ced6')
        d.ellipse((cx-155,380,cx+155,660),fill='#e5e9ec',outline=INK,width=3)
        for sx in [-225,225]:
            d.rectangle((cx+sx-20,470,cx+sx+20,570),fill='#a0aab4',outline=INK,width=2)
        if front:
            d.ellipse((cx-58,462,cx+58,578),fill='#a8b5bf',outline=INK,width=3)
            text(d,cx-45,505,'SHAFT',22,True)
        else:
            box(d,(cx-113,430,cx+113,604),fill='#263a49')
            text(d,cx-73,485,'BACK',30,True,color='white')
        switches=[('S1','Violet','J3-3'),('S2','Black','to C')]
        rotary=[('A*','Blue','J3-1'),('C*','Black','J3-5'),('B*','Yellow','J3-2')]
        if not front:switches=switches[::-1];rotary=rotary[::-1]
        for i,(n,c,dest) in enumerate(switches):
            x=cx-100+i*200
            d.rectangle((x-14,315,x+14,365),fill='#d7ad58',outline=INK,width=2)
            text(d,x-20,265,n,27,True)
            text(d,x-60,235,dest,23)
        for i,(n,c,dest) in enumerate(rotary):
            x=cx-125+i*125
            d.rectangle((x-14,678,x+14,738),fill='#d7ad58',outline=INK,width=2)
            wire(d,x,740,x,805,c)
            text(d,x-22,820,n,29,True);text(d,x-35,862,dest,23,True)
        if not front:
            # C to S2 is the local jumper, routed outside the housing.
            d.line((cx,740,cx,765,cx-290,765,cx-290,310,cx-100,310,cx-100,315),fill=INK,width=6)
            text(d,cx-310,945,'Black local C–S2 jumper; one ground crimp at J3-5',23,True)
    text(d,60,1010,'Two-terminal group: switch. Three-terminal group: rotation. Side ears: mechanical mounting only.',27,True)
    text(d,60,1065,'*First identify C by meter. A/B are assigned here; swapping only A/B reverses selection direction.',26)
    text(d,60,1120,'S1/S2 can exchange roles. Fit only after the measured terminal groups match this reference view.',26)
    text(d,60,1175,'J3-4 (+5 V) remains EMPTY. No wire goes to the metal body, shaft or mounting ears.',27,True)
    save(im,'ec11-pinout.png')

def tables():
    sections=[]
    for h in ['J1','J2','J3','J4','J5','J6','Local']:
        sections.extend([f'#### {h} connection schedule','',
            '| Wire ID / PCB pin | Function | Off-board termination | Recommended color | AWG |',
            '| --- | --- | --- | --- | --- |'])
        for r in ROWS:
            if r['header']==h:
                sections.append(f'| `{r["wire_id"]}` | `{r["net"]}` | {r["destination"]} | {r["color"]} | {r["awg"]} |')
        sections.append('')
    path=ROOT/'docs/final-product-wiring-guide.md'
    content=path.read_text(encoding='utf-8')
    start='<!-- WIRE_TABLES_START -->';end='<!-- WIRE_TABLES_END -->'
    before,tail=content.split(start);_,after=tail.split(end)
    path.write_text(before+start+'\n\n'+'\n'.join(sections)+'\n'+end+after,encoding='utf-8')

if __name__=='__main__':
    board();plug();mic();encoder();ui();gx16();ec11_physical();tables()
