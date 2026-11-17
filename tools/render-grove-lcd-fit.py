"""Draw the independently reviewed Grove interface in both viewing directions."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle

ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'mechanical/interfaces/grove-lcd-v4.json').read_text())
fig,axes=plt.subplots(2,1,figsize=(12,9),layout='constrained')
for ax,rear in zip(axes,[False,True]):
    ax.add_patch(Rectangle((0,0),80,40,fc='#e1e8ed',ec='#294454',lw=1.8))
    def xpos(x,w=0):return 80-x-w if rear else x
    for label,key,color in [('BEZEL','bezel_outline_front_mm','#a8b6c3'),('VIEWING AREA','viewing_area_front_mm','#adcdb4')]:
        x,y,w,h=d[key];ax.add_patch(Rectangle((xpos(x,w),y),w,h,fc=color,ec='#294454'))
        if not rear:ax.text(xpos(x,w)+w/2,y+h-1.5 if label=='BEZEL' else y+h/2,label,ha='center',va='center',fontsize=9)
    for i,(x,y) in enumerate(d['all_hole_centres_front_mm']):
        ax.add_patch(Circle((xpos(x),y),2.1,fc='#e1e8ed',ec='#294454'))
        ax.add_patch(Circle((xpos(x),y),1.15,fc='white',ec='#294454'))
        if i<4:
            ax.text(xpos(x),y+(-5 if y==0 else 5),f'{xpos(x):g}, {y:g}',ha='center',fontsize=10)
            old_y=-2.1 if y==0 else 42.1
            ax.add_patch(Circle((xpos(x),old_y),.9,fill=False,ec='#bd493f',ls='--',lw=1.6))
    ax.add_patch(Rectangle((xpos(17,9),-1),9,11,fc='#fff4da',ec='#8f7840'))
    ax.text(xpos(17,9)+4.5,4,'J1',ha='center',fontsize=9)
    ax.set(xlim=(-7,87),ylim=(-12,52),aspect='equal');ax.grid(alpha=.16)
    ax.set_title(('REAR VIEW — mirror X once, keep Y unchanged' if rear else 'FRONT VIEW — readable LCD, Grove socket at lower left')+'\nBlack holes = drawing; dashed red = failed locator rows',weight='bold')
    ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
fig.suptitle('Grove V4 LCD — hole rows are 40 mm apart; R2.10 is an ear radius',fontsize=15,weight='bold')
out=ROOT/'docs/images/lcd-fit/corrected-front-and-rear.png';fig.savefig(out,dpi=160)
plt.close(fig)

fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
projection=d['measured_pcb_front_to_bezel_front_mm'];gap=d['bezel_to_panel_rear_gap_mm']
ax.add_patch(Rectangle((-projection-gap-3,-10),3,40,fc='#b5c6d4',ec='#294454',lw=2))
ax.add_patch(Rectangle((-projection,0),projection,23.8,fc='#d0d6db',ec='#294454',lw=2))
ax.add_patch(Rectangle((0,-10),1.6,40,fc='#a9c8ae',ec='#294454',lw=2))
ax.annotate('',(-projection,35),(0,35),arrowprops={'arrowstyle':'<->'})
ax.text(-projection/2,36,f'D = {projection:.2f} mm (user measurement)',ha='center',weight='bold',fontsize=13)
ax.annotate('Front face of metal bezel',xy=(-projection,17),xytext=(-15,23),ha='right',arrowprops={'arrowstyle':'->'})
ax.annotate('PCB front face\n(side facing the display)',xy=(0,9),xytext=(5,14),arrowprops={'arrowstyle':'->'})
ax.text(-projection-gap-1.5,-14,'Panel',ha='center');ax.text(.8,-14,'PCB',ha='center')
ax.annotate(f'Selected {gap:.2f} mm gap',xy=(-projection-gap/2,2),xytext=(-13,-4),ha='right',arrowprops={'arrowstyle':'->'})
ax.text(-4,43,'L1 side section — measured projection and selected clearance',ha='center',weight='bold',fontsize=14)
ax.text(-4,-22,f'Support length = {projection:.2f} + {gap:.2f} = {projection+gap:.2f} mm.\nThe 13.5 mm overall module thickness is a different dimension.',ha='center',fontsize=12)
ax.set(xlim=(-29,21),ylim=(-26,47),aspect='equal');ax.axis('off')
fig.savefig(ROOT/'docs/images/lcd-fit/depth-measurement.png',dpi=160);plt.close(fig)
