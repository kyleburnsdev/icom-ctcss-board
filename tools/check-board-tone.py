"""NUCLEO-driven TP5 tone/bypass screening under parent-controlled RAW power.

CH1 x10 TP4, CH2 x10 TP5, grounds TP1. Fixture wiring: PF12 through 1k to
J1-5, PF13 through 1k to J5-1, GND TP1. PCB USB disconnected. No radio.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from bench.rigol_scope import Scope, ownership
from bench.fixture_control import Fixture
from bench.analog_tone import analyze




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-port', required=True)
    parser.add_argument('--expected-tone-hz', type=float, default=151.4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.expected_tone_hz) or not 67 <= args.expected_tone_hz <= 254.1:
        parser.error('Expected tone outside project range')
    args.output.mkdir(exist_ok=False)
    report = {'passed': False, 'settings_restored': False, 'fixture_transcript': [], 'states': [],
              'wiring': __doc__, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits_basis': 'Selected carrier analog bring-up screens; saved 151.4 Hz expected from prior production record; absolute timebase unqualified'}
    fixture = None
    try:
        fixture = Fixture(args.fixture_port, report)
        fixture.start()
        with ownership(), Scope() as scope:
            before = report['scope_before'] = scope.status()
            if before['settings'][':TRIG:SWE'] == 'SING' and before['trigger'] != 'STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed = [key for key in before['settings'] if key.startswith(':CHAN')]
            changed += [':TIM:SCAL', ':TIM:OFFS', ':ACQ:MDEP', ':ACQ:TYPE', ':TRIG:MODE',
                        ':TRIG:SWE', ':TRIG:EDG:SOUR', ':TRIG:EDG:SLOP', ':TRIG:EDG:LEV']
            try:
                scope.running(True)
                for command in [':CHAN1:DISP 1', ':CHAN2:DISP 1', ':CHAN1:PROB 10', ':CHAN2:PROB 10',
                                ':CHAN1:SCAL 1', ':CHAN1:OFFS -2.5', ':CHAN1:COUP DC', ':CHAN1:BWL ON', ':CHAN1:INV 0',
                                ':CHAN2:SCAL 0.5', ':CHAN2:OFFS -1.5', ':CHAN2:COUP DC', ':CHAN2:BWL ON', ':CHAN2:INV 0',
                                ':TIM:SCAL 0.02', ':TIM:OFFS 0', ':ACQ:TYPE NORM', ':TRIG:MODE EDGE',
                                ':TRIG:SWE NORM', ':TRIG:EDG:SOUR CHAN1', ':TRIG:EDG:SLOP POS', ':TRIG:EDG:LEV 2.5']:
                    scope.write(command)
                time.sleep(.5)
                scope.write(':ACQ:MDEP 600000')
                time.sleep(.3)
                report['scope_configured'] = scope.status()
                for name, ptt, bypass, active in [('idle',0,0,False), ('ptt',1,0,True),
                                                  ('bypass',1,1,False), ('resume',1,0,True), ('release',0,0,False)]:
                    fixture.set(ptt, bypass)
                    capture = scope.capture(args.output/name, channel=2, single=True, trigger_timeout=5, max_points=600000)
                    fixture.check()
                    raw = (args.output/name/'waveform.u8').read_bytes()
                    row = {'name': name, 'ptt': ptt, 'bypass': bypass,
                           'measurement': analyze(raw, capture['preamble'], active, args.expected_tone_hz),
                           'sha256': hashlib.sha256(raw).hexdigest()}
                    report['states'].append(row)
                    scope.screenshot(args.output/(name+'.bmp'))
                    if not row['measurement']['passed']:
                        raise RuntimeError('Analog tone screen failed at ' + name)
            finally:
                scope.running(True)
                for key in changed:
                    scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger'] != 'STOP')
                after = report['scope_after'] = scope.status()
                report['settings_restored'] = (all(after['settings'][k] == before['settings'][k] for k in changed)
                                               and (after['trigger']=='STOP') == (before['trigger']=='STOP'))
                if not report['settings_restored']:
                    raise RuntimeError('Scope restoration mismatch')
        fixture.check()
        report['passed'] = True
    except (Exception, KeyboardInterrupt) as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        if fixture is not None:
            try:
                fixture.close()
            except BaseException as exc:
                report['cleanup_error'] = str(exc)
                report['passed'] = False
        (args.output/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ['passed','error','cleanup_error','states','fixture_final']}))
    return 0 if report['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
