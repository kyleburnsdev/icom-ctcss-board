"""Native Windows KA3005P control through sigrok-cli; see agent-control.md.

No hardware access at import. run explicitly enables output for a bounded capture.
Normal/error cleanup is best effort, not a hardware watchdog.
"""
import argparse
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


FIELDS = ('voltage_target', 'current_limit', 'enabled', 'voltage', 'current',
          'regulation', 'ocp_enabled', 'ovp_enabled')
DEFAULT_EXE = Path.home() / '.local/share/sigrok-cli-nightly-20261105/sigrok-cli.exe'


def decimal_setting(value, maximum, step):
    try:
        number = Decimal(value)
        if not number.is_finite() or not 0 < number <= Decimal(maximum):
            raise ValueError('setting outside the positive nominal range')
        if number % Decimal(step):
            raise ValueError('setting is not a multiple of the device resolution')
        return number
    except InvalidOperation as exc:
        raise ValueError('invalid numeric setting') from exc


@contextmanager
def port_lock(port):
    """Cooperating runners only; native serial clients must still be kept closed."""
    import msvcrt
    path = Path(tempfile.gettempdir()) / f'toolpath-ka3005p-{port}.lock'
    with path.open('a+b') as handle:
        if path.stat().st_size == 0:
            handle.write(b'0'); handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError(f'Another cooperating runner owns {port}') from exc
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


class Supply:
    def __init__(self, exe, port):
        if not re.fullmatch(r'COM[1-9][0-9]*', port):
            raise ValueError('Use an explicit Windows COM port')
        self.base = [str(exe), '--driver', f'korad-kaxxxxp:conn={port}']
        self.port = port

    def call(self, *args, timeout=10):
        completed = subprocess.run([*self.base, *args], capture_output=True,
                                   text=True, timeout=timeout)
        if completed.returncode or completed.stderr.strip():
            # Treat diagnostics as failures: the driver can emit errors with exit 0.
            detail = re.sub(r'(S/?N:\s*)[^\s\]]+', r'\1[redacted]', completed.stderr)
            raise RuntimeError(f'sigrok exit {completed.returncode}: {detail.strip()}')
        return completed.stdout

    def identify(self):
        text = self.call('--show')
        expected = f'korad-kaxxxxp:conn={self.port} - Korad KA3005P '
        if not any(line.startswith(expected) for line in text.splitlines()):
            raise RuntimeError('Expected KA3005P identity not found; no writes sent')
        expected_serial = os.environ.get('KORAD_SERIAL_NUMBER')
        if expected_serial and f'[S/N: {expected_serial}]' not in text:
            raise RuntimeError('Instrument serial identity differs; no writes sent')

    def state(self):
        args = [arg for field in FIELDS for arg in ('--get', field)]
        values = self.call(*args).splitlines()
        if len(values) != len(FIELDS):
            raise RuntimeError('Incomplete sigrok readback')
        result = {}
        for field, raw in zip(FIELDS, values):
            if field in ('enabled', 'ocp_enabled', 'ovp_enabled'):
                if raw not in ('true', 'false'):
                    raise RuntimeError(f'Invalid boolean readback: {field}')
                result[field] = raw == 'true'
            elif field == 'regulation':
                if raw not in ("'CV'", "'CC'"):
                    raise RuntimeError('Invalid regulation readback')
                result[field] = raw.strip("'")
            else:
                result[field] = float(raw)
                if not math.isfinite(result[field]):
                    raise RuntimeError(f'Invalid numerical readback: {field}')
        return result

    def configure(self, **values):
        self.call('--config', ':'.join(f'{k}={v}' for k,v in values.items()), '--set')

    def off(self):
        self.configure(enabled='no')
        state = self.state()
        if state['enabled']:
            raise RuntimeError('Output shutdown NOT confirmed')
        return state

    def run(self, volts, amps, seconds, ocp):
        # Validate before even an output-off write; preserve state on invalid input.
        volts = decimal_setting(str(volts), '30', '0.01')
        amps = decimal_setting(str(amps), '5', '0.001')
        if isinstance(seconds, bool) or not isinstance(seconds, int) or not 1 <= seconds <= 30:
            raise ValueError('Capture duration must be 1..30 integer seconds')
        if ocp not in ('on', 'off'):
            raise ValueError('Choose OCP on (trip) or off (CC limiting)')
        result = {'requested_voltage_v': float(volts), 'current_limit_a': float(amps)}
        try:
            self.off()
            self.configure(voltage_target=f'{volts:.2f}', current_limit=f'{amps:.3f}',
                           ocp_enabled='yes' if ocp == 'on' else 'no')
            before = self.state()
            if (before['enabled'] or abs(before['voltage_target']-float(volts)) > .0001
                    or abs(before['current_limit']-float(amps)) > .00001
                    or before['ocp_enabled'] != (ocp == 'on')):
                raise RuntimeError('Settings readback mismatch; will not enable output')
            result['before_enable'] = before
            self.configure(enabled='yes')
            enabled = self.state()
            if not enabled['enabled']:
                raise RuntimeError('Output failed to enable or protection tripped')
            result['after_enable'] = enabled
            start = time.monotonic()
            analog = self.call('--time', str(seconds*1000), '-O', 'analog', timeout=seconds+10)
            result['capture_wall_seconds'] = round(time.monotonic()-start, 3)
            result['capture_requested_seconds'] = seconds
            result['analog_output'] = analog
            # Preserve labeled engineering units; never infer synchronized pairs.
            lines = analog.splitlines()
            if not any(line.startswith('V: ') for line in lines) or not any(line.startswith('I: ') for line in lines):
                raise RuntimeError('Capture missing voltage or current telemetry')
            result['after_capture'] = self.state()
            if not result['after_capture']['enabled']:
                raise RuntimeError('Output turned off during acquisition; inspect protection/load')
        finally:
            # This executes on exceptions/Ctrl-C, but not force-kill, host loss or USB loss.
            result['final_state'] = self.off()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=DEFAULT_EXE)
    parser.add_argument('--port', required=True)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('status')
    sub.add_parser('off')
    run = sub.add_parser('run')
    run.add_argument('--volts', required=True)
    run.add_argument('--amps', required=True)
    run.add_argument('--seconds', required=True, type=int)
    run.add_argument('--ocp', required=True, choices=('on','off'))
    args = parser.parse_args()
    try:
        if args.action == 'run':
            decimal_setting(args.volts, '30', '0.01')
            decimal_setting(args.amps, '5', '0.001')
            if not 1 <= args.seconds <= 30:
                raise ValueError('Capture duration must be 1..30 seconds')
        supply = Supply(args.exe, args.port)
        with port_lock(args.port):
            supply.identify()
            if args.action == 'run':
                result = supply.run(args.volts,args.amps,args.seconds,args.ocp)
            else:
                result = supply.off() if args.action == 'off' else supply.state()
        print(json.dumps(result,indent=2))
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({'error':str(exc) or type(exc).__name__,
                          'action':'Use off and verify state; if communication fails, use the physical output/power switch.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
