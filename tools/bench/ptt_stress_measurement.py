"""Evaluate every physical PTT transition in one bounded mixed-activity record."""
import math


def edges(raw,p):
    if len(raw)!=p['points'] or not math.isfinite(p['xincrement']) or not 0<p['xincrement']<=1e-5:
        raise ValueError('Incomplete or insufficient-resolution channel')
    # Fixed physical 2 V threshold avoids estimating LOW from a percentile:
    # sparse keying can occupy less than 10% of the six-second record.
    if not p['yincrement']>0:raise ValueError('Invalid voltage scale')
    threshold=2/p['yincrement']+p['yorigin']+p['yreference']
    if not 0<threshold<255:raise ValueError('2 V threshold outside ADC range')
    rise=[];fall=[]
    for i in range(1,len(raw)):
        at=(i-p['xreference'])*p['xincrement']+p['xorigin']
        if raw[i-1]<threshold<=raw[i]:rise.append(at)
        elif raw[i]<threshold<=raw[i-1]:fall.append(at)
    return rise,fall


def evaluate(input_raw,input_p,output_raw,output_p,pairs):
    for key in ('points','xincrement','xreference','xorigin'):
        if input_p[key]!=output_p[key]:raise ValueError('PTT channel axes differ')
    if input_p['points']*input_p['xincrement']<5:
        raise ValueError('Insufficient mixed-activity record duration')
    ir,iff=edges(input_raw,input_p)
    orise,ofall=edges(output_raw,output_p)
    if any(len(events)!=pairs for events in (ir,iff,orise,ofall)):
        raise ValueError('Missing or extra input/output transitions')
    source=sorted([(t,True) for t in iff]+[(t,False) for t in ir])
    output=sorted([(t,True) for t in orise]+[(t,False) for t in ofall])
    if abs(source[0][0])>.005:
        raise ValueError('First input edge is not the actual trigger')
    end=(len(input_raw)-1-input_p['xreference'])*input_p['xincrement']+input_p['xorigin']
    if end-source[-1][0]<.05:
        raise ValueError('Insufficient observation after last input release')
    latencies=[]
    for i,((at,pressed),(response,level)) in enumerate(zip(source,output)):
        if pressed!=(i%2==0) or level!=pressed:
            raise ValueError('Unexpected transition polarity/order')
        delay=response-at
        if not 0<=delay<=.025:raise ValueError('PTT response outside 0..25 ms')
        if i+1<len(source) and response>=source[i+1][0]:
            raise ValueError('Output response overlaps next input transition')
        latencies.append(delay*1000)
    return {'passed':True,'pairs':pairs,'transitions':len(source),
            'latencies_ms':latencies,'min_latency_ms':min(latencies),
            'max_latency_ms':max(latencies),'sample_interval_s':input_p['xincrement'],
            'edge_resolution_bound_s':2*input_p['xincrement'],
            'post_last_release_observed_s':end-source[-1][0],
            'claim':'All D7/D8 edges in this retained window; D9 and other pins unobserved'}
