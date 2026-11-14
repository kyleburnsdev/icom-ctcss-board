"""Physical D10 edge to raw-PWM suppression/resumption; no filtered-audio claim."""
from .ptt_measurement import edges


def evaluate(input_raw,input_p,pwm_raw,pwm_p,enabled):
    for key in ('points','xincrement','xreference','xorigin'):
        if input_p[key]!=pwm_p[key]:raise ValueError('Bypass channel axes do not align')
    ir,iff=edges(input_raw,input_p)
    source,other=(iff,ir) if enabled else (ir,iff)
    if len(source)!=1 or other:raise ValueError('Missing or extra bypass input edges')
    edge=source[0]
    rises,falls=edges(pwm_raw,pwm_p)
    duty=[];times=[];periods=[];fall_index=0
    for a,b in zip(rises,rises[1:]):
        while fall_index<len(falls) and falls[fall_index]<=a:fall_index+=1
        if fall_index>=len(falls) or falls[fall_index]>=b:raise ValueError('Missing PWM falling edge')
        periods.append(b-a);times.append(a);duty.append((falls[fall_index]-a)/(b-a))
    pre=[v for t,v in zip(times,duty) if t<edge-.003]
    post=[v for t,v in zip(times,duty) if t>edge+.025]
    if len(pre)<100 or len(post)<100:raise ValueError('Insufficient pre/post bypass observation')
    midpoint=lambda value:abs(value-.5)<=.0050001
    checks={'continuous_carrier':bool(periods) and min(periods)>=98e-6 and max(periods)<=102e-6,
            'not_adc_clipped':min(pwm_raw)>0 and max(pwm_raw)<255}
    result={'bypass_enabled':enabled,'input_edge_s':edge,'midpoint_tolerance_duty_percent':.5,
            'sample_interval_s':pwm_p['xincrement'],'complete_carrier_periods':len(periods),
            'scope':'D10 physical input to raw PWM duty response; excludes analog filter decay'}
    if enabled:
        checks['initially_modulated']=min(pre)<=.2 and max(pre)>=.8
        bad=[i for i,(t,v) in enumerate(zip(times,duty)) if t>=edge and not midpoint(v)]
        start=bad[-1]+1 if bad else next((i for i,t in enumerate(times) if t>=edge),len(times))
        settle=times[start]-edge if start<len(times) and times[-1]-times[start]>=.01 else None
        checks['settled_midpoint_within_25_ms']=settle is not None and 0<=settle<=.025
        checks['final_midpoint']=all(midpoint(v) for v in post)
        result['settled_midpoint_ms']=None if settle is None else settle*1000
    else:
        checks['initially_midpoint']=all(midpoint(v) for v in pre)
        onset=next((t-edge for t,v in zip(times,duty) if t>=edge and not midpoint(v)),None)
        low=1;high=0;span=None
        for t,v in zip(times,duty):
            if t<edge:continue
            low=min(low,v);high=max(high,v)
            if low<=.2 and high>=.8:span=t-edge;break
        checks['modulation_onset_within_25_ms']=onset is not None and 0<=onset<=.025
        checks['both_modulation_extremes_within_25_ms']=span is not None and 0<=span<=.025
        checks['final_modulation']=min(post)<=.2 and max(post)>=.8
        result['modulation_onset_ms']=None if onset is None else onset*1000
        result['full_modulation_span_ms']=None if span is None else span*1000
    result['checks']=checks;result['passed']=all(checks.values())
    return result
