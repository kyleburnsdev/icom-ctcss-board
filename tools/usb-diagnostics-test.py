"""Bounded, non-saving Pro Micro bench USB protocol checks; requires pyserial 3.5.

Arduino signal pins must be disconnected (passive measurement probes allowed).
Does not flash, hang, reset, or issue a valid SAVE. Reports firmware state only;
it does not measure PTT latency or waveform continuity. Do not run concurrently
with another serial client or while changing the wiring/power.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import serial

ROOT = Path(__file__).resolve().parents[1]


def fields(line):
    return {key: int(value) for word in line.split() if '=' in word
            for key, value in [word.split('=', 1)]}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(port, report):
    with serial.Serial(port, 115200, timeout=.1, write_timeout=2) as device:
        time.sleep(.2)
        device.reset_input_buffer()

        def reply(timeout=3):
            deadline = time.monotonic() + timeout
            data = bytearray()
            while time.monotonic() < deadline:
                data.extend(device.read(1))
                if data.endswith(b'\n'):
                    line = data.decode('ascii').strip()
                    report['transcript'].append({'reply': line})
                    return line
            raise TimeoutError(f'Incomplete USB reply: {data!r}')

        def send(payload):
            report['transcript'].append({'send_ascii': payload.decode('ascii')})
            device.write(payload)

        def status():
            send(b'STATUS\n')
            line = reply()
            require(line.startswith('CTCSS1 '), f'Wrong identity: {line}')
            return fields(line)

        initial = status()
        require(initial.get('bench') == 1, 'Requires identified bench firmware')
        require(initial['tx'] == initial['fault'] == initial['busy'] == 0,
                f'Requires idle, healthy firmware: {initial}')
        report['initial'] = initial

        def unchanged(state):
            for key in ('saved', 'active', 'tx', 'bypass', 'armed', 'lcd', 'busy', 'fault'):
                require(state[key] == initial[key], f'Unexpected {key}: {state}')

        for command in ('', 'UNKNOWN', 'SAVE', 'SAVE 669', 'SAVE 2542',
                        'SAVE 65536', 'SAVE -1', 'SAVE abc', 'SAVE 1514x',
                        'STATUS extra', 'x' * 80):
            send((command + '\n').encode('ascii'))
            response = reply()
            expected = 'ERR line too long' if len(command) > 39 else (
                'ERR save' if command.startswith('SAVE ') else 'ERR command')
            require(response == expected, f'{command!r}: {response!r}, expected {expected!r}')
            unchanged(status())
        report['checks'].append('invalid commands rejected; state unchanged; parser resynchronized')

        send(b'STA'); time.sleep(.05); send(b'TUS\r\n')
        line = reply()
        require(line.startswith('CTCSS1 '), f'Fragmented command: {line}')
        unchanged(fields(line))
        report['checks'].append('fragmented command and CRLF accepted')

        # Sequential traffic checks content; deliberately stalled reads below
        # exercise backpressure separately. Neither proves physical pin timing.
        started = time.monotonic()
        for _ in range(200):
            unchanged(status())
        report['traffic'] = {'commands': 200, 'elapsed_s': time.monotonic() - started}
        report['checks'].append('200 consecutive STATUS replies preserve state')

        send(b'STATUS\n' * 16)
        time.sleep(.5)
        # AVR USB receive capacity may discard input while the reply endpoint
        # is full. Drain surviving output, then use newline + marker to prove
        # recovery without assuming every flooded command was retained.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            data = device.read(1024)
            if data:
                report['backpressure_raw'].append(data.decode('ascii'))
            else:
                break
        else:
            raise TimeoutError('USB output did not quiesce after bounded flood')
        send(b'\n')
        require(reply() == 'ERR command', 'Parser did not recover after stalled reader')
        unchanged(status())
        report['checks'].append('recovers after 16-command burst and 0.5 s stalled reader')
        report['final'] = status()
        unchanged(report['final'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro', required=True, help='Explicit identified Pro Micro COM port')
    parser.add_argument('--output', required=True, type=Path, help='New report path; never overwritten')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the report before operating; retain partial/failing runs.
    with args.output.open('x', encoding='utf-8') as output:
        paths = [Path(__file__)] + list((ROOT / 'firmware/icom_ctcss').glob('*'))
        report = {'utc': datetime.now(timezone.utc).isoformat(), 'port': args.pro,
                  'scope': 'USB protocol/state only; no electrical measurement',
                  'passed': False, 'checks': [], 'transcript': [], 'backpressure_raw': [],
                  'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in paths if p.is_file()}}
        try:
            run(args.pro, report)
            report['passed'] = True
        except BaseException as error:
            report['error'] = repr(error)
            raise
        finally:
            json.dump(report, output, indent=2)
            output.write('\n')
        print('PASS USB diagnostics:', '; '.join(report['checks']))


if __name__ == '__main__':
    main()
