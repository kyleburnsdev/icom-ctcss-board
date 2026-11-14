"""Send one bounded physical UI gesture through the F767 fixture.

Requires the documented three open-drain control wires and an online display.
This does not read screen text or qualify edge timing. Button gestures can save
settings depending on the current screen; establish that screen before use.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent / 'bench'))
from serial_device import Device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro', required=True)
    parser.add_argument('--standin', required=True)
    parser.add_argument('--action', choices=('short', 'long', 'forward', 'reverse'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    log = []
    fixture = pro = None
    result = {'action': args.action, 'passed': False, 'screen_acceptance': 'requires visual observation'}
    try:
        fixture = Device(args.standin, 'fixture', log)
        assert 'board=NUCLEO-F767ZI' in fixture.command('ID')
        fixture.command('STOP')
        state = fixture.status()
        assert state['armed'] == 0 and state['drive'] == 0
        pro = Device(args.pro, 'arduino', log)
        result['before'] = pro.status()
        assert result['before']['lcd'] == 1 and result['before']['fault'] == 0
        assert result['before']['tx'] == 0 and result['before']['busy'] == 0
        fixture.command('ARM')
        if args.action in ('short', 'long'):
            fixture.command('BUTTON 1')
            time.sleep(.12 if args.action == 'short' else .95)
            fixture.command('BUTTON 0')
        else:
            # Electrical AB 11 -> 01 -> 00 -> 10 -> 11, or reverse.
            sequence = [('ENCA', 1), ('ENCB', 1), ('ENCA', 0), ('ENCB', 0)]
            if args.action == 'reverse':
                sequence = [('ENCB', 1), ('ENCA', 1), ('ENCB', 0), ('ENCA', 0)]
            for signal, pressed in sequence:
                fixture.command(f'{signal} {pressed}')
                time.sleep(.05)
        time.sleep(.3)
        result['after'] = pro.status()
        assert result['after']['lcd'] == 1 and result['after']['fault'] == 0
        assert result['after']['tx'] == 0 and result['after']['busy'] == 0
        result['saved_changed'] = result['before']['saved'] != result['after']['saved']
        result['passed'] = True
    finally:
        try:
            if fixture:
                fixture.command('STOP')
                result['fixture_final'] = fixture.status()
                assert result['fixture_final']['armed'] == 0 and result['fixture_final']['drive'] == 0
        finally:
            if pro:
                pro.close()
            if fixture:
                fixture.close()
            result['transcript'] = log
            (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'transcript'}, indent=2))


if __name__ == '__main__':
    main()
