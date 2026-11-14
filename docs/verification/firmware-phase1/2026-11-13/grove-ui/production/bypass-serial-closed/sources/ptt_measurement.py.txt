"""Evaluate synchronized physical D7/D8 records, without host-command timing."""
import math


def edges(raw,p):
    if len(raw)!=p['points'] or len(raw)<1000:
        raise ValueError('Incomplete/insufficient channel samples')
    if not math.isfinite(p['xincrement']) or not 0<p['xincrement']<=1e-6:
        raise ValueError('Insufficient time resolution')
    codes=sorted(raw);low,high=codes[len(raw)//10],codes[9*len(raw)//10]
    if high-low<20:raise ValueError('Channel does not contain resolved LOW and HIGH states')
    threshold=(low+high)/2
    rise=[];fall=[]
    for index in range(1,len(raw)):
        at=(index-p['xreference'])*p['xincrement']+p['xorigin']
        if raw[index-1]<threshold<=raw[index]:rise.append(at)
        elif raw[index]<threshold<=raw[index-1]:fall.append(at)
    return rise,fall


def evaluate(input_raw,input_p,output_raw,output_p,pressed,bouncing=False):
    for key in ('points','xincrement','xreference','xorigin'):
        if input_p[key]!=output_p[key]:raise ValueError(f'Channel time axes do not align: {key}')
    ir,iff=edges(input_raw,input_p);orr,of=edges(output_raw,output_p)
    source,other_source=(iff,ir) if pressed else (ir,iff)
    destination,other_destination=(orr,of) if pressed else (of,orr)
    expected_source=5 if bouncing else 1
    expected_other=4 if bouncing else 0
    if len(source)!=expected_source or len(destination)!=1 or len(other_source)!=expected_other or other_destination:
        raise ValueError('Expected exactly one input/output transition; missing edges or extra pulses')
    if bouncing:
        ordered=sorted(source+other_source)
        if not all(.0008<=b-a<=.0012 for a,b in zip(ordered,ordered[1:])):
            raise ValueError('Unexpected bounce pulse spacing')
    latency=destination[0]-source[-1]
    return {'passed':0<=latency<=.025,'pressed':pressed,'input_edge_s':source[-1],
            'output_edge_s':destination[0],'latency_ms':latency*1000,
            'bounce_pattern':bouncing,'input_transition_count':len(source)+len(other_source),
            'selected_limit_ms':25,'sample_interval_s':input_p['xincrement'],
            'edge_resolution_bound_s':2*input_p['xincrement'],
            'scope':'Physical D7 to D8 midpoint-threshold latency including qualification; finite record only'}


def watchdog(input_raw,input_p,output_raw,output_p):
    for key in ('points','xincrement','xreference','xorigin'):
        if input_p[key]!=output_p[key]:raise ValueError('Misaligned watchdog channels')
    def physical_edges(raw,p):
        if len(raw)!=p['points'] or not 0<p['xincrement']<=1e-5 or len(raw)*p['xincrement']<5:
            raise ValueError('Incomplete or insufficient watchdog record')
        threshold=2/p['yincrement']+p['yorigin']+p['yreference']
        rising=[];falling=[]
        for i in range(1,len(raw)):
            at=(i-p['xreference'])*p['xincrement']+p['xorigin']
            if raw[i-1]<threshold<=raw[i]:rising.append(at)
            elif raw[i]<threshold<=raw[i-1]:falling.append(at)
        return rising,falling
    ir,iff=physical_edges(input_raw,input_p);orr,of=physical_edges(output_raw,output_p)
    if len(ir)!=4 or len(iff)!=4 or len(of)!=1 or orr:
        raise ValueError('Missing/extra marker edges or output released/rekeyed unexpectedly')
    widths=[fall-rise for rise,fall in zip(ir,iff)]
    if not all(.0008<=width<=.0012 for width in widths):
        raise ValueError('Marker pulse widths not the expected subqualification 1 ms')
    if not iff[-1]<of[0] or iff[-1]-ir[0]>.012:
        raise ValueError('Marker not before output release or marker pattern too long')
    bound=of[0]-iff[-1]
    return {'passed':bound<=1,'release_upper_bound_ms':bound*1000,
            'marker_last_fall_s':iff[-1],'output_fall_s':of[0],
            'marker_pulse_widths_ms':[width*1000 for width in widths],
            'no_output_rekey_in_record':True,'held_after_release_observed_s':
            (len(output_raw)-1-output_p['xreference'])*output_p['xincrement']+output_p['xorigin']-of[0],
            'sample_interval_s':input_p['xincrement'],
            'scope':'Physical pre-HANG marker to D8 LOW is a conservative upper bound, not an exact HANG timestamp'}
