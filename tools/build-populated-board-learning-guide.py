"""Build measured-data figures and content for the populated PCB learning guide.

Run from the repository root with Python, numpy, matplotlib and Pillow.
Then run tools/build-populated-board-learning-guide.ps1 to author DOCX/PDF in Word.
Only retained evidence is read; no instrument or KiCad source is modified.
"""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/verification/populated-board/2026-11-16'
FIG=ROOT/'docs/images/populated-board-learning'
WORK=ROOT/'.agent-scratch/populated-board-learning-guide'
FIG.mkdir(parents=True,exist_ok=True)
WORK.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':11,
                     'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,
                     'figure.facecolor':'white','savefig.facecolor':'white'})
BLUE='#087f96'; ORANGE='#b86513'; GRAY='#687681'; INK='#152b3a'; PALE='#eaf2f5'


def read(path): return json.loads((BASE/path).read_text(encoding='utf-8-sig'))


def wave(folder,channel=None):
    path=BASE/folder
    if channel is not None: path=path/f'ch{channel}'
    meta=json.loads((path/'capture.json').read_text())
    p=meta['preamble']
    raw=np.frombuffer((path/'waveform.u8').read_bytes(),dtype=np.uint8)
    if len(raw)!=p['points']: raise ValueError('Incomplete waveform '+str(path))
    v=(raw.astype(float)-p['yorigin']-p['yreference'])*p['yincrement']
    t=(np.arange(len(raw))-p['xreference'])*p['xincrement']+p['xorigin']
    return t,v,p,raw


def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=240,bbox_inches='tight',pad_inches=.12)
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',pad_inches=.12)
    plt.close(fig)


def axis_clean(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.2)


def arrow(ax,start,end,color=INK,**kwargs):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='->',mutation_scale=11,
                                 color=color,linewidth=1.2,**kwargs))


def box(ax,x,y,w,h,text,color=PALE):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor=INK,linewidth=1))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)


def functional_path():
    fig,ax=plt.subplots(figsize=(7.2,2.6))
    ax.set(xlim=(0,10),ylim=(0,3)); ax.axis('off')
    box(ax,.1,1.8,1.5,.75,'Microphone\naudio')
    box(ax,8.2,1.8,1.65,.75,'Radio\naudio')
    arrow(ax,(1.6,2.18),(8.2,2.18))
    ax.text(4.9,2.48,'Direct pass-through J1 pin 1 to J2 pin 1',ha='center',fontsize=9)
    stages=[(.1,'Pro Micro\nD9 PWM'),(2.1,'R1 R2 C1 C2\nlow-pass filter'),(4.2,'Divider and\nRV1 level'),(6.3,'C3 DC block\nand R5 mixer')]
    for x,text in stages: box(ax,x,.25,1.8,.85,text)
    for x in [1.9,4.,6.1]: arrow(ax,(x,.67),(x+.2,.67))
    arrow(ax,(8.1,.67),(8.1,2.18))
    ax.text(.95,.03,'TP4',ha='center',fontsize=9,color=BLUE)
    ax.text(3,.03,'TP5',ha='center',fontsize=9,color=BLUE)
    ax.text(8.45,1.4,'TP6 joins\nthe audio net',fontsize=9,color=BLUE)
    ax.text(5,1.38,'The tone is added in parallel with microphone audio',ha='center',fontsize=10)
    save(fig,'functional-path')


def bench_setup():
    fig,ax=plt.subplots(figsize=(7.2,4.15))
    ax.set(xlim=(0,10),ylim=(0,6)); ax.axis('off')
    box(ax,3.65,2.05,2.6,2.2,'Populated PCB\n\nTP2 RAW   TP3 +5 V\nTP1 ground\n\nNo PCB USB')
    box(ax,.1,4.4,2.7,1.15,'KORAD KA3005P\n8.00 V and 50 mA limit')
    arrow(ax,(2.8,4.85),(3.65,3.65),ORANGE)
    ax.text(2.85,4.45,'+ to TP2\n- to TP1',fontsize=9)
    box(ax,7.2,4.4,2.7,1.15,'OWON XDM1251\nTP3 voltage vs TP1')
    arrow(ax,(7.2,4.85),(6.25,3.65),BLUE)
    box(ax,7.2,1.8,2.7,1.35,'Rigol DS1202Z-E\nTips move by test\nGround clips to TP1')
    arrow(ax,(7.2,2.5),(6.25,2.9),BLUE)
    box(ax,.1,1.65,2.7,1.6,'NUCLEO-F767ZI\nST-LINK USB to PC\nOpen-drain stimulus\nNo shared power rail')
    arrow(ax,(2.8,2.45),(3.65,2.6),BLUE)
    ax.text(.2,.8,'PF12 through 1 kΩ to J1-5 for PTT\nPF13 through 1 kΩ to J5-1 for bypass\nNUCLEO GND to TP1',fontsize=9)
    ax.text(6.6,.8,'Supply OFF for wiring\nScope grounds at TP1',fontsize=9,ha='left')
    save(fig,'bench-setup')


def board_locator():
    data=read('learning-pad-locator.json')['footprints']
    byref={f['reference']:f for f in data}
    fig,ax=plt.subplots(figsize=(7.2,5.4))
    ax.add_patch(Rectangle((50,50),100,150,facecolor='#eef4ee',edgecolor=INK,linewidth=1.2))
    for x,y in [(56,56),(144,56),(56,194),(144,194)]:
        ax.add_patch(Circle((x,y),2,facecolor='white',edgecolor=GRAY,linewidth=.8))
    for ref in ['J1','J2','J3','J4','J5','J6','U1','R1','R2','R3','R4','R5','RV1','Q1']:
        pads=byref[ref]['pads']; xs=[p['x'] for p in pads]; ys=[p['y'] for p in pads]
        if ref=='U1':
            ax.add_patch(Rectangle((min(xs)-2,min(ys)-2),max(xs)-min(xs)+4,max(ys)-min(ys)+4,
                                   facecolor='#dbe5eb',edgecolor=GRAY,linewidth=.8))
            ax.text(np.mean(xs),np.mean(ys),'U1\nPro Micro',ha='center',va='center',fontsize=8)
        elif ref.startswith('J'):
            ax.plot(xs,ys,color=GRAY,linewidth=2,zorder=2)
            ax.text(np.mean(xs)+(4 if ref in ['J3','J4','J5','J6'] else 0),
                    np.mean(ys)+(-4 if ref!='J2' else 5),ref,fontsize=9,ha='left' if ref in ['J3','J4','J5','J6'] else 'center')
        else:
            ax.plot(xs,ys,color=GRAY,linewidth=2)
            ax.text(np.mean(xs),min(ys)-3,ref,ha='center',fontsize=7)
        for p in pads:
            ax.scatter(p['x'],p['y'],s=9,marker='s' if p['number']=='1' else 'o',color='#c9973c',zorder=3)
    places={'TP1':(24,115),'TP2':(24,93),'TP3':(24,77),'TP4':(169,130),
            'TP5':(169,153),'TP6':(24,179),'TP7':(24,150),'TP8':(169,190)}
    names=['GND','RAW +8 V','regulated +5 V','PWM','FILTER 2','audio injection','PTT sense','radio PTT']
    for i,name in enumerate(names,1):
        ref=f'TP{i}'; p=byref[ref]['pads'][0]; label=places[ref]
        ax.scatter(p['x'],p['y'],s=38,color=INK if i==1 else ORANGE if i in [2,3] else BLUE,zorder=5)
        ax.annotate(ref+'\n'+name,xy=(p['x'],p['y']),xytext=label,ha='center',va='center',
                    fontsize=9,arrowprops=dict(arrowstyle='-',color=GRAY,linewidth=.8))
    ax.text(100,64,'Component side up\nJ1 and J2 at the bottom',ha='center',va='top',fontsize=10)
    ax.set(xlim=(5,192),ylim=(210,43),aspect='equal'); ax.axis('off')
    save(fig,'board-testpoints')


def resistance_plot():
    fig,ax=plt.subplots(figsize=(7.2,3))
    for file,label,color in [('tp3-to-ground-resistance.json','+5 V to ground',BLUE),
                              ('tp2-to-ground-resistance.json','RAW to ground',ORANGE),
                              ('raw-to-vcc-resistance.json','RAW to +5 V',GRAY)]:
        d=read(file); y=np.array([r['ohm'] if r['ohm'] is not None else np.nan for r in d['readings']])/1000
        ax.plot(np.arange(1,len(y)+1),y,'o-',label=label,color=color,markersize=4)
        ax.annotate(f'{y[-1]:.0f} kΩ',xy=(12,y[-1]),xytext=(12.4,y[-1]),fontsize=10,color=color,va='center')
    ax.set(xlim=(.7,14),ylim=(0,1100),xlabel='Host poll index within each separate run',ylabel='Displayed resistance (kΩ)')
    ax.legend(loc='upper left',fontsize=9); axis_clean(ax)
    ax.text(5,1020,'First RAW and rail-to-rail replies were OL',fontsize=9,color=GRAY)
    save(fig,'resistance-settling')


def power_plot():
    fig,ax=plt.subplots(figsize=(7.2,2.55))
    d1=read('raw-at-pcb.json')['raw_readings_v']; d2=read('vcc-at-pcb.json')['vcc_readings_v']
    ax.barh([1,0],[np.mean(d1),np.mean(d2)],height=.42,color=[ORANGE,BLUE])
    for y,v,label in [(1,np.mean(d1),'RAW at TP2'),(0,np.mean(d2),'regulated rail at TP3')]:
        ax.text(.18,y,label,color='white',va='center',fontsize=11)
        ax.text(v+.12,y,f'{v:.4f} V',va='center',fontsize=11)
    ax.axvline(8,color=ORANGE,ls='--',lw=1); ax.text(8.03,1.38,'8.00 V supply setting',ha='right',fontsize=9)
    ax.set(xlim=(0,9.3),ylim=(-.5,1.65),yticks=[],xlabel='Voltage relative to TP1 ground (V)')
    axis_clean(ax)
    save(fig,'power-rails')


def pwm_plot():
    t,v,p,raw=wave('idle-pwm/capture')
    threshold=(np.percentile(raw,10)+np.percentile(raw,90))/2
    rises=np.where((raw[:-1]<threshold)&(raw[1:]>=threshold))[0]+1
    origin=rises[2]; i0=max(0,origin-int(20e-6/p['xincrement'])); i1=origin+int(340e-6/p['xincrement'])
    tx=(np.arange(i0,i1)-origin)*p['xincrement']*1e6
    fig,ax=plt.subplots(figsize=(7.2,3.4))
    ax.plot(tx,v[i0:i1],color=BLUE,lw=1)
    ax.annotate('',xy=(100,5.38),xytext=(0,5.38),arrowprops=dict(arrowstyle='<->',color=INK))
    ax.text(50,5.47,'One period ≈ 100 µs',ha='center',fontsize=10)
    ax.annotate('HIGH ≈ 4.92 V',xy=(25,4.916),xytext=(150,4.12),arrowprops=dict(arrowstyle='->',color=GRAY),fontsize=10)
    ax.annotate('LOW ≈ 0.10 V',xy=(75,.102),xytext=(155,.78),arrowprops=dict(arrowstyle='->',color=GRAY),fontsize=10)
    ax.annotate('',xy=(50,3.6),xytext=(0,3.6),arrowprops=dict(arrowstyle='<->',color=ORANGE))
    ax.text(25,3.25,'HIGH for\nabout 50 µs',ha='center',va='top',fontsize=9,color=ORANGE)
    ax.set(xlim=(-20,340),ylim=(-.4,5.9),xlabel='Time relative to an actual rising edge (µs)',ylabel='TP4 voltage (V)')
    axis_clean(ax); save(fig,'idle-pwm-annotated')


def filter_plot():
    fig,axes=plt.subplots(2,1,figsize=(7.2,4),sharex=True,sharey=True,layout='constrained')
    for ax,folder,title in zip(axes,['idle-filter-100mv/ripple','grounded-ch2-control/ripple'],
                               ['CH2 on TP5 filter output','CH2 tip and ground both on TP1']):
        t,v,p,raw=wave(folder)
        n=int(.00042/p['xincrement']); x=np.arange(n)*p['xincrement']*1e6
        ax.plot(x,v[:n]*1000,color=BLUE,lw=.45)
        ax.set_title(title,loc='left'); ax.set_ylabel('AC reading (mV)'); ax.set_ylim(-320,340)
        axis_clean(ax)
    axes[0].annotate('Brief spikes appear at PWM edges',xy=(50,250),xytext=(115,235),fontsize=9,
                     arrowprops=dict(arrowstyle='->',color=GRAY))
    axes[1].annotate('Comparable spikes remain on ground',xy=(150,-240),xytext=(180,-180),fontsize=9,
                     arrowprops=dict(arrowstyle='->',color=GRAY))
    axes[-1].set_xlabel('Elapsed time from the start of each separate record (µs)')
    save(fig,'filter-ground-control')


def tone_plot():
    data=read('physical-tone-bypass/result.json')
    fig,axes=plt.subplots(5,1,figsize=(7.2,5.15),sharex=True,sharey=True,layout='constrained')
    labels={'idle':'Idle','ptt':'PTT pressed','bypass':'Bypass while PTT held','resume':'Bypass removed','release':'PTT released'}
    for ax,row in zip(axes,data['states']):
        t,v,p,raw=wave('physical-tone-bypass/'+row['name'])
        n=int(.03/p['xincrement']); n-=n%32
        avg=v[:n].reshape(-1,32).mean(axis=1)
        ax.plot((np.arange(len(avg))*32+15.5)*p['xincrement']*1000,avg,color=BLUE,lw=1)
        ax.set_title(labels[row['name']],loc='left',fontsize=10)
        ax.set_ylim(.35,2.75); ax.set_yticks([1,2]); ax.set_ylabel('TP5 (V)',fontsize=9,labelpad=6)
        axis_clean(ax)
    axes[-1].set_xlabel('First 30 ms of each independent 240 ms record')
    save(fig,'tone-bypass-sequence')


def ptt_circuit():
    fig,ax=plt.subplots(figsize=(7.2,1.9))
    ax.set(xlim=(0,10),ylim=(0,2.6)); ax.axis('off')
    box(ax,.05,.65,2.15,1.05,'Microphone PTT\nJ1-5 to R8 to TP7')
    box(ax,3.05,.65,1.75,1.05,'Pro Micro\ninput D7')
    box(ax,5.6,.65,1.7,1.05,'D8 base drive\nQ1 NPN')
    arrow(ax,(2.2,1.18),(3.05,1.18)); arrow(ax,(4.8,1.18),(5.6,1.18))
    ax.plot([7.3,8.6],[1.18,1.18],color=INK,lw=1.2)
    ax.plot([8.6,8.6],[1.18,2.15],color=INK,lw=1.2)
    ax.text(8.9,1.2,'TP8 collector',fontsize=10,va='center')
    ax.text(8.6,2.3,'TP3 +5 V\nthrough external 1 kΩ',fontsize=9,ha='center')
    ax.text(6.45,.28,'Emitter returns to TP1 ground',ha='center',fontsize=9)
    ax.text(2.4,2.25,'NUCLEO sinks J1-5 through 1 kΩ',fontsize=10,ha='center')
    arrow(ax,(1.8,2.02),(1.2,1.7),BLUE)
    ax.text(5,.04,'Simplified test arrangement; base resistor and pull-down omitted from this block view',ha='center',fontsize=8,color=GRAY)
    save(fig,'ptt-test-circuit')


def ptt_plot():
    data=read('loaded-ptt/result.json')
    chosen=[next(r for r in data['transitions'] if r['name']=='bypass-0-pair-1-press'),
            next(r for r in data['transitions'] if r['name']=='bypass-1-pair-3-release')]
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.65),sharey=True,layout='constrained')
    for ax,row in zip(axes,chosen):
        m=row['measurement']
        for ch,label,color,style in [(1,'TP7 sense',GRAY,'--'),(2,'TP8 collector',BLUE,'-')]:
            t,v,p,raw=wave('loaded-ptt/'+row['name'],ch)
            x=(t-m['input_edge_s'])*1000
            keep=(x>=-1)&(x<=9)
            ax.plot(x[keep][::10],v[keep][::10],color=color,ls=style,lw=1,label=label)
        ax.annotate('',xy=(m['latency_ms'],2.6),xytext=(0,2.6),arrowprops=dict(arrowstyle='<->',color=ORANGE))
        ax.text(m['latency_ms']/2,2.9,f"{m['latency_ms']:.3f} ms",ha='center',fontsize=10,color=ORANGE)
        ax.set_title('Normal press' if m['pressed'] else 'Bypass mode release',loc='left')
        ax.set(xlim=(-1,9),ylim=(-.3,5.5),xlabel='Time from actual input edge (ms)')
        ax.legend(loc='lower right',fontsize=8); axis_clean(ax)
    axes[0].set_ylabel('Voltage (V)')
    save(fig,'ptt-timing-annotated')


def mixing_plot():
    fig,axes=plt.subplots(2,2,figsize=(7.2,4.1),layout='constrained')
    for r,folder in enumerate(['mixing-maximum-b','mixing-minimum']):
        d=read(folder+'/result.json')
        for c,ch in enumerate([1,2]):
            t,v,p,raw=wave(folder,ch)
            n=int(.03/p['xincrement']); n-=n%32
            avg=v[:n].reshape(-1,32).mean(axis=1)
            axes[r,c].plot((np.arange(len(avg))*32+15.5)*p['xincrement']*1000,avg,color=BLUE,lw=1)
            axes[r,c].set_title(('Clockwise setting' if r==0 else 'Verified minimum')+'\n'+('TP5 filter' if ch==1 else 'TP6 audio'),fontsize=10)
            axes[r,c].set_ylim((.35,2.75) if ch==1 else (-.10,.10))
            axes[r,c].set_ylabel('V'); axis_clean(axes[r,c])
    for ax in axes[-1]: ax.set_xlabel('Elapsed time (ms)')
    save(fig,'mixing-and-minimum')


def led_plot():
    bad=read('loaded-leds/result.json')['states'][-1]['measurements'][1]['mean_v']
    good=read('loaded-leds-c/result.json')['states'][2]['measurements'][1]['mean_v']
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.45),layout='constrained',gridspec_kw={'width_ratios':[1.1,1]})
    ax=axes[0]; ax.set(xlim=(0,5),ylim=(0,4)); ax.axis('off')
    ax.text(2.5,3.65,'GPIO HIGH',ha='center',fontsize=11)
    ax.plot([2.5,2.5],[3.3,2.9],color=INK)
    box(ax,1.6,2.25,1.8,.65,'R6 or R7 330 Ω')
    ax.plot([2.5,2.5],[2.25,1.9],color=INK)
    ax.text(2.8,1.95,'J6 output\nmeasured here',va='center',fontsize=9)
    box(ax,1.6,.85,1.8,.65,'Temporary 1 kΩ')
    ax.plot([2.5,2.5],[1.9,1.5],color=INK)
    ax.plot([2.5,2.5],[.85,.45],color=INK)
    ax.text(2.5,.15,'J6 return to ground',ha='center',fontsize=10)
    ax=axes[1]
    ax.bar(['Wrong load\n9.939 kΩ','Verified load\n1.0004 kΩ'],[bad,good],color=[ORANGE,BLUE],width=.55)
    for i,val in enumerate([bad,good]): ax.text(i,val+.12,f'{val:.3f} V',ha='center',fontsize=11)
    ax.set(ylim=(0,5.4),ylabel='Asserted bypass output (V)')
    axis_clean(ax)
    save(fig,'led-load-diagnostic')


def next_steps_plot():
    fig,ax=plt.subplots(figsize=(7.2,1.9)); ax.axis('off'); ax.set(xlim=(0,10),ylim=(0,2.8))
    stages=[('PCB screens\npassed',.05),('Wire actual\nUI devices',2.05),('Check full\nload power',4.05),('Map and test\nradio interface',6.05),('Set tone\ndeviation',8.05)]
    for text,x in stages: box(ax,x,.75,1.8,1.05,text)
    for x in [1.85,3.85,5.85,7.85]: arrow(ax,(x,1.28),(x+.2,1.28))
    ax.text(5,.25,'Power off before each wiring change; begin radio setup with RV1 at minimum',ha='center',fontsize=10)
    save(fig,'integration-next-steps')


def make_figures():
    for function in [functional_path,bench_setup,board_locator,resistance_plot,power_plot,pwm_plot,
                     filter_plot,tone_plot,ptt_circuit,ptt_plot,mixing_plot,led_plot,next_steps_plot]:
        function()


PAGES=[]
def page(title,blocks): PAGES.append({'title':title,'blocks':blocks})
def para(text,lead=None): return {'type':'paragraph','text':text,'lead':lead}
def figure(name,caption,width=7.0): return {'type':'figure','path':str(FIG/(name+'.png')),'caption':caption,'width_inches':width,'alt':caption}
def table(headers,rows,widths,font=10): return {'type':'table','headers':headers,'rows':rows,'widths':widths,'font_size':font}


def make_content():
    page('1 What the checks established',[
        para('The populated Icom CTCSS carrier PCB passed the selected pre-wiring electrical checks. It is ready for staged connection of the controls and display, followed by radio integration checks. No PCB defect was identified in this campaign.'),
        para('The Pro Micro was soldered in place and tested as part of the board. Final off-board devices and the radio stayed disconnected. TP4 was initially missing; the owner installed it before the PWM tests. Measurements were taken on 16 November 2026.'),
        figure('functional-path','Figure 1. The microphone audio passes directly between the headers. A separate PWM and filter path adds the CTCSS tone to that audio net. This is a functional diagram, not a complete schematic.'),
        table(['Circuit block','What we observed'],[
            ['Power','RAW 7.9834 to 7.9839 V; regulated rail approximately 5.000 V'],
            ['Idle PWM','9,999.77 Hz carrier and 50.04 to 50.08 percent duty'],
            ['Filtered tone','Approximately 151.393 to 151.398 Hz; PTT and bypass control it'],
            ['Loaded radio PTT','About 0.084 V LOW at a calculated 4.9 mA load; response 3.84 to 5.20 ms'],
            ['Final tone output','127.7 mV central peak-to-peak at the tested clockwise setting; 1.05 mV at minimum'],
            ['LED outputs and continuity','Both loaded LED paths passed; 21 continuity checks were at most 0.3 Ω']
        ],[1.8,5.35],10),
        para('The practical conclusion is a passed PCB screen, not complete product acceptance. The real display load, encoder, cable adapters and radio still need their integration checks. RV1 is left at minimum.')])

    page('2 How the instruments were connected',[
        para('A test is useful only when the instrument is connected to the intended points. The supply provided energy, the meter measured steady voltage or resistance, the scope recorded waveforms, and the NUCLEO reproduced switch closures.'),
        figure('bench-setup','Figure 2. Common test arrangement. The supply and NUCLEO power rails stayed separate; their grounds shared TP1. Probe tips moved between tests. The diagram is schematic and does not represent a breadboard layout.'),
        table(['Instrument','Role and connection'],[
            ['KORAD KA3005P','USB COM11; RAW at TP2 and return at TP1; 8.00 V and 50 mA limit'],
            ['OWON XDM1251','USB COM15; voltage across a test point and TP1; isolated resistance checks when unpowered'],
            ['Rigol DS1202Z-E','Two analog channels; actual probe switches matched the selected channel factors during captures'],
            ['NUCLEO-F767ZI','ST-LINK USB COM5; PF12 through 1 kΩ to J1-5, PF13 through 1 kΩ to J5-1, GND to TP1']
        ],[1.75,5.4],10),
        para('The fixture outputs were open drain: they pulled an input LOW or released it. The PCB supplied the pull-ups. An output command of 1 meant a simulated pressed switch, not a driven 3.3 V HIGH.'),
        para('The PCB USB connector remained disconnected during RAW-powered measurements. Firmware was not flashed or changed. Fixture identity and STOP readback were checked before connecting its signal wires. At the end, its outputs were released before removal.')])

    page('3 Finding the test points',[
        figure('board-testpoints','Figure 3. Component-side locator derived from saved KiCad pad positions. Simplified bodies and omitted components make the test points readable; this is not an as-built photograph or a fabrication drawing.',6.0),
        table(['Point','Net','Why it matters'],[
            ['TP1','GND','Reference for supply, meter and scope grounds'],
            ['TP2','RAW nominal +8 V','Incoming power before the module regulator'],
            ['TP3','Regulated +5 V','MCU and UI supply rail'],
            ['TP4','D9 PWM','Switching source before the analog filter'],
            ['TP5','FILTER 2','Reconstructed tone before divider and level control'],
            ['TP6','MIC AUDIO','Tone injection and direct microphone audio net'],
            ['TP7','PTT SENSE D7','Actual MCU input after the onboard series resistor'],
            ['TP8','RADIO PTT','Q1 collector that sinks the radio PTT line']
        ],[.65,1.8,4.7],9.5),
        para('Pin 1 remains pin 1 when the board is rotated. Use the reference labels and square pin-1 lands rather than a remembered left-to-right view. The Pro Micro names in the continuity checklist mean its printed Arduino pin labels.')])

    page('4 Learning from unpowered resistance checks',[
        para('Before applying power, we looked for unintended low-resistance paths from each rail to ground and between RAW and +5 V. The module stayed installed, so capacitors, resistors and semiconductor junctions all influenced the reading.'),
        figure('resistance-settling','Figure 4. Displayed resistance changed as the meter stimulated the unpowered circuit. The horizontal axis is host poll index, not a calibrated sample-time axis. An OL response is an overload indication, not a numerical resistance.'),
        table(['Probe pair','Observed behavior','What it told us'],[
            ['TP3 to TP1','Settled near 536 kΩ','No low-resistance +5 V short observed'],
            ['TP2 to TP1','634 kΩ rising to 749 kΩ','No low-resistance RAW short observed; not settled'],
            ['TP2 to TP3','683 kΩ rising to 986 kΩ','No low-resistance rail-to-rail short observed in this polarity']
        ],[1.15,2.25,3.75],10),
        para('A resistance meter applies a test stimulus. A rising reading can be ordinary capacitor charging, so one initial value is not a reliable diagnosis. The readings do not establish operating-voltage leakage, exact component values or insulation ratings.'),
        para('The meter left approximately 0.43 V, 0.47 V and 0.63 V after these respective resistance runs. Returning to voltage mode did not discharge the circuit. We measured residual voltage again before later resistance work.'),
        para('Learning point. Start with the circuit topology: a populated board is not a bare resistor. Retain settling behavior and distinguish OL from a valid number.')])

    page('5 Applying current limited power',[
        para('The board was powered at the accepted project input of 8.00 V RAW. A 50 mA current limit bounded the initial experiment. Overcurrent trip was disabled during the bounded runs so constant-current limiting remained available; unexpected limiting would stop the test.'),
        figure('power-rails','Figure 5. Independent meter readings at the PCB show the regulator reducing RAW to the nominal +5 V rail. Supply telemetry alone would not establish the voltage at either PCB test point.'),
        table(['Quantity','Measured result','Interpretation'],[
            ['RAW at TP2','7.983436 to 7.983857 V','Power reaches the board input'],
            ['+5 V at TP3','4.999728 to 5.000676 V','Regulated rail passes the selected 4.75 to 5.25 V screen'],
            ['Supply current','35 to 36 mA in released-state status reads','Normal observed populated-board load without final devices'],
            ['Cleanup','Output off and 0 V / 0 A read back','The script closed the powered experiment explicitly']
        ],[1.25,2.45,3.45],10),
        para('The current and voltage telemetry were polled at different times. They are not a synchronized startup recording, a peak-current measurement or a thermal test. The display and backlight were absent, so this does not qualify their power budget.'),
        para('Two near-zero VCC attempts were later explained by a disconnected or non-contacting meter lead. Those numbers were invalid as PCB rail measurements. The supply still showed its usual load, which prompted a connection check before declaring a board fault.'),
        para('Closing software does not turn this supply off. Each powered run explicitly disabled output and verified it. Final stored settings were 1.00 V, 50 mA and OCP on, with output OFF. A CC indication while output is OFF is not evidence of a load short.')])

    page('6 Reading the idle PWM waveform',[
        para('TP4 is the raw digital switching signal. At idle it spends approximately half of every cycle HIGH and half LOW. The analog filter uses its average and duty variation; a meter alone cannot show those switching details.'),
        figure('idle-pwm-annotated','Figure 6. Actual RAW samples with period, HIGH duration and voltage plateaus annotated. This view is a short segment; the numerical evaluation used the complete retained capture.'),
        table(['Measurement','Result','Selected screening limit'],[
            ['Carrier estimate','9,999.7657 Hz','10 kHz ±1 percent'],
            ['Period range','100.000 to 100.040 µs','Every period 98 to 102 µs'],
            ['Duty range','50.04 to 50.08 percent','Every duty 48 to 52 percent'],
            ['LOW / HIGH plateaus','0.1024 V / 4.9163 V','LOW -0.3 to 0.5 V; HIGH 4 to 5.5 V'],
            ['Record','1.2 million samples; 40 ns spacing; 48 ms','478 complete periods evaluated; no ADC clipping detected']
        ],[1.35,2.65,3.15],10),
        para('Carrier and tone are different frequencies. The approximately 10 kHz carrier switches the MCU output. The selected 151.4 Hz CTCSS tone is encoded by changing duty over many carrier cycles. Seeing 10 kHz at TP4 does not mean the radio receives a 10 kHz tone.'),
        para('This was a real-triggered finite capture. It screened idle PWM on the populated board; it did not establish absolute timebase calibration, every startup event or analog tone quality. TP4 was installed and inspected before this measurement.')])

    page('7 Separating filter behavior from probe pickup',[
        para('At idle, TP5 should be mostly steady DC with much less switching ripple than TP4. The two 3.3 kΩ and 100 nF stages have individual unloaded RC corners near 482 Hz, but their loading interacts with the divider and trimmer.'),
        figure('filter-ground-control','Figure 7. Unclipped AC captures with the same nominal 20 MHz bandwidth limit. Brief excursions appear at the filter and also with the probe tip grounded. The two rows are separate acquisitions; no subtraction was used.'),
        para('The nominal loaded ladder predicts 1.558 V DC and about 14.25 mV peak-to-peak idle ripple. TP5 measured 1.536 V DC. Its central 1st-to-99th-percentile span was 24 mV, with 7.17 mV AC RMS in the wider capture.'),
        para('Brief excursions reached -0.268 to +0.288 V. They clipped the first 10 and 50 mV/div attempts; those attempts were retained as incomplete excursion measurements. At 100 mV/div the capture was unclipped.'),
        para('With CH2 tip and ground both on TP1, similar excursions remained: -0.268 to +0.248 V, a 16 mV central span and 4.41 mV AC RMS. This establishes a substantial setup contribution. It does not identify the exact coupling mechanism or prove that the PCB contributes no noise.'),
        para('Learning point. A percentile span excludes tail excursions by definition. Do not describe it as the full peak-to-peak noise, and do not subtract independent peak-to-peak spans to invent a corrected result. Precise residual-noise acceptance remains open.')])

    page('8 Making the filtered tone appear and disappear',[
        para('The NUCLEO simulated the real PTT and bypass closures at the PCB headers. We watched TP5 through five states. The selected 151.4 Hz expectation came from the prior production setting; this campaign did not change that setting or re-read the installed firmware binary.'),
        figure('tone-bypass-sequence','Figure 8. The first 30 ms of each independent 240 ms TP5 capture. Curves use the documented 32-sample average, a 12.8 µs window. These are physical analog signals, not the firmware sine table.'),
        table(['Condition','Tone estimate','Central p-p / averaged RMS'],[
            ['PTT pressed','151.3930 Hz','1.9716 V / 0.7001 V'],
            ['Bypass removed while held','151.3979 Hz','1.9732 V / 0.7000 V'],
            ['Idle, bypass or release','Tone suppressed','About 25 mV / 8.9 to 9.9 mV']
        ],[2.6,1.5,3.05],10),
        para('Bypass removed the tone while PTT remained held; removing bypass restored it. Releasing PTT suppressed it again. This exercised the populated PTT-input path, bypass-input path and filter together. These steady-state captures did not measure their transition latency.'),
        para('Frequency was estimated from a least-squares line through 36 or 37 qualified rising mean crossings. The selected analog screen allowed ±0.2 Hz on the nominal scope timebase. This is not a traceably calibrated frequency or distortion measurement.')])

    page('9 Measuring the loaded radio PTT transistor',[
        figure('ptt-test-circuit','Figure 9. Simplified loaded-PTT test. A temporary 1 kΩ pull-up from TP3 to TP8 gave a calculated load of about 5 mA. No radio was attached.'),
        figure('ptt-timing-annotated','Figure 10. Two examples of synchronized TP7 and TP8 captures. The orange bracket measures between physical waveform edges, rather than between host commands. Plot display is decimated; timing used full-resolution data.'),
        table(['Quantity across 12 transitions','Observed result'],[
            ['Collector LOW / released HIGH','0.08379 to 0.08387 V / 5.0019 to 5.0238 V'],
            ['Input-to-collector delay','3.8424 to 5.2008 ms; all below 25 ms'],
            ['Input LOW with the fixture','Approximately 1.012 V; below the selected 1.5 V screen'],
            ['Capture integrity','600 kpoints per channel at 200 ns; 120 ms; same stopped acquisition']
        ],[3.0,4.15],10),
        para('Three press/release pairs passed in each bypass state, with exactly one appropriate input edge and one collector edge per event. The emitter and base network pulled the collector close to ground under the selected load. The roughly 1 V input LOW includes the deliberate fixture and onboard series resistance.'),
        para('The calculated sink current is about 4.916 mA, using nominal 5 V, the 1 kΩ load and measured collector LOW. This is not an independent current measurement. The actual radio PTT voltage, current and unpowered behavior still require radio-stage acceptance.')])

    page('10 Following tone through the final mixing path',[
        para('TP5 is before the divider and level control. TP6 is the final microphone-audio net after RV1, C3 and R5. CH1 used a ×10 probe at TP5; CH2 used ×1 at TP6, providing a nominal 1 MΩ load for the small output signal.'),
        figure('mixing-and-minimum','Figure 11. Matched-scale comparisons at the tested clockwise setting and the electrically verified minimum. Both channels within each row share a stopped acquisition. Curves show 32-sample averages.'),
        table(['At TP6','Clockwise setting','Verified minimum'],[
            ['Tone / central p-p','151.3995 Hz / 127.7069 mV','1.0479 mV residual span'],
            ['Averaged AC RMS','45.3342 mV','0.1767 mV'],
            ['Mean DC','-0.4537 mV','-0.0578 mV']
        ],[1.5,2.9,2.75],10),
        para('C3 passed the alternating tone while removing the upstream DC level near 1.56 V. With C3 nominally 1 µF, R5 100 kΩ and the 1 MΩ scope input, the coupling time constant is about 1.1 seconds. Six seconds of additional settling were allowed before capture.'),
        para('The specified Bourns 3296W has about 25 turns of travel and its wiper idles at the endpoint. Do not force a hard stop. The owner used 30 gentle counterclockwise turns, then the electrical minimum was verified. RV1 is left there. The tested gain was a coarse functional screen, not exact component-tolerance or radio-deviation acceptance.')])

    page('11 Loading the LED outputs and finding a fixture error',[
        para('Resistors replaced the final LEDs so both output paths could be checked without LED polarity or forward-voltage uncertainty. Each intended load was 1 kΩ across a J6 output and its own return contact. With the onboard 330 Ω resistor, ideal HIGH is 5 × 1000 / 1330 = 3.759 V.'),
        figure('led-load-diagnostic','Figure 12. The measured bypass HIGH changed when the mistaken 10 kΩ fixture load was replaced with a verified 1.0004 kΩ resistor. The high first reading did not establish a PCB defect.'),
        table(['State','PTT output J6-1','Bypass output J6-3'],[
            ['Idle','Approximately 0 V','-0.0184 V'],
            ['PTT only','3.6467 V','Approximately 0 V'],
            ['Both asserted','3.6357 V','3.6461 V'],
            ['Bypass only','Approximately 0 V','3.6465 V'],
            ['Released','Approximately 0 V','-0.0114 V']
        ],[2.1,2.5,2.55],10),
        para('The first bypass HIGH was 4.778 V, outside the selected 3.2 to 4.3 V range for a 1 kΩ load. The isolated resistor measured 9.939 kΩ. A lighter load naturally sits closer to the GPIO HIGH; replacing it resolved the discrepancy. Both driver, series-resistor and J6 return paths then passed.'),
        para('These were forced-triggered static captures, 60,000 samples at 200 ns per channel. They establish steady loaded states, not LED response timing. Actual brightness, color and LED polarity were not tested.'),
        para('A separate scope-restoration error was also caught during the mixing tests. Restoring the probe factor after scale and offset changed those settings again. Explicit recovery and a repeat verified the correction. A cleanup failure must be resolved even when the signal measurement looks good.')])

    pairs=[['C01','TP1','J1-6'],['C02','TP1','J1-7'],['C03','TP1','J2-6'],['C04','TP1','J2-7'],
           ['C05','J1-1','J2-1'],['C06','J1-2','J2-2'],['C07','J1-3','J2-3'],['C08','J1-4','J2-4'],['C09','J1-8','J2-8'],
           ['C10','TP2','J2-2'],['C11','TP6','J2-1'],['C12','TP8','J2-5'],['C13','TP1','J4-1'],['C14','TP3','J4-2'],
           ['C15','TP1','J3-5'],['C16','TP3','J3-4'],['C17','J3-1','Pro Micro 4'],['C18','J3-2','Pro Micro 5'],
           ['C19','J3-3','Pro Micro 6'],['C20','J4-3','Pro Micro 2 / SDA'],['C21','J4-4','Pro Micro 3 / SCL']]
    page('12 Completing the physical connector checks',[
        para('All supply, scope, fixture and temporary-load connections were removed. The shorted meter leads measured 0.163 to 0.166 Ω. The meter was deliberately left in resistance autorange for the owner to check the following physical connections.'),
        table(['Check','One probe','Other probe','Criterion'],[r+['Below 2 Ω'] for r in pairs]+[['N01','J1-5','J2-5','Above 1 kΩ or OL']],
              [.6,1.65,2.65,2.25],9.5),
        para('The owner reported every C01 to C21 check at 0.3 Ω or less, with N01 showing OL. No exceptions or skipped checks were reported. Only the maximum and N01 indication were reported; individual C-row values were not recorded.'),
        para('The low readings connect the measured circuit behavior to the actual cable headers, including the audio, RAW, collector and UI branches. OL at N01 confirms that microphone PTT and radio PTT are not directly shorted together. Semiconductor paths can give finite resistance in other conditions; this is not an insulation test.'),
        para('These are operator-reported numerical observations, separate from the USB-retained waveform and meter captures. The lead contribution is included. The OWON was subsequently restored to DCV, autorange and rate S, with math off.')])

    page('13 What to do next and what remains open',[
        para('The selected pre-wiring screen passed. The useful next step is staged off-board assembly using the final-product wiring guide, while preserving the accepted Grove V4 display and bare EC11 connections. Begin with RV1 at minimum.'),
        figure('integration-next-steps','Figure 13. The PCB checks support this next sequence. Each stage has measurements of its own; passing an earlier block does not establish the later load or radio behavior.'),
        table(['Not established by this campaign','Next practical check'],[
            ['Full UI power and temperature','Add display, controls and LEDs with power off; measure rails/current and regulator temperature under the actual complete load'],
            ['Actual user interface operation','Exercise the real EC11, display traffic, menus, saved settings and indicators after wiring'],
            ['Radio connector and electrical envelope','Map the owned adapters; establish actual PTT voltage/current and available microphone-port current before connecting the radio'],
            ['RF deviation and audio quality','Set the required tone deviation with appropriate radio equipment and check microphone audio and residual switching noise'],
            ['Fault and transient coverage','Loaded reset/watchdog, power-up transients and independently calibrated noise/timebase were not exercised here']
        ],[2.55,4.6],10),
        para('The grounded-probe control limits the precision of the residual-noise claim. The small TP6 signal was measured into the scope input, not the radio. Do not treat its amplitude as the radio deviation setting.'),
        para('Final bench state. The PCB is disconnected from external power and fixtures. RV1 is minimum. The supply reads output OFF with 0 V and 0 A; stored settings are 1 V, 50 mA and OCP on. The meter reads DCV/autorange/S with math off. The NUCLEO was released before its PCB wires were removed.'),
        para('The diagnostic habit to carry forward is to check the whole measurement chain: source, reference, load, probe, instrument state, raw capture and interpretation. A plausible number without a known connection is not an accepted measurement.')])

    page('14 Evidence and repeatable checks',[
        para('The self-contained explanations and figures in this guide can be shared on their own. The repository retains the underlying data, failed attempts, settings, scripts and cleanup records for a deeper review. Paths below are relative to docs/verification/populated-board/2026-11-16.'),
        table(['ID','Evidence group','Primary record or folder'],[
            ['E01','Unpowered supply screening','tp3-to-ground-resistance.json; tp2-to-ground-resistance.json; raw-to-vcc-resistance.json'],
            ['E02','Independent rail measurements','raw-at-pcb.json; vcc-at-pcb.json'],
            ['E03','Idle PWM','idle-pwm/result.json and capture/'],
            ['E04','Filter and ground control','idle-filter-100mv/; grounded-ch2-control/'],
            ['E05','Physical filtered-tone sequence','physical-tone-bypass/result.json'],
            ['E06','Loaded Q1 transitions','loaded-ptt/result.json and per-event ch1/ch2 folders'],
            ['E07','Final mixing and level control','mixing-maximum-b/; mixing-minimum/'],
            ['E08','LED loads and correction','loaded-leds-c/; bypass-led-test-resistor.json; bypass-led-replacement-resistor.json'],
            ['E09','Continuity and final state','connector-operator-results.json; connector-meter-finished.json; supply-final-status.json'],
            ['E10','Offline replay','offline-replay.json: 160 checks passed; no hardware access']
        ],[.5,2.2,4.45],9.5),
        para('Each waveform folder contains RAW BYTE samples and a capture preamble. Voltage is reconstructed as (code - yorigin - yreference) × yincrement. Time is (sample index - xreference) × xincrement + xorigin. Hashes identify retained files; they do not establish calibration.'),
        para('To replay accepted data from the repository root in PowerShell, use a fresh output filename:'),
        {'type':'code','text':'python tools/check-populated-board-evidence.py `\n  docs/verification/populated-board/2026-11-16 `\n  --out NEW_REPLAY.json'},
        para('The live scripts and exact wiring, limits, dependencies and recovery actions are documented in tools/bench/README.md. Do not run a powered command merely to reproduce a picture; its physical setup and preceding checks still apply.'),
        para('Document provenance. PCB and schematic hashes match the retained wiring snapshot. Current installed firmware was physically exercised but not re-read or flashed. Earlier November 13 bare-module tests are historical context, not new validation of this populated board.'),
        {'type':'link','text':'Bourns 3296 manufacturer datasheet for nominal travel and wiper-idle behavior','url':'https://www.bourns.com/docs/Product-Datasheets/3296.pdf'},
        para('Guide figures are derived from retained measurements or explicitly labeled schematic views. No as-built photograph or simulated trace is substituted for a physical result. The accompanying manifest lists the source and delivered-file identities.')])


if __name__=='__main__':
    make_figures()
    make_content()
    (WORK/'guide-content.json').write_text(json.dumps({'title':'Icom CTCSS board bench checks',
        'subtitle':'An illustrated learning guide to the populated PCB tests',
        'date':'16 November 2026','pages':PAGES},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'figures':len(list(FIG.glob('*.png'))),'pages':len(PAGES),'content':str(WORK/'guide-content.json')}))
