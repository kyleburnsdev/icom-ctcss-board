"""Exclusive NUCLEO open-drain fixture control with a bounded status lease."""
import threading
import time

from .serial_device import Device


class Fixture:
    def __init__(self, port, report):
        self.device = Device(port, 'fixture', report['fixture_transcript'])
        self.report = report
        self.lock = threading.Lock()
        self.stopping = threading.Event()
        self.expected_drive = 0
        self.error = None
        self.worker = None

    def start(self):
        identity = self.device.command('ID')
        self.report['fixture_identity'] = identity
        if not identity.startswith('STANDIN1 phase=1 board=NUCLEO-F767ZI'):
            raise RuntimeError('Unexpected fixture identity')
        self.device.command('STOP')
        state = self.device.status()
        if state['armed'] or state['drive']:
            raise RuntimeError('Fixture did not release before arming')
        self.device.command('ARM')
        self.worker = threading.Thread(target=self.keepalive, daemon=True)
        self.worker.start()

    def keepalive(self):
        deadline = time.monotonic() + 90
        try:
            while not self.stopping.wait(0.5):
                with self.lock:
                    if time.monotonic() > deadline:
                        self.device.command('STOP')
                        raise TimeoutError('Fixture experiment exceeded 90-second lease-worker budget')
                    state = self.device.status()
                    if state['armed'] != 1 or state['drive'] != self.expected_drive:
                        raise RuntimeError('Fixture drive/armed state changed unexpectedly')
        except BaseException as exc:
            self.error = exc

    def set(self, ptt, bypass):
        self.check()
        with self.lock:
            self.device.command(f'PTT {ptt}')
            self.device.command(f'BYPASS {bypass}')
            self.expected_drive = ptt + 2 * bypass
            state = self.device.status()
            if state['drive'] != self.expected_drive or state['armed'] != 1:
                raise RuntimeError('Fixture command readback mismatch')
        time.sleep(0.2)

    def check(self):
        if self.error is not None:
            raise RuntimeError('Fixture keepalive failed: ' + str(self.error))

    def close(self):
        self.stopping.set()
        if self.worker is not None:
            self.worker.join(timeout=3)
            if self.worker.is_alive():
                raise RuntimeError('Fixture serial worker did not stop')
        try:
            with self.lock:
                self.device.command('STOP')
                self.report['fixture_final'] = self.device.status()
                if self.report['fixture_final']['armed'] or self.report['fixture_final']['drive']:
                    raise RuntimeError('Fixture final release unconfirmed')
        finally:
            self.device.close()

