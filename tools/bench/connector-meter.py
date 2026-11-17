"""Prepare/finish a human-paced, unpowered connector continuity checklist.

prepare requires tips shorted off-PCB and all PCB sources disconnected. It
checks the short and intentionally LEAVES RESISTANCE MODE for the operator.
finish restores DCV/autorange/rate S. Neither action powers the PCB.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from xdm1251 import Meter, identity, require_dcv, utc, voltage


def write(meter,command,report):
    report['writes'].append({'utc':utc(),'command':command})
    wire=(command+'\n').encode('ascii')
    if meter.transport.write(wire)!=len(wire):
        raise IOError('Incomplete meter setup write')


def restore(meter,report):
    write(meter,'CONF:VOLT:DC AUTO',report)
    write(meter,'RATE S',report)
    report['after']=meter.state()
    require_dcv(report['after'])
    if report['after']['auto']!='1' or report['after']['rate']!='S':
        raise RuntimeError('DCV cleanup mismatch')
    report['dcv_restored']=True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','finish'])
    parser.add_argument('--port',required=True)
    parser.add_argument('--setup-confirmed',action='store_true',help='Tips shorted off-PCB; PCB disconnected from all sources')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.action=='prepare' and not args.setup_confirmed:
        parser.error('prepare requires confirmed shorted-tip/unpowered setup')
    report={'started_utc':utc(),'action':args.action,'status':'incomplete','queries':[],
            'writes':[],'dcv_restored':False,'port':args.port,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.out.open('x',encoding='utf-8') as output:
        try:
            import serial
            with serial.Serial(args.port,115200,timeout=2,write_timeout=2) as transport:
                meter=Meter(transport,report)
                report['identity']=identity(meter.query('*IDN?'),'V1.0.1.0.4')
                report['before']=meter.state()
                if args.action=='finish':
                    restore(meter,report)
                    report['status']='dcv_restored'
                else:
                    require_dcv(report['before'])
                    if report['before']['secondary'].strip('"').upper()!='NONE':
                        raise RuntimeError('Secondary display must be off')
                    report['shorted_tips_dcv_v']=voltage(meter.query('MEAS1?'))
                    if abs(report['shorted_tips_dcv_v'])>.05:
                        raise RuntimeError('Unexpected voltage on reportedly shorted, isolated tips')
                    ready=False
                    try:
                        write(meter,'CONF:RES AUTO',report)
                        write(meter,'RATE S',report)
                        time.sleep(3)
                        state=report['resistance_state']=meter.state()
                        if state['function'].strip('"').upper()!='RES' or state['math'].upper()!='NONE' or state['auto']!='1':
                            raise RuntimeError('Unexpected resistance settings')
                        report['shorted_tips_ohm']=[]
                        for i in range(8):
                            value=float(meter.query('MEAS1?'))
                            if not math.isfinite(value) or not 0<=value<=2:
                                raise RuntimeError('Shorted tips exceed selected 2 ohm gross-check limit')
                            report['shorted_tips_ohm'].append(value)
                            if i<7: time.sleep(.5)
                        report['after']=meter.state()
                        if any(report['after'][k]!=state[k] for k in state if k!='range'):
                            raise RuntimeError('Meter settings changed during preparation')
                        ready=True
                        report['status']='resistance_mode_left_for_operator'
                        report['handoff']='PCB must stay disconnected from every source; record checklist readings, then run finish before reconnecting power'
                    finally:
                        if not ready: restore(meter,report)
            report['session_closed']=True
            code=0
        except (Exception,KeyboardInterrupt) as exc:
            report['error']=type(exc).__name__+': '+str(exc)
            code=2
        finally:
            report['finished_utc']=utc()
            json.dump(report,output,indent=2,allow_nan=False)
            output.write('\n')
    print(json.dumps({k:report.get(k) for k in ['status','error','shorted_tips_ohm','after','dcv_restored']}))
    return code


if __name__=='__main__':
    raise SystemExit(main())
