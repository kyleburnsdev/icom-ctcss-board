"""USB and wired phase-one tests. Requires pyserial 3.5; never flashes boards.

Run --help. Results contain timestamps and source hashes. Physical results are
only claimed for the explicitly selected mode. Full mode needs the guide's
four dividers and two open-drain drive wires. Always releases the fixture.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import sys
from datetime import datetime, timezone
import serial

ROOT = Path(__file__).resolve().parents[1]


def fields(line):
    return {k: int(v) for item in line.split() if '=' in item
            for k, v in [item.split('=', 1)] if v.lstrip('-').isdigit()}


class Device:
    def __init__(self, port):
        self.port = port
        self.serial = serial.Serial(port, 115200, timeout=.1, write_timeout=1)
        time.sleep(.15)
        self.serial.reset_input_buffer()

    def command(self, command, prefix=None, timeout=2):
        self.serial.write((command+'\n').encode('ascii'))
        return self.read(prefix, timeout)

    def read(self, prefix=None, timeout=2):
        until = time.monotonic()+timeout
        while time.monotonic() < until:
            line = self.serial.readline().decode('ascii', errors='replace').strip()
            if line.startswith('ERR'):
                raise RuntimeError(f'{self.port}: {line}')
            if line and (prefix is None or line.startswith(prefix)):
                return line
        raise TimeoutError(f'{self.port}: no {prefix or "reply"}')

    def status(self):
        return fields(self.command('STATUS'))

    def save(self, tone):
        self.command(f'SAVE {tone}', 'OK')
        until = time.monotonic()+2
        while time.monotonic() < until:
            s = self.status()
            if not s['busy']:
                assert s['saved'] == tone, s
                return s
            time.sleep(.02)
        raise TimeoutError('EEPROM save did not finish')

    def close(self):
        self.serial.close()


def run(args, result):
    pro = Device(args.pro)
    standin = Device(args.standin) if args.standin else None
    original = None
    def record(name, data):
        result['checks'].append({'name': name, 'data': data})
        print(name, data, flush=True)
    try:
        initial = pro.status()
        assert initial.get('bench') == 1 and initial['fault'] == 0, initial
        assert initial['tx'] == 0, 'Release PTT before starting'
        original = initial['saved']
        record('initial', initial)
        if standin:
            record('fixture_identity', standin.command('ID', 'STANDIN1'))
            standin.command('STOP', 'OK')
        if args.mode == 'usb':
            if standin:
                standin.command('ARM', 'OK')
                standin.command('PTT 1', 'OK')
                s = standin.status(); assert s['armed'] == 1 and s['drive'] == 1, s
                standin.command('BOUNCE 0', 'OK'); time.sleep(.03)
                s = standin.status(); assert s['drive'] == 0 and not s['bouncing'], s
                assert s['bounce_late_us'] < 100, s
                record('fixture_bounce_scheduler_without_wires', s)
                standin.command('PTT 1', 'OK')
                time.sleep(5.2)
                s = standin.status(); assert s['armed'] == 0 and s['drive'] == 0, s
                record('fixture_host_lease_expiry_without_wires', s)
            for tone in (670, 1514, 2541, 1000):
                s = pro.save(tone)
                assert s['active'] == tone and s['tx'] == 0, s
                record(f'usb_save_{tone}', s)
            # WDT resets USB. Wait for re-enumeration, then reopen the same port.
            pro.serial.write(b'HANG\n')
            pro.close()
            start = time.monotonic()
            while time.monotonic()-start < 12:
                time.sleep(.2)
                try:
                    pro = Device(args.pro)
                    s = pro.status()
                    break
                except (serial.SerialException, TimeoutError):
                    pro.close()
            else:
                raise TimeoutError('Watchdog recovery: device did not return')
            assert s['saved'] == 1000 and s['tx'] == 0 and not s['fault'], s
            record('usb_watchdog_persistence', {'status': s, 'host_reconnect_s': time.monotonic()-start,
                   'note': 'USB reconnect time is NOT electrical PTT release latency'})
            return
        if not standin:
            raise ValueError('--standin is required for wired tests')
        assert initial['armed'] == 1, initial
        standin.command('ARM', 'OK')

        def measure(tone=None):
            standin.command('MEASURE 3000', 'OK')
            m = fields(standin.read('MEAS', 4))
            assert m['periods'] > 28000 and m['errors'] == 0, m
            # This loose carrier check diagnoses wrong clocks/configuration; tone
            # acceptance below is the actual +/-0.1 Hz requirement.
            assert abs(m['carrier_mHz']-10000000) < 100000, m
            if tone is None:
                assert m['cycles'] == 0 and 48 <= m['min_high_us'] <= m['max_high_us'] <= 52, m
            else:
                assert m['cycles'] > 100 and abs(m['tone_mHz']-tone*100) <= 100, m
                assert m['min_high_us'] < 20 and m['max_high_us'] > 80, m
            return m

        record('idle_pwm', measure())
        for pressed in (1, 0):
            standin.command(f'BOUNCE {pressed}', 'OK'); time.sleep(.04)
            s = standin.status()
            assert not s['bouncing'] and s['bounce_late_us'] < 100, s
            assert (s['sense'] & 3) == (3 if pressed else 0), s
            assert s['latency_valid'] and s['latency_us'] <= 25000, s
            record(f'bounce_{pressed}', s)
        for tone in (670, 1514, 2541):
            pro.save(tone)
            standin.command('PTT 1', 'OK'); time.sleep(.04)
            s = standin.status()
            assert s['sense'] & 3 == 3 and s['latency_valid'] and s['latency_us'] <= 25000, s
            record(f'press_{tone}', s)
            record(f'tone_{tone}', measure(tone))
            standin.command('BYPASS 1', 'OK'); time.sleep(.04)
            s = standin.status(); assert s['sense'] == 7, s
            record(f'bypass_{tone}', measure())
            pro.save(1000 if tone != 1000 else 1514)
            standin.command('BYPASS 0', 'OK'); time.sleep(.04)
            record(f'resume_latched_{tone}', measure(tone))
            standin.command('PTT 0', 'OK'); time.sleep(.04)
            s = standin.status()
            assert s['sense'] == 0 and s['latency_valid'] and s['latency_us'] <= 25000, s
            record(f'release_{tone}', s)
        # Hold PTT through watchdog reset. A hardware input remains held, but
        # neither D8 nor its LED may reassert until release and a fresh press.
        pro.save(1514)
        standin.command('PTT 1', 'OK'); time.sleep(.04)
        assert standin.status()['sense'] & 3 == 3
        pro.serial.write(b'HANG\n')
        deadline = time.monotonic()+1
        while time.monotonic() < deadline:
            if standin.status()['sense'] & 3 == 0:
                break
        else:
            raise AssertionError('Watchdog did not release D8/LED within 1 second')
        released_at = time.monotonic()
        for _ in range(25):
            assert standin.status()['sense'] & 3 == 0, 'Rekey while held after watchdog'
            time.sleep(.1)
        record('held_watchdog_no_rekey', {'observed_release_before_deadline': True,
                                        'observed_released_s': time.monotonic()-released_at})
        standin.command('PTT 0', 'OK'); time.sleep(.04)
        standin.command('PTT 1', 'OK'); time.sleep(.04)
        assert standin.status()['sense'] & 3 == 3
        standin.command('PTT 0', 'OK')
    finally:
        already_failing = sys.exc_info()[0] is not None
        cleanup_errors = []
        if standin:
            try:
                standin.command('STOP', 'OK')
            except Exception as error:
                cleanup_errors.append(f'Fixture STOP: {error}')
            finally:
                standin.close()
        if original is not None:
            # A reset can invalidate the handle; reconnect before restoring.
            pro.close()
            try:
                pro = Device(args.pro)
                pro.save(original)
                record('restored_original_tone', original)
            except Exception as error:
                cleanup_errors.append(f'Restore original tone: {error}')
            finally:
                pro.close()
        else:
            pro.close()
        if cleanup_errors:
            result['cleanup_errors'] = cleanup_errors
            if not already_failing:
                raise RuntimeError('; '.join(cleanup_errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro', required=True)
    parser.add_argument('--standin')
    parser.add_argument('--mode', choices=('usb', 'wired'), default='usb')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    files = list((ROOT/'firmware/icom_ctcss').glob('*')) + [Path(__file__)]
    files += list((ROOT/'firmware/radio_standin/Core').rglob('*'))
    files += [ROOT/'firmware/radio_standin/radio_standin.ioc']
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': args.mode,
              'ports': {'pro': args.pro, 'standin': args.standin}, 'checks': [],
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in files if p.is_file()}, 'passed': False}
    try:
        run(args, result)
        result['passed'] = True
    except Exception as error:
        result['error'] = repr(error)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
