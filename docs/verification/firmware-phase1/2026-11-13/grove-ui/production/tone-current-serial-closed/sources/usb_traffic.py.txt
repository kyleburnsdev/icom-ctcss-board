"""Bounded concurrent STATUS traffic; no saves, resets or input stimulus."""
from contextlib import contextmanager
import threading
import time


@contextmanager
def status_traffic(port, report):
    if port is None:
        yield
        return
    import serial
    stop = threading.Event()
    ready = threading.Event()
    traffic = {'port': port, 'commands': 0, 'replies': [], 'passed': False}
    report['usb_traffic'] = traffic

    def worker():
        try:
            with serial.Serial(port, 115200, timeout=.1, write_timeout=1) as device:
                time.sleep(.2)
                device.reset_input_buffer()
                baseline = None
                traffic['start_monotonic_s'] = time.monotonic()
                deadline = time.monotonic()+20
                while not stop.is_set():
                    if time.monotonic() > deadline:
                        raise TimeoutError('STATUS traffic exceeded 20-second budget')
                    device.write(b'STATUS\n')
                    line = bytearray()
                    until = time.monotonic()+2
                    while not line.endswith(b'\n'):
                        if time.monotonic() >= until:
                            raise TimeoutError('Incomplete STATUS reply during scope capture')
                        line.extend(device.read(1))
                    reply = line.decode('ascii').strip()
                    traffic['replies'].append(reply)
                    if not reply.startswith('CTCSS1 '):
                        raise RuntimeError(f'Unexpected identity: {reply}')
                    values = {k: int(v) for word in reply.split() if '=' in word
                              for k, v in [word.split('=',1)]}
                    if values['bench'] != 1 or any(values[k] for k in ('tx','fault','busy','bypass')):
                        raise RuntimeError(f'Requires idle healthy bench firmware: {reply}')
                    state = {k: values[k] for k in ('saved','active','tx','bypass','armed','lcd','busy','fault')}
                    if baseline is not None and state != baseline:
                        raise RuntimeError(f'State changed during traffic: {reply}')
                    baseline = state
                    traffic['commands'] += 1
                    ready.set()
                traffic['passed'] = traffic['commands'] >= 10
        except BaseException as error:
            traffic['error'] = repr(error)
            ready.set()
        finally:
            traffic['end_monotonic_s'] = time.monotonic()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    try:
        if not ready.wait(4) or 'error' in traffic:
            raise RuntimeError(f'USB traffic failed to start: {traffic.get("error")}')
        traffic['capture_call_start_monotonic_s'] = time.monotonic()
        yield
        traffic['capture_call_end_monotonic_s'] = time.monotonic()
    finally:
        stop.set()
        thread.join(4)
        if thread.is_alive():
            raise RuntimeError('USB worker did not stop')
        if not traffic['passed']:
            raise RuntimeError(f'USB traffic failed: {traffic.get("error", "too few replies")}')
