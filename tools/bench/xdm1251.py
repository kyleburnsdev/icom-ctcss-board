"""Read-only XDM1251 status and bounded DCV polling. See agent-control.md.

No hardware access at import. Requires pyserial 3.5; never sends setup/reset.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import time


def utc():
    return datetime.now(timezone.utc).isoformat()


def identity(raw, firmware):
    fields = raw.strip().split(',')
    if len(fields) != 4 or fields[:2] != ['OWON', 'XDM1251']:
        raise ValueError('Expected OWON XDM1251 identity')
    if fields[3] != firmware:
        raise ValueError('Firmware differs from explicitly selected version')
    return {'manufacturer': fields[0], 'model': fields[1], 'firmware': fields[3]}


def voltage(raw):
    value = float(raw.strip())
    if not math.isfinite(value) or abs(value) > 1000:
        raise ValueError('Non-finite, overload or out-of-envelope DC voltage')
    return value


class Meter:
    def __init__(self, transport, evidence):
        self.transport = transport
        self.evidence = evidence

    def query(self, command):
        # Internal allowlist keeps this helper read-only.
        if command not in {'*IDN?', 'FUNC1?', 'FUNC2?', 'AUTO?', 'RATE?',
                           'CALC:FUNC?', 'CALC:NULL:OFFS?', 'RANGE?', 'MEAS1?'}:
            raise ValueError('Unsupported read-only query')
        started = time.monotonic()
        row = {'command': command, 'started_utc': utc()}
        self.evidence['queries'].append(row)
        try:
            wire = (command + '\n').encode('ascii')
            if self.transport.write(wire) != len(wire):
                raise IOError('Incomplete command write')
            raw = self.transport.read_until(b'\n', size=1024)
            if command == '*IDN?':
                # Never persist instrument serial numbers, including partial IDN.
                fields = raw.split(b',')
                row['raw'] = b','.join(fields[:2] + [b'[redacted]'] + fields[3:]).decode('ascii', errors='backslashreplace')
            else:
                row['raw'] = raw.decode('utf-8', errors='backslashreplace')
            if not raw.endswith(b'\n'):
                raise TimeoutError('Missing complete newline-terminated response; stop without retry')
            return raw.decode('utf-8').strip()
        finally:
            row['roundtrip_s'] = time.monotonic() - started

    def state(self):
        return {key: self.query(command) for key, command in {
            'function': 'FUNC1?', 'secondary': 'FUNC2?', 'auto': 'AUTO?',
            'rate': 'RATE?', 'range': 'RANGE?', 'math': 'CALC:FUNC?', 'offset': 'CALC:NULL:OFFS?',
        }.items()}


def require_dcv(state):
    if state['function'].strip('"').upper() != 'VOLT':
        raise ValueError('DCV polling requires existing DC voltage mode; set it manually')
    if state['math'].strip('"').upper() != 'NONE':
        raise ValueError('DCV polling requires math/relative disabled manually')
    if state['auto'] not in {'0', '1'} or state['rate'] not in {'S', 'M', 'F'}:
        raise ValueError('Unknown range/rate state')


def capture(meter, evidence, count, interval):
    before = meter.state()
    evidence['before'] = before
    require_dcv(before)
    evidence['readings'] = []
    for i in range(count):
        raw = meter.query('MEAS1?')
        evidence['readings'].append({'index': i, 'value_v': voltage(raw)})
        if i + 1 < count:
            time.sleep(interval)
    evidence['after'] = meter.state()
    require_dcv(evidence['after'])
    # The active numeric range may legitimately change during autoranging.
    ignored = {'range'} if before['auto'] == '1' else set()
    if any(evidence['after'][key] != value for key, value in before.items() if key not in ignored):
        raise RuntimeError('Instrument settings changed during polling')
    evidence['status'] = 'characterization_complete'
    evidence['interpretation'] = ('Host-polled displayed DCV values; no conversion timestamps, '
                                  'freshness guarantee, calibration or DUT acceptance established')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'poll-dcv'])
    parser.add_argument('--port', required=True)
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--firmware', default='V1.0.1.0.4')
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--interval', type=float, default=0.5,
                        help='Seconds to wait AFTER each response, not a sample period')
    parser.add_argument('--out', type=Path, required=True, help='New JSON filename; never overwritten')
    args = parser.parse_args()
    if not 1 <= args.count <= 1000 or not math.isfinite(args.interval) or not 0.1 <= args.interval <= 60:
        parser.error('count must be 1..1000; interval must be finite 0.1..60 seconds')
    if args.count * 4 + (args.count - 1) * args.interval + 60 > 600 or args.baud <= 0:
        parser.error('Requested worst-case polling duration exceeds 600 s or invalid baud')
    evidence = {'started_utc': utc(), 'port': args.port, 'baud': args.baud,
                'action': args.action, 'queries': [], 'status': 'incomplete',
                'settings_writes_sent': False, 'requested_count': args.count,
                'interval_after_response_s': args.interval,
                'python_version': platform.python_version(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    # Claim the output before opening hardware; preserve failures in the same file.
    with args.out.open('x', encoding='utf-8') as output:
        try:
            import serial
            evidence['pyserial_version'] = serial.VERSION
            with serial.Serial(args.port, args.baud, timeout=2, write_timeout=2,
                               bytesize=8, parity='N', stopbits=1,
                               xonxoff=False, rtscts=False, dsrdtr=False) as transport:
                meter = Meter(transport, evidence)
                evidence['identity'] = identity(meter.query('*IDN?'), args.firmware)
                if args.action == 'status':
                    evidence['state'] = meter.state()
                    evidence['status'] = 'status_complete'
                else:
                    capture(meter, evidence, args.count, args.interval)
                evidence['session_closed'] = False
            evidence['session_closed'] = True
            code = 0
        except (Exception, KeyboardInterrupt) as exc:
            evidence['error'] = type(exc).__name__ + ': ' + str(exc)
            code = 2
        finally:
            evidence['finished_utc'] = utc()
            json.dump(evidence, output, indent=2, allow_nan=False)
            output.write('\n')
    print(json.dumps({'status': evidence['status'], 'evidence': str(args.out),
                      'error': evidence.get('error')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
