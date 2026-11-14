"""Qualify ENCA reassigned through 1k to SCL, with XDM1251 across SCL/GND.

Arduino D4 retains its pull-up, but has no fixture drive. No power rails joined.
Meter must already be in DCV, math off, leads COM and voltage jack. Read-only
meter queries only; no modes, supply settings or firmware are changed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import serial
from bench.serial_device import Device
from bench.xdm1251 import Meter, identity, require_dcv, voltage


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro', required=True)
    parser.add_argument('--standin', required=True)
    parser.add_argument('--meter', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(len({args.pro,args.standin,args.meter}) == 3, 'Distinct ports required')
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'utc':datetime.now(timezone.utc).isoformat(), 'passed':False,
              'clamp_command':'ENCA', 'transcript':[], 'meter':{'queries':[]},
              'wiring':'PF15 through 1k to D3/SCL; D4 pulled high; XDM1251 red SCL, black GND',
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    fixture = arduino = None
    try:
        fixture = Device(args.standin, 'fixture', report['transcript'])
        require('board=NUCLEO-F767ZI' in fixture.command('ID'), 'Wrong fixture')
        fixture.command('STOP')
        arduino = Device(args.pro, 'arduino', report['transcript'])
        initial = arduino.status(); report['initial'] = initial
        require(initial['lcd'] == 1 and not any(initial[k] for k in ('tx','bypass','busy','fault')), 'Requires healthy idle display')
        with serial.Serial(args.meter, 115200, timeout=2, write_timeout=2) as transport:
            meter = Meter(transport, report['meter'])
            report['meter']['identity'] = identity(meter.query('*IDN?'), 'V1.0.1.0.4')
            before = meter.state(); require_dcv(before); report['meter']['before'] = before

            def readings(name, armed=False):
                # Polling values are displayed conversions, not time-resolved edges.
                # Settle 1.5 s, keep fixture lease alive, then retain three polls.
                for _ in range(5):
                    if armed:
                        state = fixture.status()
                        require(state['armed']==1 and state['drive']==8, 'Clamp lease/drive changed')
                    time.sleep(.3)
                vals=[]
                for _ in range(3):
                    if armed:
                        state=fixture.status(); require(state['drive']==8 and state['armed']==1,'Clamp released during reading')
                    vals.append(voltage(meter.query('MEAS1?'))); time.sleep(.35)
                report[name]=vals
                return vals

            high=readings('released_before_V')
            require(all(3.5<=v<=5.25 for v in high), 'SCL released HIGH not established; check leads/wiring')
            fixture.command('ARM'); fixture.command('ENCA 1')
            # Toggle bypass to guarantee a changed frame and attempted transaction.
            fixture.command('BYPASS 1'); time.sleep(.1); fixture.command('BYPASS 0')
            low=readings('clamped_V', True)
            require(all(-.1<=v<=.8 for v in low), 'SCL clamp is not a qualified LOW')
            offline=arduino.status(); report['clamped_arduino']=offline
            require(offline['lcd']==0 and offline['tx']==0 and offline['saved']==initial['saved'] and offline['fault']==0,
                    'Display did not go offline cleanly')
            fixture.command('STOP')
            after_high=readings('released_after_V')
            require(all(3.5<=v<=5.25 for v in after_high), 'SCL did not recover HIGH')
            after=meter.state(); report['meter']['after']=after; require_dcv(after)
            require(all(after[k]==v for k,v in before.items() if k!='range' or before['auto']!='1'), 'Meter settings changed')
        report['clamp_checks_passed']=True
    except BaseException as error:
        report['error']=repr(error)
        raise
    finally:
        try:
            if fixture:
                fixture.command('STOP'); report['fixture_final']=fixture.status()
                require(report['fixture_final']['armed']==0 and report['fixture_final']['drive']==0,'Fixture not released')
            if arduino:
                deadline=time.monotonic()+3
                while True:
                    state=arduino.status()
                    if state['lcd']==1: break
                    require(time.monotonic()<deadline,'Display did not recover'); time.sleep(.05)
                report['arduino_final']=state
                require(not any(state[k] for k in ('tx','bypass','busy','fault')), 'Arduino not healthy idle')
                if 'initial' in report:require(state['saved']==report['initial']['saved'],'Saved tone changed')
            report['passed']=report.get('clamp_checks_passed',False) and 'error' not in report
        finally:
            if fixture:fixture.close()
            if arduino:arduino.close()
            (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('transcript','meter')},indent=2))


if __name__=='__main__':
    main()
