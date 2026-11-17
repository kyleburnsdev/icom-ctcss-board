"""Loaded Q1 response: CH1 x10 TP7, CH2 x10 TP8, grounds TP1.

Use parent RAW power wrapper; 1k load TP3-to-TP8. NUCLEO fixture stays as
for tone testing. No radio, PCB USB or final UI. Replaces acquisition buffers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from bench.fixture_control import Fixture
from bench.ptt_measurement import edges
from bench.rigol_scope import Scope, ownership


def evaluate(input_raw, ip, output_raw, op, pressed):
    for key in ['points','xincrement','xorigin','xreference']:
        if ip[key] != op[key]:
            raise ValueError('Channel axes do not match')
    if min(input_raw) == 0 or max(input_raw) == 255 or min(output_raw) == 0 or max(output_raw) == 255:
        raise ValueError('ADC-clipped channel')
    ir, iff = edges(input_raw, ip)
    outr, outf = edges(output_raw, op)
    source, other_source = (iff, ir) if pressed else (ir, iff)
    destination, other_destination = (outf, outr) if pressed else (outr, outf)
    if len(source) != 1 or len(destination) != 1 or other_source or other_destination:
        raise ValueError('Require exactly one same-polarity input and collector transition')
    def plateau(raw, p, tail):
        count = len(raw)//5
        values = raw[-count:] if tail else raw[:count]
        return (sum(values)/count-p['yorigin']-p['yreference'])*p['yincrement']
    input_before, input_after = [plateau(input_raw,ip,tail) for tail in [False,True]]
    out_before, out_after = [plateau(output_raw,op,tail) for tail in [False,True]]
    input_high, input_low = (input_before,input_after) if pressed else (input_after,input_before)
    output_high, output_low = (out_before,out_after) if pressed else (out_after,out_before)
    latency = destination[0]-source[0]
    checks = {'input_high_4_5_to_5_5_v': 4.5 <= input_high <= 5.5,
              'input_low_below_1_5_v': -.3 <= input_low <= 1.5,
              'collector_released_4_5_to_5_5_v': 4.5 <= output_high <= 5.5,
              'collector_asserted_below_0_4_v': -.3 <= output_low <= .4,
              'latency_at_most_25_ms': 0 <= latency <= .025}
    return {'passed': all(checks.values()), 'checks': checks, 'pressed': pressed,
            'latency_ms': latency*1000, 'input_edge_s': source[0], 'collector_edge_s': destination[0],
            'input_high_v': input_high, 'input_low_v': input_low,
            'collector_high_v': output_high, 'collector_low_v': output_low,
            'nominal_sink_current_ma': (5-output_low),
            'sink_current_basis': '(nominal 5 V minus measured collector LOW) / nominal 1 kOhm; not an independent current measurement',
            'sample_interval_s': ip['xincrement'], 'two_edge_sampling_bound_s': 2*ip['xincrement']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-port', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    report = {'passed': False, 'settings_restored': False, 'fixture_transcript': [], 'transitions': [],
              'wiring': __doc__, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    fixture = None
    try:
        fixture = Fixture(args.fixture_port, report)
        fixture.start()
        with ownership(), Scope() as scope:
            before = report['scope_before'] = scope.status()
            if before['settings'][':TRIG:SWE']=='SING' and before['trigger']!='STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed = [key for key in before['settings'] if key.startswith(':CHAN')]
            changed += [':TIM:SCAL',':TIM:OFFS',':ACQ:MDEP',':ACQ:TYPE',':TRIG:MODE',
                        ':TRIG:SWE',':TRIG:EDG:SOUR',':TRIG:EDG:SLOP',':TRIG:EDG:LEV']
            try:
                scope.running(True)
                for channel in [1,2]:
                    for field,value in [('DISP','1'),('PROB','10'),('SCAL','1'),('OFFS','-2.5'),
                                        ('COUP','DC'),('BWL','ON'),('INV','0')]:
                        scope.write(f':CHAN{channel}:{field} {value}')
                for command in [':TIM:SCAL 0.01',':TIM:OFFS 0',':ACQ:TYPE NORM',
                                ':TRIG:MODE EDGE',':TRIG:SWE NORM',':TRIG:EDG:SOUR CHAN1',
                                ':TRIG:EDG:LEV 2.5']:
                    scope.write(command)
                time.sleep(.5)
                scope.write(':ACQ:MDEP 600000')
                time.sleep(.3)
                report['scope_configured'] = scope.status()
                for bypass in [0,1]:
                    fixture.set(0,bypass)
                    for pair in range(1,4):
                        for pressed in [True,False]:
                            name = f'bypass-{bypass}-pair-{pair}-' + ('press' if pressed else 'release')
                            destination = args.output/name
                            destination.mkdir()
                            scope.running(True)
                            scope.write(':TRIG:EDG:SLOP ' + ('NEG' if pressed else 'POS'))
                            scope.write(':SING')
                            time.sleep(.8)
                            fixture.set(int(pressed),bypass)
                            until = time.monotonic()+5
                            while scope.q(':TRIG:STAT')!='STOP':
                                fixture.check()
                                if time.monotonic()>until:
                                    raise TimeoutError('No completed real input-edge trigger')
                                time.sleep(.05)
                            channels = []
                            for channel in [1,2]:
                                meta = scope.capture(destination/f'ch{channel}',channel=channel,single=False,max_points=600000)
                                if scope.q(':TRIG:STAT')!='STOP':
                                    raise RuntimeError('Scope restarted between synchronized channel reads')
                                raw = (destination/f'ch{channel}'/'waveform.u8').read_bytes()
                                channels.append((raw,meta['preamble']))
                            fixture.check()
                            measured = evaluate(*channels[0],*channels[1],pressed)
                            row = {'name':name,'bypass':bypass,'measurement':measured,
                                   'waveform_sha256':[hashlib.sha256(c[0]).hexdigest() for c in channels]}
                            report['transitions'].append(row)
                            (destination/'measurement.json').write_text(json.dumps(row,indent=2)+'\n')
                            if not measured['passed']:
                                raise RuntimeError('Loaded collector screen failed: '+name)
            finally:
                scope.running(True)
                for key in changed:
                    scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger']!='STOP')
                after = report['scope_after'] = scope.status()
                report['settings_restored'] = (all(after['settings'][k]==before['settings'][k] for k in changed)
                                               and (after['trigger']=='STOP')==(before['trigger']=='STOP'))
                if not report['settings_restored']:
                    raise RuntimeError('Scope restoration mismatch')
        fixture.check()
        report['passed'] = len(report['transitions'])==12
    except (Exception,KeyboardInterrupt) as exc:
        report['error'] = type(exc).__name__+': '+str(exc)
    finally:
        if fixture is not None:
            try:
                fixture.close()
            except BaseException as exc:
                report['cleanup_error'] = str(exc)
                report['passed'] = False
        (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report.get(k) for k in ['passed','error','cleanup_error','transitions','fixture_final']}))
    return 0 if report['passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
