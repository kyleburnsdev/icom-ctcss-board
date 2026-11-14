"""Measure real D7->D8 PTT latency with synchronized DS1202Z-E channels.

CH1 x10 -> Arduino D7; CH2 x10 -> Arduino D8; both grounds Arduino GND.
F767 minimal input-drive fixture required; radio/bench supply disconnected.
Changes/restores scope settings and replaces the acquisition buffer.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
import serial
from serial.tools import list_ports

from bench.rigol_scope import Scope,ownership
from bench.serial_device import Device
from bench.ptt_measurement import evaluate,watchdog

ROOT=Path(__file__).resolve().parents[1]


def require(condition,message):
    if not condition:raise RuntimeError(message)


def watchdog_cases(args,report,scope,fixture,arduino):
    for bypass in (0,1):
        fixture.command(f'BYPASS {bypass}');fixture.command('PTT 1');time.sleep(.05)
        require(arduino.status()['tx']==1,'PTT did not key before watchdog experiment')
        scope.write(':TRIG:SWE NORM');scope.write(':TRIG:EDG:SOUR CHAN2')
        scope.write(':TRIG:EDG:SLOP NEG');scope.write(':TRIG:EDG:LEV 2')
        scope.running(True);scope.write(':SING')
        # Fill the long pretrigger buffer, with PTT already held and the lease refreshed.
        until=time.monotonic()+3.5
        while time.monotonic()<until:
            state=fixture.status();require(state['drive']==1+2*bypass and state['armed']==1,'Fixture lost held input')
            time.sleep(.2)
        require(scope.q(':TRIG:STAT') in ('WAIT','RUN'),'Premature output-fall trigger')
        # Four 1 ms release pulses mark the waveform without qualifying a release.
        # The last falling edge is necessarily BEFORE the subsequent HANG command.
        fixture.command('BOUNCE 1');time.sleep(.03)
        require(fixture.status()['bouncing']==0,'Marker pattern did not complete')
        before=arduino.status();require(before['tx']==1 and before['fault']==0,'Marker unkeyed Arduino')
        started=time.monotonic();arduino.connection.write(b'HANG\n');arduino.connection.flush();arduino.close()
        disappeared=False;recovered=None;stopped=False
        while time.monotonic()-started<15:
            state=fixture.status();require(state['drive']==1+2*bypass and state['armed']==1,'Fixture did not hold PTT')
            present=args.pro in {p.device for p in list_ports.comports()}
            if not present:disappeared=True
            if disappeared and present and recovered is None:
                try:
                    arduino.reopen();recovered=arduino.status()
                    recovered_at=time.monotonic()-started
                except (serial.SerialException,TimeoutError):arduino.close()
            stopped=scope.q(':TRIG:STAT')=='STOP'
            if stopped and recovered is not None:break
            time.sleep(.1)
        require(stopped and disappeared and recovered is not None,'Missing reset, USB recovery or real output-fall capture')
        require(recovered['tx']==0 and recovered['armed']==0 and recovered['fault']==0 and
                recovered['bypass']==bypass and recovered['saved']==report['initial']['saved'],
                f'Unexpected held-reset state: {recovered}')
        folder=args.output/f'watchdog-bypass-{bypass}';folder.mkdir()
        channels=[]
        for channel in (1,2):
            fixture.status()
            meta=scope.capture(folder/f'ch{channel}',channel=channel,single=False,max_points=600000)
            require(scope.q(':TRIG:STAT')=='STOP','Watchdog buffer restarted between channels')
            channels.append(((folder/f'ch{channel}/waveform.u8').read_bytes(),meta['preamble']))
        state=fixture.status();require(state['drive']==1+2*bypass and state['armed']==1,'Held input lost during transfer')
        measured=watchdog(*channels[0],*channels[1])
        row={'name':folder.name,'bypass':bypass,'measurement':measured,'status_before_hang':before,
             'status_held_after_reset':recovered,'host_usb_recovery_s':recovered_at}
        report['checks'].append(row);(folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n')
        print(folder.name,measured,flush=True);require(measured['passed'],'Electrical watchdog release exceeded one second')
        scope.screenshot(folder/'scope.bmp')
        fixture.command('PTT 0');time.sleep(.05);require(arduino.status()['armed']==1,'Did not rearm after release')
        fixture.command('PTT 1');time.sleep(.05);require(arduino.status()['tx']==1,'Fresh press did not key')
        fixture.command('PTT 0');time.sleep(.05)


def run(args,report):
    fixture=arduino=None
    try:
        fixture=Device(args.standin,'fixture',report['transcript'])
        require(fixture.command('ID').startswith('STANDIN1 phase=1 board=NUCLEO-F767ZI '),'Wrong fixture')
        fixture.command('STOP')
        arduino=Device(args.pro,'arduino',report['transcript'])
        report['initial']=arduino.status()
        require(report['initial']['bench'] in (0,1) and report['initial']['armed']==1 and
                not any(report['initial'][k] for k in ('tx','bypass','fault','busy')),'Requires idle healthy Arduino')
        if args.save_before_edge or args.watchdog:
            require(report['initial']['bench']==1,'Save/watchdog stimulus requires bench firmware')
        with ownership(),Scope() as scope:
            before=scope.status();report['scope_before']=before
            require(not(before['settings'][':TRIG:SWE']=='SING' and before['trigger']!='STOP'),
                    'Preserve already armed single capture')
            settings={}
            for channel in (1,2):
                settings.update({f':CHAN{channel}:{key}':value for key,value in
                    [('DISP','1'),('PROB','10'),('SCAL','1'),('OFFS','-2.5'),('COUP','DC'),('BWL','OFF'),('INV','0')]})
            # Offset/scale changes can move the trigger level. Apply all channel
            # settings first, and establish/restore trigger level LAST.
            settings.update({':TIM:SCAL':'0.5' if args.watchdog else '0.01',':TIM:OFFS':'0',':ACQ:TYPE':'NORM',
                             ':TRIG:MODE':'EDGE',':TRIG:SWE':'NORM',':TRIG:EDG:SOUR':'CHAN1',
                             ':TRIG:EDG:SLOP':'NEG',':TRIG:EDG:LEV':'2'})
            try:
                scope.running(True)
                for key,value in settings.items():scope.write(f'{key} {value}')
                time.sleep(.4)
                require(scope.q(':CHAN1:DISP')=='1' and scope.q(':CHAN2:DISP')=='1','Dual channels did not settle')
                scope.write(':ACQ:MDEP 600000');time.sleep(.2)
                require(scope.q(':ACQ:MDEP')=='600000','Memory depth not accepted')
                scope.write(':TRIG:EDG:LEV 2')
                report['scope_configured']=scope.status()
                require(abs(float(report['scope_configured']['settings'][':TRIG:EDG:LEV'])-2)<.001,
                        'Trigger level did not settle to 2 V')
                fixture.command('ARM')
                fault_mask=0
                if args.display_fault:
                    require(report['initial']['lcd']==1,'Display must be online before fault')
                    fixture.command('ENCA 1');fault_mask=8
                    fixture.command('BYPASS 1')  # Force changed display content.
                    deadline=time.monotonic()+2
                    while arduino.status()['lcd']!=0:
                        fixture.status()
                        require(time.monotonic()<deadline,'Display did not go offline under qualified SCL clamp')
                        time.sleep(.05)
                    report['display_fault_initial']=arduino.status()
                    # Exercise invisible short and long button gestures. Encoder A
                    # is reassigned to SCL, so no full-detent claim is made here.
                    for duration in (.12,.95,.12):
                        fixture.command('BUTTON 1');time.sleep(duration)
                        fixture.command('BUTTON 0');time.sleep(.05)
                    invisible=arduino.status();report['invisible_buttons']=invisible
                    require(invisible['lcd']==0 and invisible['saved']==report['initial']['saved'] and invisible['busy']==0,
                            'Invisible button gestures altered durable setting or display state')
                if args.watchdog:
                    watchdog_cases(args,report,scope,fixture,arduino)
                    return
                for bypass in (0,1):
                    fixture.command(f'BYPASS {bypass}');time.sleep(.05)
                    for pair in range(args.pairs):
                        for pressed in (True,False):
                            name=f'bypass-{bypass}-pair-{pair+1}-'+('press' if pressed else 'release')
                            folder=args.output/name;folder.mkdir()
                            baseline=arduino.status()
                            require(baseline['tx']==int(not pressed),'Wrong baseline PTT state')
                            scope.write(':TRIG:SWE NORM');scope.write(':TRIG:EDG:SLOP '+('NEG' if pressed else 'POS'))
                            scope.write(':TRIG:EDG:LEV 2')
                            scope.running(True);scope.write(':SING');time.sleep(.8)
                            require(scope.q(':TRIG:STAT') in ('WAIT','RUN'),'Scope triggered before stimulus')
                            save_before=None
                            if args.save_before_edge:
                                target=1000 if baseline['saved']!=1000 else 1514
                                require(arduino.command(f'SAVE {target}').startswith('OK'),'Save not queued')
                                save_before=arduino.status()
                                require(save_before['busy']==1,'Save busy state not observed before stimulus')
                            fixture.command(('BOUNCE' if args.bounce else 'PTT')+f' {int(pressed)}')
                            deadline=time.monotonic()+3
                            while scope.q(':TRIG:STAT')!='STOP':
                                if time.monotonic()>deadline:
                                    report['trigger_timeout']={'scope':scope.status(),
                                        'arduino':arduino.status(),'fixture':fixture.status()}
                                    raise TimeoutError('No completed PTT trigger')
                                time.sleep(.02)
                            observed=arduino.status()
                            require(observed['tx']==int(pressed) and observed['bypass']==bypass and observed['fault']==0,
                                    f'Unexpected Arduino state: {observed}')
                            if args.display_fault:require(observed['lcd']==0,'Display fault disappeared during PTT test')
                            if args.save_before_edge:
                                require(observed['busy']==0 and observed['saved']==target,'Save did not complete as expected')
                            channels=[]
                            for channel in (1,2):
                                lease=fixture.status()
                                require(lease['armed']==1 and lease['drive']==int(pressed)+2*bypass+fault_mask,'Fixture lease/drive changed')
                                # Capture both channels from the SAME stopped acquisition.
                                # The helper must restore STOP after each channel transfer.
                                meta=scope.capture(folder/f'ch{channel}',channel=channel,single=False,max_points=600000)
                                require(scope.q(':TRIG:STAT')=='STOP','Acquisition restarted between channel reads')
                                channels.append(((folder/f'ch{channel}/waveform.u8').read_bytes(),meta['preamble']))
                            lease=fixture.status()
                            require(lease['armed']==1 and lease['drive']==int(pressed)+2*bypass+fault_mask,'Fixture lease expired during transfer')
                            if args.bounce:require(lease['bouncing']==0 and lease['bounce_late_us']<100,'Bounce schedule exceeded selected bound')
                            measured=evaluate(*channels[0],*channels[1],pressed,bouncing=args.bounce)
                            row={'name':name,'bypass':bypass,'measurement':measured,'arduino_state':observed,
                                 'save_state_immediately_before_stimulus':save_before}
                            if args.bounce:row['fixture_bounce_status']=lease
                            report['checks'].append(row)
                            (folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n')
                            print(name,measured,flush=True)
                            if pair==0 and bypass==0:scope.screenshot(folder/'scope.bmp')
                            require(measured['passed'],'PTT latency outside 0..25 ms')
            finally:
                # Release inputs before restoring scope settings.
                fixture.command('STOP')
                scope.running(True)
                for key in settings:scope.write(f'{key} {before["settings"][key]}')
                scope.write(':ACQ:MDEP '+before['settings'][':ACQ:MDEP'])
                scope.running(before['trigger']!='STOP')
                after=scope.status();report['scope_after']=after
                keys=list(settings)+[':ACQ:MDEP']
                mismatch={key:[before['settings'][key],after['settings'][key]]
                          for key in keys if before['settings'][key]!=after['settings'][key]}
                report['scope_restored']=not mismatch and ((before['trigger']=='STOP')==(after['trigger']=='STOP'))
                require(report['scope_restored'],f'Scope restoration mismatch: {mismatch}')
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
                if args.save_before_edge and report.get('initial',{}).get('bench')==1:
                    arduino.save(report['initial']['saved'])
                if args.display_fault:
                    deadline=time.monotonic()+3
                    while arduino.status()['lcd']!=1:
                        require(time.monotonic()<deadline,'Display did not recover after SCL release')
                        time.sleep(.05)
                time.sleep(.05);report['arduino_final']=arduino.status()
                require(report['arduino_final']['tx']==0 and report['arduino_final']['bypass']==0,'Arduino not released')
                require(report['arduino_final']['saved']==report['initial']['saved'],'Saved tone changed')
            except BaseException as error:errors.append(repr(error))
            finally:arduino.close()
        if errors:
            report['cleanup_errors']=errors;raise RuntimeError('; '.join(errors))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pro',required=True);parser.add_argument('--standin',required=True)
    parser.add_argument('--pairs',type=int,default=3)
    parser.add_argument('--save-before-edge',action='store_true',help='Confirm an asynchronous save is busy immediately before each PTT stimulus')
    parser.add_argument('--watchdog',action='store_true',help='Measure electrical watchdog release in both bypass states, using a physical pre-HANG marker')
    parser.add_argument('--bounce',action='store_true',help='Use eight 1 ms toggles and measure response from the final stable input edge')
    parser.add_argument('--display-fault',action='store_true',help='ENCA reassigned through 1k to SCL, requires passed electrical qualification')
    parser.add_argument('--fault-qualification',type=Path,help='Passed qualify-display-clamp.py result from this wiring session')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.watchdog and (args.save_before_edge or args.bounce):parser.error('Watchdog is a separate mode')
    if args.display_fault:
        if args.watchdog or not args.fault_qualification:parser.error('Display fault requires qualification and is separate from watchdog')
        qualification=json.loads(args.fault_qualification.read_text(encoding='utf-8'))
        if not qualification.get('passed') or qualification.get('clamp_command')!='ENCA':parser.error('Clamp qualification did not pass')
    if args.pro==args.standin or not 1<=args.pairs<=20:parser.error('Distinct ports and 1..20 pairs required')
    args.output.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),ROOT/'tools/bench/serial_device.py',ROOT/'tools/bench/ptt_measurement.py',ROOT/'tools/bench/rigol_scope.py']
    report={'utc':datetime.now(timezone.utc).isoformat(),'passed':False,'checks':[],'transcript':[],
            'wiring':'Rigol CH1 x10 D7 input; CH2 x10 D8 output; common Arduino GND; F767 minimal-drive fixture',
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    if args.display_fault:
        report['display_fault_wiring']='PF15 ENCA through existing 1k to Arduino D3/SCL; D4 retains 10k pull-up, encoder A disconnected'
        report['electrical_qualification']=qualification
        report['qualification_sha256']=hashlib.sha256(args.fault_qualification.read_bytes()).hexdigest()
    try:
        run(args,report);report['passed']=True
    except BaseException as error:report['error']=repr(error);raise
    finally:(args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
