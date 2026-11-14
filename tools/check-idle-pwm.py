"""Capture and evaluate bare Pro Micro D9 idle PWM with a DS1202Z-E CH1 x10 probe.

Requires tools/bench/requirements.txt. Arduino USB only, no driven signal inputs;
probe tip D9, ground GND, physical probe x10. Changes/restores scope settings;
replaces the acquisition buffer. Does not operate the Arduino or power supply.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

from bench.rigol_scope import Scope, ownership
from bench.usb_traffic import status_traffic
from bench.tone_measurement import evaluate_tone


def evaluate(raw, p):
    if len(raw) != p['points'] or len(raw) < 10000:
        raise ValueError('Incomplete or insufficient waveform')
    dt = p['xincrement']
    if dt <= 0 or dt > 1e-6:
        raise ValueError('Insufficient sample resolution')
    codes = sorted(raw)
    low, high = codes[len(raw)//10], codes[9*len(raw)//10]
    volts = lambda code: (code-p['yorigin']-p['yreference'])*p['yincrement']
    if high-low < 20:
        raise ValueError('No adequately resolved two-level waveform')
    threshold = (low+high)/2
    rises, falls = [], []
    for index in range(1, len(raw)):
        if raw[index-1] < threshold <= raw[index]:
            rises.append(index)
        elif raw[index] < threshold <= raw[index-1]:
            falls.append(index)
    if len(rises) < 100:
        raise ValueError('Fewer than 100 observed cycles')
    periods = [b-a for a, b in zip(rises, rises[1:])]
    widths, falling = [], 0
    for a, b in zip(rises, rises[1:]):
        while falling < len(falls) and falls[falling] <= a:
            falling += 1
        if falling >= len(falls) or falls[falling] >= b:
            raise ValueError('Missing falling edge within cycle')
        widths.append((falls[falling]-a)/(b-a)*100)
    frequency = (len(rises)-1)/((rises[-1]-rises[0])*dt)
    checks = {
        'carrier_within_selected_1_percent': abs(frequency-10000) <= 100,
        'every_period_98_to_102_us': min(periods)*dt >= 98e-6 and max(periods)*dt <= 102e-6,
        'every_duty_48_to_52_percent': min(widths) >= 48 and max(widths) <= 52,
        'low_level_minus_0_3_to_0_5_v': -.3 <= volts(low) <= .5,
        'high_level_4_to_5_5_v': 4 <= volts(high) <= 5.5,
        'not_adc_clipped': min(raw) > 0 and max(raw) < 255,
    }
    return dict(passed=all(checks.values()), checks=checks, frequency_hz=frequency,
                complete_periods=len(periods), period_min_us=min(periods)*dt*1e6,
                period_max_us=max(periods)*dt*1e6, duty_min_percent=min(widths),
                duty_max_percent=max(widths), low_plateau_v=volts(low),
                high_plateau_v=volts(high), sample_interval_s=dt,
                scope='Idle PWM only; selected coarse limits, not tone accuracy or calibrated jitter')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New run directory')
    parser.add_argument('--pro-stress', help='Explicit Pro Micro port: continuously query STATUS during capture')
    parser.add_argument('--tone-hz', type=float, help='Expected encoded tone with physical PTT held; selects a long capture')
    parser.add_argument('--channel',type=int,choices=(1,2),default=1,help='Scope channel physically connected to D9')
    args = parser.parse_args()
    if args.tone_hz is not None and (not math.isfinite(args.tone_hz) or not 67 <= args.tone_hz <= 254.1):
        parser.error('--tone-hz must be 67.0 through 254.1')
    if args.tone_hz is not None and args.pro_stress:
        parser.error('Tone-mode USB stress is not implemented; use one mode at a time')
    depth = 12000000 if args.tone_hz is not None else 1200000
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'utc': datetime.now(timezone.utc).isoformat(), 'passed': False,
              'wiring': f'USB-powered Pro Micro D9 -> Rigol CH{args.channel} x10; GND -> probe ground',
              'settings_restored': False}
    try:
        with ownership(), Scope() as scope:
            before = scope.status()
            report['before'] = before
            if before['settings'][':TRIG:SWE'] == 'SING' and before['trigger'] != 'STOP':
                raise RuntimeError('Preserve already armed single acquisition')
            changed = [':CHAN1:DISP', ':CHAN2:DISP', ':CHAN1:PROB', ':CHAN1:SCAL',
                       ':CHAN1:OFFS', ':CHAN1:COUP', ':CHAN1:BWL', ':CHAN1:INV',
                       ':TIM:SCAL', ':TIM:OFFS', ':ACQ:MDEP', ':ACQ:TYPE',
                       ':TRIG:MODE', ':TRIG:SWE', ':TRIG:EDG:SOUR',
                       ':TRIG:EDG:SLOP', ':TRIG:EDG:LEV']
            changed=[key.replace(':CHAN1:',f':CHAN{args.channel}:') if key not in (':CHAN1:DISP',':CHAN2:DISP') else key for key in changed]
            try:
                scope.running(True)
                settings=[':CHAN1:PROB 10',
                                ':CHAN1:SCAL 1', ':CHAN1:OFFS -2.5', ':CHAN1:COUP DC',
                                ':CHAN1:BWL OFF', ':CHAN1:INV 0', ':TIM:SCAL 0.002',
                                ':TIM:OFFS 0', ':ACQ:TYPE NORM',
                                ':TRIG:MODE EDGE', ':TRIG:SWE NORM',
                                ':TRIG:EDG:SOUR CHAN1', ':TRIG:EDG:SLOP POS',
                                ':TRIG:EDG:LEV 2.5']
                scope.write(f':CHAN{args.channel}:DISP 1');scope.write(f':CHAN{3-args.channel}:DISP 0')
                for setting in settings:
                    scope.write(setting.replace(':CHAN1:',f':CHAN{args.channel}:').replace('SOUR CHAN1',f'SOUR CHAN{args.channel}'))
                time.sleep(.4)
                if args.tone_hz is not None:
                    scope.write(':TIM:SCAL 0.5')
                    time.sleep(.2)
                # Channel-enable changes alter the depth choices asynchronously.
                # Wait for the single-channel configuration before selecting depth.
                if scope.q(f':CHAN{args.channel}:DISP') != '1' or scope.q(f':CHAN{3-args.channel}:DISP') != '0':
                    raise RuntimeError('Scope channel configuration did not settle')
                scope.write(f':ACQ:MDEP {depth}')
                time.sleep(.2)
                report['configured'] = scope.status()
                if report['configured']['settings'][':ACQ:MDEP'] != str(depth):
                    raise RuntimeError('Scope did not accept selected memory depth')
                with status_traffic(args.pro_stress, report):
                    result = scope.capture(args.output/'capture', channel=args.channel,single=True,
                                           trigger_timeout=15 if args.tone_hz is not None else 5,
                                           max_points=depth)
                rawpath = args.output/'capture/waveform.u8'
                if args.tone_hz is None:
                    report['measurement'] = evaluate(rawpath.read_bytes(), result['preamble'])
                else:
                    report['measurement'] = evaluate_tone(rawpath.read_bytes(), result['preamble'], args.tone_hz)
                report['waveform_sha256'] = hashlib.sha256(rawpath.read_bytes()).hexdigest()
                scope.screenshot(args.output/'scope.bmp')
            finally:
                scope.running(True)  # memory depth changes take effect while running
                for key in changed:
                    scope.write(f'{key} {before["settings"][key]}')
                scope.running(before['trigger'] != 'STOP')
                after = scope.status()
                report['after'] = after
                mismatches = {key: [before['settings'][key], after['settings'][key]]
                              for key in changed if before['settings'][key] != after['settings'][key]}
                report['settings_restored'] = not mismatches and ((after['trigger'] == 'STOP') == (before['trigger'] == 'STOP'))
                if not report['settings_restored']:
                    raise RuntimeError(f'Scope restoration mismatch: {mismatches}')
            report['passed'] = report['measurement']['passed'] and report['settings_restored']
    except BaseException as error:
        report['error'] = repr(error)
        raise
    finally:
        (args.output/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report['measurement'], indent=2))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
