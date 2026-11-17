"""Shared Grove V4 mechanical interface; front-view coordinates, millimetres.

The JSON owns dimensions. B2/C1 consume this single definition. In a rear view,
mirror X once: x_rear=80-x_front. Do not mirror the panel's native front-view
coordinates. No 2.1 mm offset is added to hole centers: it is the ear radius.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
DEFINITION=ROOT/'mechanical/interfaces/grove-lcd-v4.json'
DATA=json.loads(DEFINITION.read_text(encoding='utf-8'))

def at(origin, coordinates):
    x,y=origin
    return [(x+a,y+b) for a,b in coordinates]

def holes(origin, all_six=False):
    points=DATA['all_hole_centres_front_mm']
    return at(origin,points if all_six else [points[i] for i in DATA['used_hole_indices']])

def window(origin):
    x,y,w,h=DATA['viewing_area_front_mm'];c=DATA['window_clearance_per_side_mm']
    return (origin[0]+x-c,origin[1]+y-c,w+2*c,h+2*c)

def bezel(origin):
    x,y,w,h=DATA['bezel_outline_front_mm']
    return (origin[0]+x,origin[1]+y,w,h)

def support_depth():
    measured=DATA['measured_pcb_front_to_bezel_front_mm']
    if measured is None:
        raise ValueError('PCB-front to bezel-front measurement is required before generating the depth-corrected mount')
    return measured+DATA['bezel_to_panel_rear_gap_mm']
