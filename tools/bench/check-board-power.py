"""Brief populated-board RAW power screen. See tools/bench/README.md.

Energizes TP2 at 8 V, limited to 50 mA. No USB or off-board devices allowed.
Meter COM/black and supply minus at TP1. Red at TP3 for vcc, TP2 for raw.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

from korad_supply import Supply, port_lock, DEFAULT_EXE
from xdm1251 import Meter, identity, require_dcv, utc, voltage


class LoggedSupply(Supply):
    def __init__(self, exe, port, evidence):
        super().__init__(exe, port)
        self.evidence = evidence

    def call(self, *args, **kwargs):
        row = {'utc': utc(), 'arguments': list(args)}
        self.evidence['supply_commands'].append(row)
        raw = super().call(*args, **kwargs)
        row['response'] = re.sub(r'(S/?N:\s*)[^\s\]]+', r'\1[redacted]', raw)
        return raw


def check_source(state):
    if (not state['enabled'] or state['regulation'] != 'CV'
            or not 7.8 <= state['voltage'] <= 8.2
            or not 0 <= state['current'] < 0.049):
        raise RuntimeError('Source not in expected 8 V CV / below-49 mA state')


def run(supply, meter, report, measurement='vcc', experiment=None):
    report['supply_before'] = supply.state()
    if report['supply_before']['enabled']:
        raise RuntimeError('Supply must initially be OFF')
    report['meter_before'] = meter.state()
    require_dcv(report['meter_before'])
    if (report['meter_before']['secondary'].strip('"').upper() != 'NONE'
            or report['meter_before']['auto'] != '1'
            or report['meter_before']['rate'] != 'S'):
        raise RuntimeError('Meter requires DCV, autorange, S, secondary/math off')
    report['pre_voltage_v'] = voltage(meter.query('MEAS1?'))
    if abs(report['pre_voltage_v']) > 1:
        raise RuntimeError('Unexpected initial VCC; check disconnected sources')
    try:
        supply.configure(voltage_target='8.00', current_limit='0.050', ocp_enabled='no')
        settings = report['settings_before_enable'] = supply.state()
        if (settings['enabled'] or abs(settings['voltage_target'] - 8) > 0.0001
                or abs(settings['current_limit'] - 0.05) > 0.00001
                or settings['ocp_enabled']):
            raise RuntimeError('Pre-enable settings mismatch')
        report['enable_requested_utc'] = utc()
        supply.configure(enabled='yes')
        check_source_state = report['supply_enabled'] = supply.state()
        check_source(check_source_state)
        time.sleep(2)
        limits = (4.75, 5.25) if measurement == 'vcc' else (7.8, 8.2)
        readings = report[measurement + '_readings_v'] = []
        for i in range(8):
            value = voltage(meter.query('MEAS1?'))
            readings.append(value)
            if not limits[0] <= value <= limits[1]:
                raise RuntimeError(f'{measurement.upper()} outside selected {limits} V screen')
            if i < 7:
                time.sleep(0.5)
        report['supply_after_measurement'] = supply.state()
        check_source(report['supply_after_measurement'])
        report['meter_after'] = meter.state()
        require_dcv(report['meter_after'])
        for key, value in report['meter_before'].items():
            if key != 'range' and report['meter_after'][key] != value:
                raise RuntimeError('Meter settings changed during run')
        report['measurement_checks_passed'] = True
        if experiment is not None:
            key = experiment['key']
            destination = experiment['output']
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / experiment['script']),
                       '--output', str(destination), *experiment['arguments']]
            report[key] = {'command': command, 'started_utc': utc()}
            result = subprocess.run(command, capture_output=True, text=True, timeout=experiment['timeout_s'])
            report[key].update(returncode=result.returncode, stdout=result.stdout,
                               stderr=result.stderr, finished_utc=utc())
            if result.returncode:
                raise RuntimeError(f'{key} failed; inspect retained child evidence')
            report[key]['result'] = json.loads((destination / 'result.json').read_text())
            if not report[key]['result']['passed']:
                raise RuntimeError(f'{key} report did not pass')
            report['supply_after_' + key] = supply.state()
            check_source(report['supply_after_' + key])
            report['vcc_after_' + key + '_v'] = voltage(meter.query('MEAS1?'))
            if not 4.75 <= report['vcc_after_' + key + '_v'] <= 5.25:
                raise RuntimeError(f'VCC outside selected limits after {key}')
    finally:
        report['disable_requested_utc'] = utc()
        report['supply_output_off'] = supply.off()
        supply.configure(voltage_target='1.00', current_limit='0.050', ocp_enabled='yes')
        final = report['supply_final'] = supply.state()
        if (final['enabled'] or abs(final['voltage_target'] - 1) > 0.0001
                or abs(final['current_limit'] - 0.05) > 0.00001
                or not final['ocp_enabled']):
            raise RuntimeError('Final off / 1 V / 50 mA / OCP-on state unconfirmed')
    time.sleep(2)
    report['post_voltage_v'] = voltage(meter.query('MEAS1?'))


def experiment_from_args(args):
    definitions = {
        'idle_pwm': dict(script='check-idle-pwm.py', key='pwm_capture', status='power_and_idle_pwm_pass',
                         scope='CH1 x10 TP4; ground TP1', fixture=False),
        'filter': dict(script='check-idle-filter.py', key='filter_capture', status='power_and_idle_filter_pass',
                       scope='CH1 x10 TP4; CH2 x10 TP5; grounds TP1', fixture=False),
        'tone': dict(script='check-board-tone.py', key='tone_capture', status='power_and_board_tone_pass',
                     scope='CH1 x10 TP4; CH2 x10 TP5; grounds TP1', fixture=True),
        'ptt': dict(script='check-board-ptt.py', key='ptt_capture', status='power_and_loaded_ptt_pass',
                    scope='CH1 x10 TP7; CH2 x10 TP8; grounds TP1; 1k load TP3 to TP8', fixture=True),
        'mixing': dict(script='check-board-mixing.py', key='mixing_capture', status='power_and_mixing_'+args.mixing_level+'_pass',
                       scope='CH1 x10 TP5; CH2 x1 TP6; grounds TP1; TP3-to-TP8 load removed; RV1 '+args.mixing_level, fixture=True),
        'leds': dict(script='check-board-leds.py', key='leds_capture', status='power_and_loaded_leds_pass',
                     scope='CH1 x10 J6-1; CH2 x10 J6-3; grounds TP1; 1k loads J6-1/2 and J6-3/4; RV1 minimum', fixture=True),
    }
    selected = [name for name in definitions if getattr(args,name+'_output') is not None]
    if len(selected)>1:
        raise ValueError('Choose one scope experiment per powered run')
    if args.grounded_control and selected!=['filter']:
        raise ValueError('Grounded control requires --filter-output')
    if not selected:
        return None
    name=selected[0]
    experiment=dict(definitions[name])
    experiment['output']=getattr(args,name+'_output')
    if args.measurement!='vcc' or not args.scope_probe_confirmed:
        raise ValueError('Scope capture requires VCC meter setup and confirmed probes')
    if experiment['output'].exists() or not experiment['output'].parent.is_dir():
        raise ValueError('Capture output must be new with an existing parent directory')
    experiment['arguments']=[]
    experiment['timeout_s']=120 if experiment['fixture'] else 60
    if experiment['fixture']:
        if not args.fixture_port or args.fixture_port.upper() in [args.meter_port.upper(),args.supply_port.upper()]:
            raise ValueError('Experiment requires a distinct explicit fixture port')
        experiment['arguments'] += ['--fixture-port',args.fixture_port]
    if name=='idle_pwm':
        experiment['arguments'].append('--raw-powered-board')
    elif name=='filter':
        experiment['arguments'] += ['--ripple-scale',args.filter_ripple_scale]
        if args.grounded_control:
            experiment['arguments'].append('--grounded-control')
            experiment['scope']='CH1 x10 TP4; CH2 x10 tip and ground TP1'
            experiment['status']='power_and_grounded_control_complete'
    elif name=='mixing':
        experiment['arguments'] += ['--level',args.mixing_level]
    return experiment


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--meter-port',required=True)
    parser.add_argument('--supply-port',required=True)
    parser.add_argument('--sigrok-exe',type=Path,default=DEFAULT_EXE)
    parser.add_argument('--setup-confirmed',required=True,action='store_true')
    parser.add_argument('--measurement',choices=['vcc','raw'],default='vcc')
    for name in ['idle-pwm','filter','tone','ptt','mixing','leds']:
        parser.add_argument('--'+name+'-output',type=Path,help='New capture directory for '+name)
    parser.add_argument('--filter-ripple-scale',choices=['0.01','0.05','0.1'],default='0.01')
    parser.add_argument('--grounded-control',action='store_true')
    parser.add_argument('--mixing-level',choices=['maximum','minimum'],default='maximum')
    parser.add_argument('--fixture-port')
    parser.add_argument('--scope-probe-confirmed',action='store_true',help='Operator verified the selected experiment wiring and physical probe factors')
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.meter_port.upper()==args.supply_port.upper():
        parser.error('Meter and supply require distinct ports')
    try:
        experiment=experiment_from_args(args)
    except ValueError as exc:
        parser.error(str(exc))
    report={'started_utc':utc(),'status':'incomplete','queries':[],'supply_commands':[],
            'setup_confirmed':True,'meter_port':args.meter_port,'supply_port':args.supply_port,
            'measurement':args.measurement,
            'connections':f'Supply + TP2; supply minus and meter COM TP1; meter V/ohm {"TP3" if args.measurement=="vcc" else "TP2"}; PCB USB and final product components disconnected',
            'limits':{'raw_v':8,'current_limit_a':.05,'vcc_v':[4.75,5.25]},'source_hashes':{}}
    files=[Path(__file__),Path(__file__).with_name('korad_supply.py'),Path(__file__).with_name('xdm1251.py')]
    if experiment is not None:
        report['scope_connections']=experiment['scope']+'; connected while supply off'
        files += [Path(__file__).resolve().parents[1]/experiment['script'],Path(__file__).with_name('rigol_scope.py')]
        if experiment['fixture']:
            report['fixture_connections']='NUCLEO GND CN10-5 TP1; PF12 CN7-20 through 1k to J1-5; PF13 CN10-2 through 1k to J5-1; rails separate'
            files += [Path(__file__).with_name(name) for name in
                      ['fixture_control.py','serial_device.py','ptt_measurement.py','analog_tone.py']]
    report['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.out.open('x',encoding='utf-8') as output:
        try:
            import serial
            report['pyserial_version']=serial.VERSION
            supply=LoggedSupply(args.sigrok_exe,args.supply_port,report)
            with port_lock(args.supply_port):
                supply.identify()
                time.sleep(.25)
                with serial.Serial(args.supply_port,9600,timeout=2,write_timeout=2) as source_transport:
                    if source_transport.write(b'*IDN?')!=5:
                        raise IOError('Incomplete supply identity write')
                    source_identity=source_transport.read(128).decode('ascii').strip()
                if 'KA3005P' not in source_identity or not re.search(r'V1\.5(?!\d)',source_identity):
                    raise RuntimeError('Unexpected supply model/firmware identity')
                report['supply_identity']={'model':'KA3005P','firmware':'V1.5','serial_number':'[redacted]'}
                time.sleep(.25)
                with serial.Serial(args.meter_port,115200,timeout=2,write_timeout=2) as transport:
                    meter=Meter(transport,report)
                    report['meter_identity']=identity(meter.query('*IDN?'),'V1.0.1.0.4')
                    run(supply,meter,report,args.measurement,experiment)
            report['status']=experiment['status'] if experiment is not None else 'power_screen_pass'
            code=0
        except (Exception,KeyboardInterrupt) as exc:
            report['error']=type(exc).__name__+': '+str(exc)
            code=2
        finally:
            report['finished_utc']=utc()
            json.dump(report,output,indent=2,allow_nan=False)
            output.write('\n')
    print(json.dumps({k:report.get(k) for k in ['status','error','vcc_readings_v','raw_readings_v',
                     'supply_enabled','supply_after_measurement','supply_final','post_voltage_v']}))
    return code


if __name__=='__main__':
    raise SystemExit(main())

