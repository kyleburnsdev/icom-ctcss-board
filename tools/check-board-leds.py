"""Loaded J6 driver screening under parent RAW power; PCB USB disconnected.

1k loads J6-1/2 and J6-3/4. CH1 x10 J6-1, CH2 x10 J6-3; grounds TP1.
NUCLEO PTT/bypass fixture unchanged. RV1 stays minimum. No final LEDs or radio.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from bench.fixture_control import Fixture
from bench.rigol_scope import Scope, ownership


def evaluate(raw, p, asserted):
    if len(raw)!=p['points'] or len(raw)<10000:
        raise ValueError('Incomplete or insufficient waveform')
    if min(raw)==0 or max(raw)==255:
        raise ValueError('ADC-clipped waveform')
    mean=(sum(raw)/len(raw)-p['yorigin']-p['yreference'])*p['yincrement']
    low,high=(3.2,4.3) if asserted else (-.3,.4)
    return {'passed':low<=mean<=high,'asserted':asserted,'mean_v':mean,
            'selected_limits_v':[low,high], 'nominal_load_current_ma':mean,
            'current_basis':'Voltage across nominal 1 kOhm; calculated, not independent current measurement'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-port',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=False)
    report={'passed':False,'settings_restored':False,'fixture_transcript':[],'states':[],
            'wiring':__doc__,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'nominal_asserted_v':5*1000/(1000+330)}
    fixture=None
    try:
        fixture=Fixture(args.fixture_port,report)
        fixture.start()
        with ownership(),Scope() as scope:
            before=report['scope_before']=scope.status()
            if before['settings'][':TRIG:SWE']=='SING' and before['trigger']!='STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed=[k for k in before['settings'] if k.startswith(':CHAN')]
            changed += [':TIM:SCAL',':TIM:OFFS',':ACQ:MDEP',':ACQ:TYPE',':TRIG:MODE',
                        ':TRIG:SWE',':TRIG:EDG:SOUR',':TRIG:EDG:SLOP',':TRIG:EDG:LEV']
            try:
                scope.running(True)
                for channel in [1,2]:
                    for field,value in [('DISP','1'),('PROB','10'),('SCAL','1'),('OFFS','-2'),
                                        ('COUP','DC'),('BWL','ON'),('INV','0')]:
                        scope.write(f':CHAN{channel}:{field} {value}')
                for command in [':TIM:SCAL 0.001',':TIM:OFFS 0',':ACQ:TYPE NORM',
                                ':TRIG:MODE EDGE',':TRIG:SWE NORM',':TRIG:EDG:SOUR CHAN1',
                                ':TRIG:EDG:SLOP POS',':TRIG:EDG:LEV 2']:
                    scope.write(command)
                time.sleep(.5)
                scope.write(':ACQ:MDEP 60000')
                time.sleep(.3)
                report['scope_configured']=scope.status()
                for name,ptt,bypass in [('idle',0,0),('ptt',1,0),('both',1,1),('bypass_only',0,1),('released',0,0)]:
                    fixture.set(ptt,bypass)
                    folder=args.output/name
                    folder.mkdir()
                    # Static level test: explicitly force trigger, never claim edge timing.
                    scope.running(True)
                    scope.write(':SING')
                    time.sleep(.2)
                    scope.write(':TFOR')
                    until=time.monotonic()+5
                    while scope.q(':TRIG:STAT')!='STOP':
                        fixture.check()
                        if time.monotonic()>until:
                            raise TimeoutError('Forced static acquisition did not complete')
                        time.sleep(.05)
                    row={'name':name,'ptt':ptt,'bypass':bypass,'acquisition':'forced_single_static_levels', 'measurements':[]}
                    for channel,asserted in [(1,ptt),(2,bypass)]:
                        capture=scope.capture(folder/f'ch{channel}',channel=channel,single=False,max_points=60000)
                        if scope.q(':TRIG:STAT')!='STOP':
                            raise RuntimeError('Buffer restarted between channel reads')
                        raw=(folder/f'ch{channel}'/'waveform.u8').read_bytes()
                        measured=evaluate(raw,capture['preamble'],bool(asserted))
                        measured.update(channel=channel,sha256=hashlib.sha256(raw).hexdigest())
                        row['measurements'].append(measured)
                    fixture.check()
                    report['states'].append(row)
                    (folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n')
                    if not all(r['passed'] for r in row['measurements']):
                        raise RuntimeError('Loaded J6 level screen failed at '+name)
            finally:
                scope.running(True)
                for channel in [1,2]:
                    key=f':CHAN{channel}:PROB'
                    scope.write(f'{key} {before["settings"][key]}')
                for key in changed:
                    if not key.endswith(':PROB'):
                        scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger']!='STOP')
                after=report['scope_after']=scope.status()
                report['settings_restored']=(all(after['settings'][k]==before['settings'][k] for k in changed)
                                              and (after['trigger']=='STOP')==(before['trigger']=='STOP'))
                if not report['settings_restored']:
                    raise RuntimeError('Scope restoration mismatch')
        fixture.check()
        report['passed']=len(report['states'])==5
    except (Exception,KeyboardInterrupt) as exc:
        report['error']=type(exc).__name__+': '+str(exc)
    finally:
        if fixture is not None:
            try: fixture.close()
            except BaseException as exc:
                report['cleanup_error']=str(exc)
                report['passed']=False
        (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ['passed','error','cleanup_error','states','fixture_final']}))
    return 0 if report['passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
