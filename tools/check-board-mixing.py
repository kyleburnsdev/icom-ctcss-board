"""Final tone path screen under parent RAW power; no radio or PCB USB.

CH1 physical x10 TP5, CH2 physical x1 TP6; grounds TP1; NUCLEO as prior tests.
Remove TP3-to-TP8 load. Operator sets RV1 to the selected endpoint with power off.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from bench.analog_tone import analyze
from bench.fixture_control import Fixture
from bench.rigol_scope import Scope, ownership


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-port',required=True)
    parser.add_argument('--level',choices=['maximum','minimum'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=False)
    report={'passed':False,'settings_restored':False,'fixture_transcript':[],
            'level':args.level,'wiring':__doc__,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'loading':'Nominal x1 scope input 1 MOhm; R5 100 kOhm; no radio',
            'selected_settling_s':6,
            'limits_basis':'Selected assembly screens; nominal full-CW TP6/TP5 amplitude ratio about 0.0758 with 1 MOhm load'}
    fixture=None
    try:
        fixture=Fixture(args.fixture_port,report)
        fixture.start()
        fixture.set(1,0)
        with ownership(),Scope() as scope:
            before=report['scope_before']=scope.status()
            if before['settings'][':TRIG:SWE']=='SING' and before['trigger']!='STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed=[key for key in before['settings'] if key.startswith(':CHAN')]
            changed += [':TIM:SCAL',':TIM:OFFS',':ACQ:MDEP',':ACQ:TYPE',':TRIG:MODE',
                        ':TRIG:SWE',':TRIG:EDG:SOUR',':TRIG:EDG:SLOP',':TRIG:EDG:LEV']
            try:
                scope.running(True)
                for command in [':CHAN1:DISP 1',':CHAN2:DISP 1',':CHAN1:PROB 10',':CHAN2:PROB 1',
                                ':CHAN1:SCAL 0.5',':CHAN1:OFFS -1.5',':CHAN1:COUP DC',':CHAN1:BWL ON',':CHAN1:INV 0',
                                ':CHAN2:SCAL 0.1',':CHAN2:OFFS 0',':CHAN2:COUP DC',':CHAN2:BWL ON',':CHAN2:INV 0',
                                ':TIM:SCAL 0.02',':TIM:OFFS 0',':ACQ:TYPE NORM',':TRIG:MODE EDGE',
                                ':TRIG:SWE NORM',':TRIG:EDG:SOUR CHAN1',':TRIG:EDG:SLOP POS',':TRIG:EDG:LEV 1.5']:
                    scope.write(command)
                time.sleep(.5)
                scope.write(':ACQ:MDEP 600000')
                # C3=1uF, R5=100k and nominal scope load=1M give about 1.1 s.
                # Allow six seconds after fixture assertion and scope setup.
                time.sleep(6)
                fixture.check()
                report['scope_configured']=scope.status()
                scope.write(':SING')
                until=time.monotonic()+5
                while scope.q(':TRIG:STAT')!='STOP':
                    fixture.check()
                    if time.monotonic()>until:
                        raise TimeoutError('No completed filtered-tone trigger')
                    time.sleep(.05)
                channels=[]
                for channel in [1,2]:
                    capture=scope.capture(args.output/f'ch{channel}',channel=channel,single=False,max_points=600000)
                    if scope.q(':TRIG:STAT')!='STOP':
                        raise RuntimeError('Buffer restarted between channel transfers')
                    raw=(args.output/f'ch{channel}'/'waveform.u8').read_bytes()
                    channels.append((raw,capture['preamble']))
                fixture.check()
                for key in ['points','xincrement','xorigin','xreference']:
                    if channels[0][1][key]!=channels[1][1][key]:
                        raise ValueError('Channel axes differ')
                report['filter']=analyze(*channels[0],True,151.4)
                report['output']=analyze(*channels[1],args.level=='maximum',151.4,
                                         active_pp=(.10,.22),active_rms=(.02,.09),
                                         mean_limits=(-.03,.03),suppressed_pp=.02,suppressed_rms=.01)
                report['waveform_sha256']=[hashlib.sha256(c[0]).hexdigest() for c in channels]
                report['ratio']=report['output']['central_pp_v']/report['filter']['central_pp_v']
                report['ratio_passed']=.05<=report['ratio']<=.11 if args.level=='maximum' else report['ratio']<=.015
                report['measurement_passed']=report['filter']['passed'] and report['output']['passed'] and report['ratio_passed']
            finally:
                scope.running(True)
                # Probe-factor changes rescale vertical units on this scope.
                # Restore factors before applying original scales and offsets.
                for channel in [1,2]:
                    key=f':CHAN{channel}:PROB'
                    scope.write(f'{key} {before["settings"][key]}')
                for key in changed:
                    if key.endswith(':PROB'):
                        continue
                    scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger']!='STOP')
                after=report['scope_after']=scope.status()
                report['settings_restored']=(all(after['settings'][k]==before['settings'][k] for k in changed)
                                              and (after['trigger']=='STOP')==(before['trigger']=='STOP'))
                if not report['settings_restored']:
                    raise RuntimeError('Scope restoration mismatch')
        fixture.check()
        report['passed']=report['measurement_passed']
    except (Exception,KeyboardInterrupt) as exc:
        report['error']=type(exc).__name__+': '+str(exc)
    finally:
        if fixture is not None:
            try: fixture.close()
            except BaseException as exc:
                report['cleanup_error']=str(exc)
                report['passed']=False
        (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ['passed','error','cleanup_error','filter','output','ratio','fixture_final']}))
    return 0 if report['passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
