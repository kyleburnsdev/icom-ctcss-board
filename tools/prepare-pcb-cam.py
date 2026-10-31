"""Prepare planar CAM inputs from native Gerber/Excellon exports, never KiCad sources.

Run from the repository root with gerbonara 1.6.3 and Shapely 2.2.
Native artwork stays unmirrored; build-pcb-cam.py performs the face setup once.
"""
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from gerbonara import ExcellonFile, GerberFile
from gerbonara.utils import MM
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'manufacturing/pcb/carvera-air/native-exports'
OUT = ROOT / 'manufacturing/pcb/carvera-air'
ERROR = 0.002
OFFSET = 0.15
TIP = 0.20
ANGLE = 30
DEPTH = 0.10
RADIUS = (TIP + 2*DEPTH*math.tan(math.radians(ANGLE/2)))/2
MASK_TIP = 0.30
MASK_DEPTH = 0.20
MASK_RADIUS = (MASK_TIP + 2*MASK_DEPTH*math.tan(math.radians(15)))/2
MASK_INSET = 0.10
MASK_PITCH = 0.12


def panel(x, y):
    return -y-50, x-50


def artwork(path):
    """Preserve Gerber polarity order, merging adjoining pads and strokes."""
    result = Polygon()
    dark = []
    for obj in GerberFile.open(path).objects:
        for primitive in obj.to_primitives(unit=MM):
            poly = primitive.to_arc_poly().approximate_arcs(max_error=ERROR)
            shape = Polygon([panel(x,y) for x,y in poly.outline])
            assert shape.is_valid
            if primitive.polarity_dark:
                dark.append(shape)
            else:
                result = unary_union([result,*dark]).difference(shape)
                dark = []
    return unary_union([result,*dark])


def polygons(shape):
    return list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]


def boundaries(shape):
    return [list(r.coords) for p in polygons(shape) for r in [p.exterior,*p.interiors]]


def mask_geometry():
    """Pad flashes only, before drilling; never expose connecting tracks.

    Bound the spring tool by the larger rigid-V envelope at the published DOC.
    DOC is commanded overtravel below retained copper Z0 into spring compliance,
    not copper removal depth; coating thickness also contributes to compression.
    The nominal contact tip is 0.3 mm; this allowance leaves extra edge mask.
    """
    pads=[]; paths=[]
    for obj in GerberFile.open(EXPORTS/'icom-ctcss-board-B_Cu.gbl').objects:
        if type(obj).__name__!='Flash': continue
        assert obj.polarity_dark and '.P' in obj.attrs
        pad=unary_union([Polygon([panel(x,y) for x,y in primitive.to_arc_poly().approximate_arcs(max_error=ERROR).outline])
                         for primitive in obj.to_primitives(unit=MM)])
        opening=pad.buffer(-MASK_INSET,quad_segs=24)
        centres=opening.buffer(-MASK_RADIUS,quad_segs=24)
        assert not centres.is_empty,obj.attrs
        lines=boundaries(centres)
        lo,hi=centres.bounds[1],centres.bounds[3]
        y=lo+MASK_PITCH/2
        while y<hi:
            cut=centres.intersection(LineString([(-1,y),(151,y)]))
            lines.extend(list(line.coords) for line in getattr(cut,'geoms',[cut])
                         if line.geom_type=='LineString' and line.length>0.001)
            y+=MASK_PITCH
        swept=unary_union([LineString(line).buffer(MASK_RADIUS,quad_segs=24) for line in lines])
        assert swept.difference(opening.buffer(0.00002)).area<1e-6
        pads.append({'pad':list(obj.attrs['.P']),'boundary':boundaries(pad),'opening':boundaries(opening)})
        paths.extend(lines)
    assert len(pads)==111
    return {'pads':pads,'centerlines':paths,'inset_mm':MASK_INSET,
            'tip_mm':MASK_TIP,'envelope_radius_mm':MASK_RADIUS,'hatch_pitch_mm':MASK_PITCH,
            'spring_overtravel_below_copper_mm':MASK_DEPTH,'rpm':6000,'feed_mm_min':400,'plunge_mm_min':200}


def drawings(holes):
    svg=str(GerberFile.open(EXPORTS/'icom-ctcss-board-F_Silkscreen.gto').to_svg(force_bounds=((50,-200),(150,-50)),bg='white'))
    (EXPORTS/'icom-ctcss-board-top-legend.svg').write_text(svg+'\n')
    (ROOT/'docs/reference/top-legend-clean.svg').write_text(svg+'\n')
    # Assembly view uses the clean legend and current drilled geometry, with
    # no normalized virtual top copper or duplicate footprint fields.
    ns='http://www.w3.org/2000/svg'; ET.register_namespace('',ns)
    tree=ET.fromstring(svg)
    group=tree.find('{'+ns+'}g')
    for hole in holes:
        kx,ky=hole['y']+50,hole['x']+50
        ET.SubElement(group,'{'+ns+'}circle',{'cx':str(kx),'cy':str(-ky),'r':str(hole['diameter']/2),'fill':'white','stroke':'#555','stroke-width':'0.1'})
    ET.indent(tree,space='  ')
    (ROOT/'docs/reference/assembly-top.svg').write_text(ET.tostring(tree,encoding='unicode')+'\n')
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800" viewBox="0 0 190 152">',
           '<rect width="190" height="152" fill="white"/>',
           '<g font-family="sans-serif" font-size="2.7" fill="#172d43">',
           '<text x="20" y="7">CTCSS PCB registration - top panel frame - dimensions mm</text>',
           '<rect x="20" y="20" width="150" height="100" fill="none" stroke="#172d43" stroke-width="0.3"/>']
    for hole in [h for h in holes if h['diameter']>=4]:
        x,y=20+hole['x'],120-hole['y']
        parts.append(f'<circle cx="{x}" cy="{y}" r="{hole["diameter"]/2}" fill="none" stroke="#172d43" stroke-width="0.25"/>')
    for index,(x,y,d) in enumerate([(20,20,4.03),(130,20,4.03),(20,70,4.12),(130,70,4.12)],1):
        sx,sy=20+x,120-y
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="{d/2+1}" fill="none" stroke="#b56b00" stroke-width="0.15" stroke-dasharray="0.8 0.6"/>')
        parts.append(f'<text x="{sx+4}" y="{sy-4}">P{index}/H{index+4} ({x},{y}) D{d}</text>')
    parts.extend([
        '<path d="M20 17 V12 H170 V17 M40 44 V38 H150 V44 M35 50 H29 V100 H35 M17 20 H12 V120 H17" fill="none" stroke="#536778" stroke-width="0.2"/>',
        '<text x="90" y="11">150</text><text x="90" y="37">110</text><text x="22" y="76">50</text><text x="1" y="72">100</text>',
        '<path d="M148 80 H152 M150 78 V82" stroke="#1a7b55" stroke-width="0.3"/>',
        '<text x="122" y="86">J1 pin 1 (130,40)</text>',
        '<text x="20" y="127">XY0: panel lower-left. Jig XY = panel + (0.10,0.10).</text>',
        '<text x="20" y="133">P1/P2: measured pin +0.02..0.04; P3/P4: +0.10..0.15.</text>',
        '<text x="20" y="139">Diameters shown assume measured 4.000 mm pins. Flip x\'=150-x, y\'=y.</text>',
        '<text x="20" y="145">Orange: 1 mm clearance envelope; footprint rule areas enforce exclusions on both copper layers.</text>',
        '</g></svg>'])
    (OUT/'registration.svg').write_text('\n'.join(parts)+'\n')


def main():
    copper = artwork(EXPORTS/'icom-ctcss-board-B_Cu.gbl')
    legend = artwork(EXPORTS/'icom-ctcss-board-F_Silkscreen.gto')
    expanded = copper.buffer(OFFSET,quad_segs=24)
    rings = boundaries(expanded)
    swept = unary_union([LineString(r).buffer(RADIUS,quad_segs=24) for r in rings])
    assert swept.intersection(copper).area < 1e-6
    holes=[]
    for name in ['icom-ctcss-board-PTH.drl','icom-ctcss-board-NPTH.drl']:
        for hole in ExcellonFile.open(EXPORTS/name).objects:
            x,y=panel(hole.x,hole.y)
            holes.append({'x':x,'y':y,'diameter':hole.tool.diameter})
    assert len(holes)==119
    expected=[(20,20,4.03),(130,20,4.03),(20,70,4.12),(130,70,4.12)]
    for x,y,d in expected:
        assert any(abs(h['x']-x)<1e-6 and abs(h['y']-y)<1e-6 and abs(h['diameter']-d)<1e-6 for h in holes)
    drawings(holes)
    # Horizontal laser fill clipped to positive legend, preserving counters.
    # Mark fully cured white mask; qualify settings on the first full board.
    hatch=[]
    lo,hi=legend.bounds[1],legend.bounds[3]
    y=lo+0.025
    while y < hi:
        cut=legend.intersection(LineString([(-1,y),(151,y)]))
        for line in getattr(cut,'geoms',[cut]):
            if line.geom_type=='LineString' and line.length>0.005:
                hatch.append(list(line.coords))
        y+=0.05
    mask=mask_geometry()
    data={'copper_boundaries':boundaries(copper),'isolation_centerlines':rings,'mask_removal':mask,
          'legend_boundaries':boundaries(legend),'legend_hatch':hatch,'holes':holes,
          'settings':{'isolation_offset_mm':OFFSET,'vbit_tip_mm':TIP,'vbit_angle_deg':ANGLE,
                      'isolation_depth_mm':DEPTH,'ideal_cut_width_mm':2*RADIUS,
                      'curve_approximation_mm':ERROR,'legend_hatch_pitch_mm':0.05},
          'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in EXPORTS.iterdir() if p.suffix in ('.gbl','.gto','.drl','.gm1')}}
    (OUT/'cam-inputs.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    report={'source_hashes':data['source_hashes'],'electrical_holes':111,'enclosure_mounts':4,'jig_holes':4,
            'isolation_loops':len(rings),'legend_hatch_segments':len(hatch),'copper_regions':len(polygons(copper)),
            'swept_cutter_copper_intersection_mm2':swept.intersection(copper).area,'settings':data['settings'],
            'mask_pad_count':len(mask['pads']),'mask_centerlines':len(mask['centerlines']),
            'mask_envelope_radius_mm':MASK_RADIUS,
            'qualification':'Planar ideal cutter only; no physical runout, spring preload, height-map, fixture or holder acceptance.'}
    (ROOT/'docs/verification/pcb-cam-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
