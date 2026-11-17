"""Bounded XDM1251 in-circuit resistance observation; see bench/README.md.

Changes meter mode and sources its resistance-test current. Requires confirmed
unpowered DUT, COM/V-ohm terminals and fixed probe connections. No DUT pass/fail.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from xdm1251 import Meter, identity, require_dcv, utc, voltage


def resistance(raw):
    value = float(raw)
    if not math.isfinite(value) or value < 0:
        raise ValueError('Invalid resistance response')
    if value == 9.9e37:
        return {'indication': 'overload', 'ohm': None}
    if value > 100_000_000:
        raise ValueError('Unexpected out-of-range resistance response')
    return {'indication': 'numeric', 'ohm': value}


def write(meter, command, evidence):
    evidence['writes'].append({'utc': utc(), 'command': command})
    wire = (command + '\n').encode('ascii')
    if meter.transport.write(wire) != len(wire):
        raise IOError('Incomplete setup write')


def require_resistance(state):
    if (state['function'].strip('"').upper() != 'RES'
            or state['math'].upper() != 'NONE'
            or state['secondary'].strip('"').upper() != 'NONE'
            or state['auto'] != '1' or state['rate'] != 'S'):
        raise ValueError('Unexpected resistance settings')


def observe(meter, evidence):
    evidence['identity'] = identity(meter.query('*IDN?'), 'V1.0.1.0.4')
    evidence['before'] = meter.state()
    require_dcv(evidence['before'])
    if evidence['before']['secondary'].strip('"').upper() != 'NONE':
        raise ValueError('Secondary function must be disabled')
    evidence['pre_voltage_v'] = [voltage(meter.query('MEAS1?')) for _ in range(3)]
    # Selected precondition for this low-voltage PCB, not a general discharge limit.
    if any(abs(v) > 0.05 for v in evidence['pre_voltage_v']):
        raise ValueError('Residual voltage exceeds selected 50 mV screening limit')
    try:
        write(meter, 'CONF:RES AUTO', evidence)
        write(meter, 'RATE S', evidence)
        evidence['resistance_before'] = meter.state()
        require_resistance(evidence['resistance_before'])
        time.sleep(3)
        evidence['readings'] = []
        for i in range(12):
            raw = meter.query('MEAS1?')
            evidence['readings'].append({'index': i, **resistance(raw)})
            if i < 11:
                time.sleep(0.75)
        evidence['resistance_after'] = meter.state()
        require_resistance(evidence['resistance_after'])
    finally:
        write(meter, 'CONF:VOLT:DC AUTO', evidence)
        write(meter, 'RATE S', evidence)
        evidence['after'] = meter.state()
        require_dcv(evidence['after'])
        if evidence['after']['rate'] != 'S' or evidence['after']['auto'] != '1':
            raise ValueError('DCV cleanup settings mismatch')
        evidence['dcv_restored'] = True
        time.sleep(3)
        evidence['post_voltage_v'] = []
        for i in range(4):
            evidence['post_voltage_v'].append(voltage(meter.query('MEAS1?')))
            if i < 3:
                time.sleep(0.75)
    evidence['status'] = 'observation_complete'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--connections', required=True, help='Exact black/red endpoints')
    parser.add_argument('--unpowered-confirmed', action='store_true', required=True,
                        help='Operator checked all sources disconnected, COM/V-ohm leads')
    parser.add_argument('--out', type=Path, required=True, help='New JSON file')
    args = parser.parse_args()
    evidence = {'started_utc': utc(), 'status': 'incomplete', 'port': args.port,
                'connections': args.connections, 'unpowered_confirmed': True,
                'queries': [], 'writes': [], 'dcv_restored': False,
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'meter_helper_sha256': hashlib.sha256(Path(__file__).with_name('xdm1251.py').read_bytes()).hexdigest(),
                'interpretation': 'In-circuit characterization; host polls may repeat conversions; no automatic DUT acceptance'}
    with args.out.open('x', encoding='utf-8') as output:
        try:
            import serial
            evidence['pyserial_version'] = serial.VERSION
            with serial.Serial(args.port, 115200, timeout=2, write_timeout=2) as transport:
                observe(Meter(transport, evidence), evidence)
            evidence['session_closed'] = True
            code = 0
        except (Exception, KeyboardInterrupt) as exc:
            evidence['error'] = type(exc).__name__ + ': ' + str(exc)
            code = 2
        finally:
            evidence['finished_utc'] = utc()
            json.dump(evidence, output, indent=2, allow_nan=False)
            output.write('\n')
    print(json.dumps({'status': evidence['status'], 'dcv_restored': evidence['dcv_restored'],
                      'readings': evidence.get('readings'),
                      'post_voltage_v': evidence.get('post_voltage_v'),
                      'error': evidence.get('error')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
