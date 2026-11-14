"""Tested DS1202Z-E USB capture helper. No hardware access at import.

See tools/bench/README.md. Capture preserves settings, not the old acquisition buffer.
"""
import argparse
from contextlib import contextmanager
import json
import math
from pathlib import Path
import tempfile
import time

SETTINGS = [':TIM:SCAL', ':TIM:OFFS', ':ACQ:MDEP', ':ACQ:TYPE',
            ':TRIG:MODE', ':TRIG:SWE', ':TRIG:EDG:SOUR', ':TRIG:EDG:SLOP',
            ':TRIG:EDG:LEV', ':WAV:SOUR', ':WAV:MODE', ':WAV:FORM',
            ':WAV:STAR', ':WAV:STOP', ':SYST:LOCK']
SETTINGS += [f':CHAN{c}:{q}' for c in (1, 2)
             for q in ('DISP', 'SCAL', 'OFFS', 'PROB', 'COUP', 'BWL', 'INV')]
TRANSFER = [':WAV:SOUR', ':WAV:MODE', ':WAV:FORM', ':WAV:STOP', ':WAV:STAR']


def preamble(text):
    fields = text.strip().split(',')
    if len(fields) != 10:
        raise ValueError('Expected all ten waveform preamble fields')
    values = [float(x) for x in fields]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Nonfinite preamble')
    if (values[0] != 0 or values[1] not in (0, 1, 2) or not values[2].is_integer()
            or not 1 <= values[2] <= 24000000 or values[4] <= 0 or values[7] <= 0):
        raise ValueError(f'Invalid BYTE waveform preamble: {text!r}')
    return dict(zip(('format', 'type', 'points', 'count', 'xincrement', 'xorigin',
                     'xreference', 'yincrement', 'yorigin', 'yreference'), values))


def calibrated(data, p, first=1):
    for i, code in enumerate(data):
        yield ((i + first - 1 - p['xreference']) * p['xincrement'] + p['xorigin'],
               (code - p['yorigin'] - p['yreference']) * p['yincrement'])


@contextmanager
def ownership():
    """Windows advisory lock; also close unrelated VISA/sigrok clients."""
    import msvcrt
    path = Path(tempfile.gettempdir()) / 'toolpath-rigol-ds1202ze.lock'
    with path.open('a+b') as f:
        if not path.stat().st_size:
            f.write(b'0'); f.flush()
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        try:
            yield
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


class Scope:
    def __enter__(self):
        import libusb_package
        libusb_package.get_libusb1_backend()  # initialize PyUSB's cached backend
        import pyvisa
        from pyvisa_py.usb import USBInstrSession
        from pyvisa.rname import ResourceName
        self.rm = pyvisa.ResourceManager('@py')
        candidates = []
        for name in USBInstrSession.list_resources():  # USB only; no network discovery
            r = ResourceName.from_string(name)
            if int(r.manufacturer_id, 0) == 0x1ab1 and int(r.model_code, 0) == 0x0517:
                candidates.append(name)
        if len(candidates) != 1:
            self.rm.close()
            raise RuntimeError(f'Expected exactly one USB 1AB1:0517; found {len(candidates)}')
        self.s = self.rm.open_resource(candidates[0])
        self.s.timeout = 3000
        self.s.chunk_size = 500  # device's USBTMC payload limit, not 52 or default 20 KiB
        self.s.write_termination = '\n'
        self.s.read_termination = '\n'
        try:
            fields = self.q('*IDN').split(',')
            if len(fields) != 4 or fields[1] != 'DS1202Z-E':
                raise RuntimeError('Unexpected instrument model')
            self.identity = dict(manufacturer=fields[0], model=fields[1], firmware=fields[3])
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        self.s.close()
        self.rm.close()

    def q(self, command):
        return self.s.query(command + '?').strip()

    def write(self, command):
        self.s.write(command)

    def running(self, enabled):
        # Reissuing STOP to an already stopped single acquisition changes this
        # firmware's sweep from SING to AUTO. Preserve that completed buffer and
        # sweep by avoiding an unnecessary state command.
        if (self.q(':TRIG:STAT') != 'STOP') == enabled:
            return
        self.write(':RUN' if enabled else ':STOP')
        deadline = time.monotonic() + 3
        while (self.q(':TRIG:STAT') != 'STOP') != enabled:
            if time.monotonic() > deadline:
                raise TimeoutError('Acquisition state did not settle')
            time.sleep(0.05)

    def binary(self, command):
        old = self.s.read_termination
        self.s.read_termination = None
        try:
            return self.s.query_binary_values(command, datatype='B', container=bytes,
                                              chunk_size=500, expect_termination=False)
        finally:
            self.s.read_termination = old

    def status(self):
        return dict(identity=self.identity, trigger=self.q(':TRIG:STAT'),
                    samplerate_hz=float(self.q(':ACQ:SRAT')),
                    settings={q: self.q(q) for q in SETTINGS})

    def errors(self):
        result = []
        for _ in range(20):
            error = self.q(':SYST:ERR')
            if error.startswith('0,'):
                return result
            result.append(error)
        raise RuntimeError('SCPI error queue did not drain')

    def screenshot(self, path):
        # No optional color/invert parameters: preserve user display preferences.
        data = self.binary(':DISP:DATA?')
        if not data.startswith(b'BM'):
            raise RuntimeError('Expected BMP screenshot')
        Path(path).write_bytes(data)

    @contextmanager
    def preserved_transfer(self):
        before = self.status()
        if before['settings'][':TRIG:SWE'] == 'SING' and before['trigger'] != 'STOP':
            raise RuntimeError('An armed single acquisition is in progress; preserve it')
        try:
            yield before
        finally:
            # Lower START first so restoring a smaller STOP is valid.
            self.write(':WAV:STAR 1')
            for cmd in TRANSFER:
                self.write(f'{cmd} {before["settings"][cmd]}')
            self.write(':TRIG:SWE ' + before['settings'][':TRIG:SWE'])
            self.running(before['trigger'] != 'STOP')
            after = self.status()
            mismatches = {k: (v, after['settings'][k]) for k, v in before['settings'].items()
                          if v != after['settings'][k]}
            stopped = after['trigger'] == 'STOP'
            if mismatches or stopped != (before['trigger'] == 'STOP'):
                raise RuntimeError(f'Settings restoration failed: {mismatches}')

    def capture(self, directory, channel=1, mode='raw', single=False, force=False,
                trigger_timeout=5, max_points=24000000):
        if (channel not in (1, 2) or mode not in ('raw', 'screen') or force and not single
                or not 0 < trigger_timeout <= 60 or not 1 <= max_points <= 24000000):
            raise ValueError('Invalid channel, mode, force, timeout or point limit')
        destination = Path(directory)
        destination.mkdir(parents=True, exist_ok=False)
        started = time.monotonic()
        with self.preserved_transfer() as before:
            (destination / 'before.json').write_text(json.dumps(before, indent=2))
            if before['settings'][f':CHAN{channel}:DISP'] != '1':
                raise RuntimeError('Requested channel is disabled; configure the experiment first')
            existing = self.errors()
            if existing:
                raise RuntimeError(f'Preexisting SCPI errors: {existing}')
            if single:
                self.write(':SING')
                time.sleep(0.1)  # allow firmware to arm before forcing/polling
                if force:
                    self.write(':TFOR')
                deadline = time.monotonic() + trigger_timeout
                while self.q(':TRIG:STAT') != 'STOP':
                    if time.monotonic() >= deadline:
                        raise TimeoutError('No completed single acquisition; no waveform accepted')
                    time.sleep(0.05)
            else:
                self.running(False)
            self.write(f':WAV:SOUR CHAN{channel}')
            self.write(':WAV:MODE ' + ('RAW' if mode == 'raw' else 'NORM'))
            self.write(':WAV:FORM BYTE')
            p = preamble(self.q(':WAV:PRE'))
            if p['type'] != (2 if mode == 'raw' else 0):
                raise RuntimeError('Instrument did not select the requested transfer mode')
            points = int(p['points'])
            if points > max_points:
                raise ValueError(f'Record has {points} points, above requested limit {max_points}')
            raw = bytearray()
            for start in range(1, points + 1, 250000):
                if time.monotonic() - started > 120:
                    raise TimeoutError('Capture exceeded 120-second transfer budget')
                stop = min(points, start + 249999)
                self.write(f':WAV:STAR {start}')
                self.write(f':WAV:STOP {stop}')
                data = self.binary(':WAV:DATA?')
                if len(data) != stop - start + 1:
                    raise RuntimeError(f'Short waveform block: {len(data)} != {stop-start+1}')
                raw.extend(data)
            errors = self.errors()
            if errors:
                raise RuntimeError(f'SCPI errors: {errors}')
            (destination / 'waveform.u8').write_bytes(raw)
            result = dict(identity=self.identity, channel=channel, mode=mode,
                          acquisition='forced_single' if force else 'single' if single else 'stopped_buffer',
                          points=len(raw), preamble=p, seconds=time.monotonic()-started,
                          probe_factor=float(before['settings'][f':CHAN{channel}:PROB']),
                          volts_formula='(code - yorigin - yreference) * yincrement',
                          seconds_formula='(zero_based_index - xreference) * xincrement + xorigin')
            (destination / 'capture.json').write_text(json.dumps(result, indent=2))
        result['restored'] = True
        (destination / 'capture.json').write_text(json.dumps(result, indent=2))
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    sub.add_parser('status')
    snap = sub.add_parser('screenshot'); snap.add_argument('path')
    cap = sub.add_parser('capture'); cap.add_argument('directory')
    cap.add_argument('--channel', type=int, choices=(1, 2), default=1)
    cap.add_argument('--mode', choices=('raw', 'screen'), default='raw')
    cap.add_argument('--single', action='store_true')
    cap.add_argument('--force', action='store_true')
    cap.add_argument('--trigger-timeout', type=float, default=5)
    cap.add_argument('--max-points', type=int, default=24000000)
    a = p.parse_args()
    if a.action == 'capture' and (a.force and not a.single or not 0 < a.trigger_timeout <= 60
                                or not 1 <= a.max_points <= 24000000):
        p.error('Force requires single; timeout must be (0,60], max-points 1..24000000')
    with ownership(), Scope() as scope:
        if a.action == 'status':
            result = scope.status()
        elif a.action == 'screenshot':
            scope.screenshot(a.path); result = {'screenshot': a.path}
        else:
            result = scope.capture(a.directory, a.channel, a.mode, a.single, a.force,
                                   a.trigger_timeout, a.max_points)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
