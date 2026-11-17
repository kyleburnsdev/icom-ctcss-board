"""Observe TP5 idle DC and ripple; RAW power is owned by check-board-power.py.

CH1 physical x10 tip TP4, CH2 physical x10 tip TP5; both grounds TP1.
No PCB USB or off-board components. Replaces buffers; restores scope settings.
"""
import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
import time

from bench.rigol_scope import Scope, ownership


def expected():
    # R4 and the trimmer's end-to-end resistance load the divider.
    load = 10000 + 1 / (1 / 1000 + 1 / 10000)
    def transfer(f):
        sc = 2j * math.pi * f * 100e-9
        return (1 / 3300**2) / ((2 / 3300 + sc) * (1 / 3300 + 1 / load + sc) - 1 / 3300**2)
    harmonics = [(n, 10 / (math.pi * n) * transfer(n * 10000)) for n in range(1, 64, 2)]
    values = [sum((amplitude * cmath.exp(2j * math.pi * n * i / 2048)).imag
                  for n, amplitude in harmonics) for i in range(2048)]
    return {'assumptions': 'Ideal 0–5 V 50% 10 kHz PWM; nominal 3.3k/100nF sections; 10k upper, 1k lower, 10k trimmer; no probe loading/parasitics',
            'dc_v': 2.5 * transfer(0).real,
            'ripple_pp_v': max(values) - min(values),
            'method': 'Linear ladder transfer; 32 odd harmonics through 630 kHz, sampled at 2048 phases'}


def summarize(raw, p):
    if len(raw) != p['points'] or len(raw) < 10000:
        raise ValueError('Incomplete/insufficient waveform')
    if not 0 < p['xincrement'] <= 1e-6:
        raise ValueError('Insufficient time resolution')
    ordered = sorted(raw)
    convert = lambda code: (code - p['yorigin'] - p['yreference']) * p['yincrement']
    mean_code = sum(raw) / len(raw)
    rms_code = math.sqrt(sum((code - mean_code)**2 for code in raw) / len(raw))
    return {'mean_v': convert(mean_code), 'rms_ac_v': rms_code * p['yincrement'],
            'min_v': convert(min(raw)), 'max_v': convert(max(raw)),
            'percentile_1_to_99_pp_v': (ordered[99 * len(raw) // 100] - ordered[len(raw) // 100]) * p['yincrement'],
            'adc_clipped': min(raw) == 0 or max(raw) == 255,
            'points': len(raw), 'sample_interval_s': p['xincrement'],
            'duration_s': len(raw) * p['xincrement']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--ripple-scale', choices=['0.01', '0.05', '0.1'], default='0.01',
                        help='CH2 AC volts/div; increase to retain excursions without clipping')
    parser.add_argument('--grounded-control', action='store_true',
                        help='CH2 tip and ground both TP1; noise control, not filter acceptance')
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    report = {'passed': False, 'settings_restored': False,
              'wiring': 'CH1 physical x10 TP4; CH2 physical x10 TP5; grounds TP1; RAW only; PCB USB disconnected',
              'calculated_nominal': expected(),
              'limits_basis': 'Selected gross assembly screens; nominal calculation is not a calibrated reference',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if args.grounded_control:
        report['wiring'] = 'CH1 physical x10 TP4; CH2 physical x10 tip and ground TP1; RAW only; PCB USB disconnected'
        report['interpretation'] = 'Grounded-probe noise characterization; no TP5 filter acceptance'
    try:
        with ownership(), Scope() as scope:
            before = report['before'] = scope.status()
            if before['settings'][':TRIG:SWE'] == 'SING' and before['trigger'] != 'STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed = [key for key in before['settings'] if key.startswith(':CHAN')]
            changed += [':TIM:SCAL', ':TIM:OFFS', ':ACQ:MDEP', ':ACQ:TYPE',
                        ':TRIG:MODE', ':TRIG:SWE', ':TRIG:EDG:SOUR', ':TRIG:EDG:SLOP', ':TRIG:EDG:LEV']
            try:
                scope.running(True)
                for command in [':CHAN1:DISP 1', ':CHAN2:DISP 1', ':CHAN1:PROB 10', ':CHAN2:PROB 10',
                                ':CHAN1:SCAL 1', ':CHAN1:OFFS -2.5', ':CHAN1:COUP DC',
                                ':CHAN1:BWL ON', ':CHAN1:INV 0', ':CHAN2:SCAL 0.5', ':CHAN2:OFFS -1.5',
                                ':CHAN2:COUP DC', ':CHAN2:BWL ON', ':CHAN2:INV 0',
                                ':TIM:SCAL 0.0001', ':TIM:OFFS 0', ':ACQ:TYPE NORM',
                                ':TRIG:MODE EDGE', ':TRIG:SWE NORM', ':TRIG:EDG:SOUR CHAN1',
                                ':TRIG:EDG:SLOP POS', ':TRIG:EDG:LEV 2.5']:
                    scope.write(command)
                time.sleep(0.5)
                scope.write(':ACQ:MDEP 600000')
                time.sleep(0.3)
                report['dc_settings'] = scope.status()
                for name, coupling, scale, offset in [('dc', 'DC', '0.1' if args.grounded_control else '0.5', '0' if args.grounded_control else '-1.5'),
                                                       ('ripple', 'AC', args.ripple_scale, '0')]:
                    scope.write(f':CHAN2:COUP {coupling}')
                    scope.write(f':CHAN2:SCAL {scale}')
                    scope.write(f':CHAN2:OFFS {offset}')
                    time.sleep(0.8)
                    report[name + '_settings'] = scope.status()
                    capture = scope.capture(args.output / name, channel=2, single=True,
                                            trigger_timeout=5, max_points=600000)
                    path = args.output / name / 'waveform.u8'
                    raw = path.read_bytes()
                    report[name] = summarize(raw, capture['preamble'])
                    report[name]['sha256'] = hashlib.sha256(raw).hexdigest()
                    scope.screenshot(args.output / (name + '.bmp'))
                report['checks'] = {
                    'dc_between_1_35_and_1_75_v': 1.35 <= report['dc']['mean_v'] <= 1.75,
                    'ripple_percentile_pp_at_most_80_mv': report['ripple']['percentile_1_to_99_pp_v'] <= .08,
                    'ripple_rms_at_most_20_mv': report['ripple']['rms_ac_v'] <= .02,
                    'no_adc_clipping': not report['dc']['adc_clipped'] and not report['ripple']['adc_clipped'],
                    'at_least_10_carrier_periods_each': all(report[key]['duration_s'] >= .001 for key in ['dc', 'ripple'])}
                if args.grounded_control:
                    report['checks'].pop('dc_between_1_35_and_1_75_v')
                    report['checks']['grounded_dc_within_50_mv'] = abs(report['dc']['mean_v']) <= .05
            finally:
                scope.running(True)
                # Restore vertical state before the original trigger level.
                for key in changed:
                    scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger'] != 'STOP')
                after = report['after'] = scope.status()
                report['settings_restored'] = (all(after['settings'][key] == before['settings'][key] for key in changed)
                                               and (after['trigger'] == 'STOP') == (before['trigger'] == 'STOP'))
                if not report['settings_restored']:
                    raise RuntimeError('Scope settings restoration mismatch')
            report['passed'] = all(report['checks'].values()) and report['settings_restored']
    except (Exception, KeyboardInterrupt) as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        (args.output / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report.get(key) for key in ['passed', 'error', 'dc', 'ripple', 'checks', 'calculated_nominal']}))
    return 0 if report['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
