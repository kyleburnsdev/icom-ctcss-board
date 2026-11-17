"""Render recognizable hardware perspective views for the wiring guide.

Python 3.10+, numpy, matplotlib. Illustrative geometry, not manufacturing CAD.
GX16 numbering follows the Renhotec reference linked in the guide; the EC11's
opposing 3/2 terminal groups are established user input. No KiCad changes.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/images/wiring'
BG='#f8fafc';INK='#172b3b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':INK})

def cylinder(ax,x,y,z0,z1,r,color,inner=0,n=72):
    t=np.linspace(0,2*np.pi,n)
    p=lambda radius,a,z:(x+radius*np.cos(a),y+radius*np.sin(a),z)
    for a,b in zip(t[:-1],t[1:]):
        faces=[([p(r,a,z0),p(r,b,z0),p(r,b,z1),p(r,a,z1)],color)]
        for z in [z0,z1]:
            ring=[p(inner,a,z),p(r,a,z),p(r,b,z),p(inner,b,z)] if inner else [(x,y,z),p(r,a,z),p(r,b,z)]
            faces.append((ring,color))
        if inner:faces.append(([p(inner,a,z0),p(inner,b,z0),p(inner,b,z1),p(inner,a,z1)],'#454c53'))
        ax._hardware_faces.extend(faces)

def block(ax,x0,x1,y0,y1,z0,z1,color):
    faces=[[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],
        [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],
        [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)],
        [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],
        [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],
        [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]]
    ax._hardware_faces.extend((face,color) for face in faces)

def finish(fig):
    for ax in fig.axes:
        if hasattr(ax,'_hardware_faces'):
            faces,colors=zip(*ax._hardware_faces)
            ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,shade=True))

def setup(fig,rect,title,elev=35,azim=-65,lim=12):
    ax=fig.add_axes(rect,projection='3d',facecolor=BG)
    ax.set(xlim=(-lim,lim),ylim=(-lim,lim),zlim=(-lim,lim))
    ax.set_box_aspect([1,1,1]);ax.view_init(elev=elev,azim=azim);ax.set_axis_off()
    ax._hardware_faces=[]
    ax.set_title(title,fontweight='bold',fontsize=17,pad=-12)
    return ax

def leader(ax,point,label,xy,color=INK):
    px,py,_=proj3d.proj_transform(*point,ax.get_proj())
    ax.annotate(label,xy=(px,py),xycoords='data',xytext=xy,textcoords='axes fraction',
        fontsize=11.5,color=color,fontweight='bold',ha='left',va='center',zorder=100,
        arrowprops=dict(arrowstyle='-',color=color,lw=1.6),
        bbox=dict(boxstyle='round,pad=.25',fc=BG,ec='none',alpha=.95))

def gx_body(ax,rear=False,female=False):
    cylinder(ax,0,0,-9,0,7.6,'#b5bec7',inner=6.7)
    # Thread ridges, nut and shell shoulder make the round connector recognizable.
    for z in np.arange(-7,-1,.65):cylinder(ax,0,0,z,z+.19,7.9,'#89959f',inner=7.5)
    cylinder(ax,0,0,-8,-6.5,10,'#abb6c1',inner=7.5,n=7)
    cylinder(ax,0,0,-1,0,8.8,'#d4dce2',inner=6.7)
    cylinder(ax,0,0,0,.4,6.6,'#252c31')
    block(ax,-.55,.55,6.1,7.1,.4,1,'#b3bbc3')
    points={str(i+1):(-np.sin(np.deg2rad(25+i*310/6))*4.7,
                         np.cos(np.deg2rad(25+i*310/6))*4.7) for i in range(7)}|{'8':(0,0)}
    mirror=-1 if rear!=female else 1
    for n,(x,y) in points.items():
        x*=mirror
        height=3.3 if rear else (.6 if female else 2.3)
        cylinder(ax,x,y,.4,height,.65,'#d4b56f',inner=.4 if rear or female else 0)
        ax.text(x,y,height+.35,n,ha='center',va='bottom',fontsize=14,
                color='#b61f2d',fontweight='bold',zorder=100)
    return points

def gx():
    fig=plt.figure(figsize=(16,9),facecolor=BG)
    fig.text(.035,.95,'GX16-8 — recognize the body and the solder cups',fontsize=25,fontweight='bold')
    fig.text(.035,.905,'Perspective illustrations; red labels are physical GX16 contact numbers. Use the flat pinout for precise orientation.',fontsize=13)
    ax=setup(fig,[.00,.25,.34,.6],'Male mating face',35,-65)
    gx_body(ax)
    leader(ax,(0,6.6,1),'Locating key',(.05,.90))
    leader(ax,(0,-7,-7),'Mounting nut / threads',(.05,.12))
    ax=setup(fig,[.33,.25,.34,.6],'Female mating face',35,-65)
    gx_body(ax,female=True)
    leader(ax,(0,0,2.3),'Socket openings',(.05,.12))
    ax=setup(fig,[.66,.25,.34,.6],'Male half: rear solder cups',50,-65)
    gx_body(ax,rear=True)
    leader(ax,(0,0,3.3),'Wire solders INTO cup',(.03,.12))
    fig.text(.04,.21,'Read the contact from its insert number, then attach the scheduled wire to the corresponding rear cup.',fontsize=15,fontweight='bold')
    fig.text(.04,.155,'Front and rear positions mirror. A bare metal shell or mounting nut is not a signal terminal.',fontsize=14)
    fig.text(.04,.10,'For the owned MIC/RADIO adapter chain, the continuity worksheet translates GX16 cavity → Icom contact → J1/J2 pin.',fontsize=13)
    finish(fig);fig.savefig(OUT/'gx16-hardware.png',dpi=150,facecolor=BG);plt.close(fig)

def ecbody(ax,underside=False):
    # Shaft upright for recognition; invert the part for a clear solder-side view.
    def b(x0,x1,y0,y1,z0,z1,c):
        block(ax,x0,x1,y0,y1,-z1 if underside else z0,-z0 if underside else z1,c)
    def cy(z0,z1,r,c):cylinder(ax,0,0,-z1 if underside else z0,-z0 if underside else z1,r,c)
    b(-5.5,5.5,-5.5,5.5,-1.5,3.5,'#a9b3be')
    b(-4.7,4.7,-4.7,4.7,-2,-1.5,'#263b36')
    cy(3.5,6.5,3.2,'#aab7c2')
    for z in np.arange(4,6.5,.5):cy(z,z+.15,3.4,'#737f8a')
    cy(6.5,15,2.35,'#d3dbe0')
    for angle in np.linspace(0,2*np.pi,20,endpoint=False):
        x,y=2.36*np.cos(angle),2.36*np.sin(angle)
        zz=[7,14.8];zz=[-z for z in zz] if underside else zz
        ax.plot([x,x],[y,y],zz,color='#778591',lw=.5)
    for x in [-6,6]:b(x-.4,x+.4,-1.2,1.2,-4,1,'#8d9aa6')
    for x in [-2.5,0,2.5]:b(x-.4,x+.4,-5.5,-4.9,-6,-1.5,'#dbc183')
    for x in [-2.5,2.5]:b(x-.4,x+.4,4.9,5.5,-6,-1.5,'#dbc183')

def ec():
    fig=plt.figure(figsize=(16,10),facecolor=BG)
    fig.text(.035,.95,'Your EC11 arrangement — three terminals opposite two',fontsize=25,fontweight='bold')
    fig.text(.035,.905,'Illustrated body, shaft and solder tabs. The 3 + 2 grouping is user-confirmed; dimensions are illustrative.',fontsize=13)
    ax=setup(fig,[.01,.30,.47,.55],'Shaft-side recognition view',25,-60,13)
    ecbody(ax)
    leader(ax,(0,0,14),'Knurled shaft / push to click',(.0,.92))
    leader(ax,(0,-5.3,-5.8),'THREE terminals: rotation',(.0,.22))
    leader(ax,(-6,0,-3),'Mounting ear: no wire',(.00,.07))
    ax=setup(fig,[.49,.30,.49,.55],'Turn over: tabs face toward you',48,-65,11)
    ecbody(ax,True)
    labels=[((-2.5,-5.3,6),'Outer rotation → J3-1, blue',(-.03,.32),'#2563c0'),
            ((0,-5.3,6),'Middle common → J3-5, black',(.05,.14),INK),
            ((2.5,-5.3,6),'Outer → J3-2, yellow',(.55,.31),'#9c7d00'),
            ((-2.5,5.3,6),'Switch → ground jumper',(-.03,.94),INK),
            ((2.5,5.3,6),'Switch → J3-3, violet',(.52,.86),'#864cc4')]
    for point,label,where,color in labels:leader(ax,point,label,where,color)
    # Ground jumper rises clear of the body; it connects tabs, not mounting ears.
    ax.plot([0,0,-7,-7,-2.5],[-5.3,-7,-7,5.3,5.3],[6,7,7,7,6],color=INK,lw=2.8,zorder=100)
    fig.text(.04,.25,'Three-terminal side: middle is the usual common; confirm it with the short meter check before soldering.',fontsize=14,fontweight='bold')
    fig.text(.04,.19,'The two outer rotation leads can swap to set clockwise direction. The two push-switch leads are interchangeable.',fontsize=13)
    fig.text(.04,.13,'Fit one black local jumper from common to one switch terminal. J3-4 (+5 V) has NO contact or wire.',fontsize=14,fontweight='bold')
    fig.text(.04,.07,'No markings or photograph are needed: the guide explains how to identify the common and confirm switch closure.',fontsize=13)
    finish(fig);fig.savefig(OUT/'ec11-hardware.png',dpi=150,facecolor=BG);plt.close(fig)

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    gx();ec()
    print('Rendered gx16-hardware.png and ec11-hardware.png')
