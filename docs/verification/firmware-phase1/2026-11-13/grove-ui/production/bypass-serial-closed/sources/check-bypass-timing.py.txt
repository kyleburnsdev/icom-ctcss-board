"""Measure D10 bypass input -> D9 PWM response; requires CH1=D10, CH2=D9 x10.

Use the minimal F767 fixture, USB only, common ground, no radio/bench supply.
Scope settings restored; old acquisition buffer replaced. See tools/bench/README.md.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time

from bench.serial_device import Device
from bench.rigol_scope import Scope,ownership
from bench.bypass_measurement import evaluate

ROOT=Path(__file__).resolve().parents[1]


def require(condition,message):
    if not condition:raise RuntimeError(message)


def run(args,report):
    fixture=arduino=None
    try:
        fixture=Device(args.standin,'fixture',report['transcript'])
        require(fixture.command('ID').startswith('STANDIN1 phase=1 board=NUCLEO-F767ZI '),'Wrong fixture')
        fixture.command('STOP');arduino=Device(args.pro,'arduino',report['transcript'])
        initial=arduino.status();report['initial']=initial
        serial_closed=getattr(args,'serial_closed',False)
        if serial_closed:
            require(initial['bench']==0 and not args.save_before_edge,'Closed-port mode requires production firmware and no SAVE stimulus')
        require(initial['bench'] in (0,1) and initial['armed']==1 and not any(initial[k] for k in ('tx','bypass','fault','busy')),
                'Requires idle healthy Arduino')
        if initial['bench']==1:arduino.save(1514)
        else:
            require(not args.save_before_edge,'Save stimulus requires bench firmware')
            require(initial['saved']==1514,'Production bypass run requires 151.4 Hz selected through UI')
        with ownership(),Scope() as scope:
            before=scope.status();report['scope_before']=before
            require(not(before['settings'][':TRIG:SWE']=='SING' and before['trigger']!='STOP'),'Preserve armed acquisition')
            settings={}
            for c in (1,2):
                settings.update({f':CHAN{c}:{k}':v for k,v in [('DISP','1'),('PROB','10'),('SCAL','1'),('OFFS','-2.5'),('COUP','DC'),('BWL','OFF'),('INV','0')]})
            settings.update({':TIM:SCAL':'0.01',':TIM:OFFS':'0',':ACQ:TYPE':'NORM',':TRIG:MODE':'EDGE',
                             ':TRIG:SWE':'NORM',':TRIG:EDG:SOUR':'CHAN1',':TRIG:EDG:SLOP':'NEG',':TRIG:EDG:LEV':'2'})
            try:
                scope.running(True)
                for k,v in settings.items():scope.write(f'{k} {v}')
                time.sleep(.4);scope.write(':ACQ:MDEP 600000');time.sleep(.2);scope.write(':TRIG:EDG:LEV 2')
                report['scope_configured']=scope.status()
                require(report['scope_configured']['settings'][':ACQ:MDEP']=='600000','Depth not accepted')
                require(abs(float(scope.q(':TRIG:EDG:LEV'))-2)<.001,'Trigger level not accepted')
                if serial_closed:
                    arduino.close();require(not arduino.connection.is_open,'Arduino serial did not close')
                    report['arduino_serial_closed_monotonic']=time.monotonic()
                fixture.command('ARM');fixture.command('PTT 1');time.sleep(.05)
                if not serial_closed:require(arduino.status()['tx']==1,'PTT did not key')
                for pair in range(args.pairs):
                    for enabled in (True,False):
                        name=f'pair-{pair+1}-'+('enable-bypass' if enabled else 'resume-tone')
                        folder=args.output/name;folder.mkdir()
                        baseline=None if serial_closed else arduino.status()
                        if serial_closed:require(not arduino.connection.is_open,'Arduino serial reopened during stimulus')
                        else:require(baseline['tx']==1 and baseline['active']==1514,'Transmission latch wrong')
                        scope.write(':TRIG:SWE NORM');scope.write(':TRIG:EDG:SLOP '+('NEG' if enabled else 'POS'))
                        scope.write(':TRIG:EDG:LEV 2');scope.running(True);scope.write(':SING');time.sleep(.8)
                        require(scope.q(':TRIG:STAT') in ('WAIT','RUN'),'Premature bypass trigger')
                        save_before=None
                        if args.save_before_edge:
                            target=1000 if baseline['saved']!=1000 else 1514
                            require(arduino.command(f'SAVE {target}').startswith('OK'),'Save not queued')
                            save_before=arduino.status();require(save_before['busy']==1,'Save not busy before bypass stimulus')
                        fixture.command(f'BYPASS {int(enabled)}')
                        until=time.monotonic()+3
                        while scope.q(':TRIG:STAT')!='STOP':
                            if time.monotonic()>until:raise TimeoutError('No completed bypass trigger')
                            time.sleep(.02)
                        observed=None if serial_closed else arduino.status()
                        if not serial_closed:
                            require(observed['tx']==1 and observed['bypass']==int(enabled) and observed['active']==1514 and observed['fault']==0,
                                    f'Unexpected keyed bypass state: {observed}')
                        if args.save_before_edge:
                            require(observed['busy']==0 and observed['saved']==target,'Durable save did not complete as expected')
                        channels=[]
                        for c in (1,2):
                            lease=fixture.status();require(lease['armed']==1 and lease['drive']==1+2*int(enabled),'Drive lease changed')
                            meta=scope.capture(folder/f'ch{c}',channel=c,single=False,max_points=600000)
                            require(scope.q(':TRIG:STAT')=='STOP','Buffer restarted between channels')
                            channels.append(((folder/f'ch{c}/waveform.u8').read_bytes(),meta['preamble']))
                        lease=fixture.status();require(lease['armed']==1 and lease['drive']==1+2*int(enabled),'Drive lease lost during transfer')
                        measured=evaluate(*channels[0],*channels[1],enabled)
                        row={'name':name,'measurement':measured,'arduino_state':observed,'save_state_before_stimulus':save_before}
                        report['checks'].append(row);(folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n')
                        print(name,measured,flush=True)
                        if pair==0:scope.screenshot(folder/'scope.bmp')
                        require(measured['passed'],'Bypass/PWM response failed')
            finally:
                fixture.command('STOP');scope.running(True)
                for k in settings:scope.write(f'{k} {before["settings"][k]}')
                scope.write(':ACQ:MDEP '+before['settings'][':ACQ:MDEP']);scope.running(before['trigger']!='STOP')
                after=scope.status();report['scope_after']=after
                keys=list(settings)+[':ACQ:MDEP']
                report['scope_restored']=all(before['settings'][k]==after['settings'][k] for k in keys) and ((before['trigger']=='STOP')==(after['trigger']=='STOP'))
                require(report['scope_restored'],'Scope settings not restored')
    finally:
        errors=[]
        if fixture is not None:
            try:
                fixture.command('STOP');report['fixture_final']=fixture.status()
                require(report['fixture_final']['armed']==0 and report['fixture_final']['drive']==0,'Fixture not released')
            except BaseException as error:errors.append(repr(error))
            finally:fixture.close()
        if arduino is not None:
            try:
                if getattr(args,'serial_closed',False) and not arduino.connection.is_open:
                    arduino.reopen();report['arduino_serial_reopened_monotonic']=time.monotonic()
                if report.get('initial',{}).get('bench')==1:arduino.save(report['initial']['saved'])
                time.sleep(.05);report['arduino_final']=arduino.status()
                require(not any(report['arduino_final'][k] for k in ('tx','bypass','fault')),'Arduino not idle/healthy')
            except BaseException as error:errors.append(repr(error))
            finally:arduino.close()
        if errors:report['cleanup_errors']=errors;raise RuntimeError('; '.join(errors))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro',required=True);parser.add_argument('--standin',required=True)
    parser.add_argument('--pairs',type=int,default=3);parser.add_argument('--save-before-edge',action='store_true')
    parser.add_argument('--serial-closed',action='store_true',help='Production only: close Arduino serial before keying and keep it closed through captures')
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.pro==args.standin or not 1<=args.pairs<=20:parser.error('Distinct ports and 1..20 pairs required')
    args.output.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),ROOT/'tools/bench/serial_device.py',ROOT/'tools/bench/rigol_scope.py',ROOT/'tools/bench/ptt_measurement.py',ROOT/'tools/bench/bypass_measurement.py']
    report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'checks':[],'transcript':[],
            'wiring':'CH1 Arduino D10 bypass; CH2 Arduino D9 PWM; both x10; common Arduino GND; F767 drive fixture',
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    try:run(args,report);report['passed']=True
    except BaseException as error:report['error']=repr(error);raise
    finally:(args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
