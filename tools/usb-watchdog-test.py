"""Repeat bench HANG/watchdog USB recovery without saves or flashing.

Requires pyserial 3.5, bare Pro Micro USB only (D9 passive probe allowed), no
driven inputs/radio. Measures USB recovery/state, never electrical PTT release.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import serial
from serial.tools import list_ports


def status(port, transcript):
    with serial.Serial(port,115200,timeout=.1,write_timeout=1) as device:
        time.sleep(.15)
        device.reset_input_buffer()
        device.write(b'STATUS\n')
        raw=bytearray(); until=time.monotonic()+2
        while not raw.endswith(b'\n'):
            if time.monotonic()>until:
                raise TimeoutError(f'Incomplete STATUS: {raw!r}')
            raw.extend(device.read(1))
        line=raw.decode('ascii').strip(); transcript.append(line)
        if not line.startswith('CTCSS1 '):
            raise RuntimeError(f'Unexpected identity: {line}')
        return {k:int(v) for word in line.split() if '=' in word for k,v in [word.split('=',1)]}


def require(condition,message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro',required=True)
    parser.add_argument('--cycles',type=int,default=5)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not 1<=args.cycles<=10:
        parser.error('--cycles must be 1 through 10')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:
        report={'utc':datetime.now(timezone.utc).isoformat(),'port':args.pro,
                'passed':False,'cycles':[],'transcript':[],
                'scope':'USB watchdog recovery only; no D8 release or bootloader-pin capture',
                'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        try:
            initial=status(args.pro,report['transcript']); report['initial']=initial
            require(initial['bench']==1 and not any(initial[k] for k in ('tx','fault','busy','bypass')),
                    'Requires idle healthy bench firmware with bypass released')
            for cycle in range(args.cycles):
                started=time.monotonic()
                with serial.Serial(args.pro,115200,timeout=.1,write_timeout=1) as device:
                    device.write(b'HANG\n')
                    device.flush()
                # A successful STATUS alone could mean HANG was never acted on.
                # Require an observed disappearance before accepting recovery.
                disappeared=False
                until=time.monotonic()+2
                while time.monotonic()<until:
                    if args.pro not in {port.device for port in list_ports.comports()}:
                        disappeared=True; break
                    time.sleep(.01)
                require(disappeared,'USB disappearance not observed; recovery evidence inconclusive')
                attempts=[]; recovered=None
                while time.monotonic()-started<12:
                    time.sleep(.2)
                    try:
                        recovered=status(args.pro,report['transcript']); break
                    except (serial.SerialException,TimeoutError) as error:
                        attempts.append(type(error).__name__)
                require(recovered is not None,'No USB recovery within 12 seconds; check device/port')
                row={'cycle':cycle+1,'host_recovery_s':time.monotonic()-started,
                     'status':recovered,'reconnect_attempts':attempts,
                     'usb_disappearance_observed':True}
                report['cycles'].append(row)
                require(recovered['saved']==initial['saved'] and recovered['active']==initial['active']
                        and recovered['tx']==0 and recovered['fault']==0 and recovered['armed']==1,
                        f'Unexpected recovered state: {recovered}')
                print(row,flush=True)
            report['final']=status(args.pro,report['transcript'])
            require(report['final']['saved']==initial['saved'] and report['final']['tx']==0
                    and report['final']['fault']==0,'Unexpected final state')
            report['passed']=True
        except BaseException as error:
            report['error']=repr(error)
            raise
        finally:
            json.dump(report,output,indent=2); output.write('\n')


if __name__=='__main__':
    main()
