"""Replay retained populated-board data without opening any instrument.

Usage: python tools/check-populated-board-evidence.py EVIDENCE_DIRECTORY --out NEW_JSON
Checks accepted records, raw hashes, current evaluators and documented closure.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tools/bench'))
from bench.analog_tone import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    base=args.directory
    report={'passed':False,'hardware_access':False,'checks':[]}
    def load(relative): return json.loads((base/relative).read_text(encoding='utf-8-sig'))
    def check(name,condition):
        report['checks'].append({'name':name,'passed':bool(condition)})
        if not condition: raise AssertionError(name)
    def capture(folder):
        meta=load(folder+'/capture.json')
        raw=(base/folder/'waveform.u8').read_bytes()
        check(folder+' complete and transfer restored',len(raw)==meta['points'] and meta['restored'])
        return raw,meta['preamble']
    def hashed(raw,expected,name): check(name,hashlib.sha256(raw).hexdigest()==expected)
    with args.out.open('x',encoding='utf-8') as output:
        try:
            idle=runpy.run_path(str(ROOT/'tools/check-idle-pwm.py'))['evaluate']
            ptt=runpy.run_path(str(ROOT/'tools/check-board-ptt.py'))['evaluate']
            leds=runpy.run_path(str(ROOT/'tools/check-board-leds.py'))['evaluate']
            data=load('idle-pwm/result.json')
            raw,p=capture('idle-pwm/capture')
            hashed(raw,data['waveform_sha256'],'Idle PWM raw SHA256')
            check('Idle PWM current evaluator',idle(raw,p)['passed'])
            for name in ['idle-filter-100mv','grounded-ch2-control']:
                data=load(name+'/result.json')
                check(name+' accepted with scope restored',data['passed'] and data['settings_restored'])
                for phase in ['dc','ripple']:
                    raw,p=capture(name+'/'+phase)
                    hashed(raw,data[phase]['sha256'],name+'/'+phase+' SHA256')
            data=load('physical-tone-bypass/result.json')
            for state in data['states']:
                raw,p=capture('physical-tone-bypass/'+state['name'])
                hashed(raw,state['sha256'],state['name']+' tone SHA256')
                check(state['name']+' analog replay',analyze(raw,p,bool(state['ptt'] and not state['bypass']),151.4)['passed'])
            data=load('loaded-ptt/result.json')
            check('Twelve loaded PTT events retained',len(data['transitions'])==12)
            for row in data['transitions']:
                channels=[capture('loaded-ptt/'+row['name']+'/ch'+str(channel)) for channel in [1,2]]
                for i,c in enumerate(channels): hashed(c[0],row['waveform_sha256'][i],row['name']+' ch'+str(i+1)+' SHA256')
                check(row['name']+' collector replay',ptt(*channels[0],*channels[1],row['measurement']['pressed'])['passed'])
            for name,active in [('mixing-maximum-b',True),('mixing-minimum',False)]:
                data=load(name+'/result.json')
                channels=[capture(name+'/ch'+str(channel)) for channel in [1,2]]
                for i,c in enumerate(channels): hashed(c[0],data['waveform_sha256'][i],name+' ch'+str(i+1)+' SHA256')
                check(name+' TP5 replay',analyze(*channels[0],True,151.4)['passed'])
                check(name+' TP6 replay',analyze(*channels[1],active,151.4,active_pp=(.10,.22),
                      active_rms=(.02,.09),mean_limits=(-.03,.03),suppressed_pp=.02,suppressed_rms=.01)['passed'])
            data=load('loaded-leds-c/result.json')
            check('Five loaded LED states retained',len(data['states'])==5)
            for state in data['states']:
                for measured in state['measurements']:
                    folder='loaded-leds-c/'+state['name']+'/ch'+str(measured['channel'])
                    raw,p=capture(folder)
                    hashed(raw,measured['sha256'],folder+' SHA256')
                    check(folder+' loaded-level replay',leds(raw,p,measured['asserted'])['passed'])
            accepted=['idle-pwm','idle-filter-100mv','grounded-ch2-control','physical-tone-bypass',
                      'loaded-ptt','mixing-maximum-b','mixing-minimum','loaded-leds-c']
            for name in accepted:
                data=load(name+'/result.json')
                check(name+' accepted and restored',data['passed'] and data['settings_restored'])
                if 'fixture_final' in data:
                    check(name+' fixture released',data['fixture_final']['armed']==0 and data['fixture_final']['drive']==0)
            parents=['power-with-idle-pwm.json','power-with-idle-filter-100mv.json','power-with-grounded-ch2-control.json',
                     'power-with-physical-tone-bypass.json','power-with-loaded-ptt.json','power-with-mixing-maximum-b.json',
                     'power-with-mixing-minimum.json','power-with-loaded-leds-c.json','raw-at-pcb.json','vcc-at-pcb.json']
            for name in parents:
                data=load(name)
                check(name+' accepted with supply off',('pass' in data['status'] or 'complete' in data['status'])
                      and not data['supply_final']['enabled'])
            manual=load('connector-operator-results.json')
            check('21 operator continuity checks and intercepted PTT',manual['same_net_checks']['count']==21
                  and manual['same_net_checks']['highest_reported_ohm']<2
                  and manual['ptt_separation']['reported_indication']=='OL')
            check('Final meter DCV restored',load('connector-meter-finished.json')['dcv_restored'])
            check('Fresh supply final OFF',not load('supply-final-status.json')['enabled'])
            expected=json.loads((ROOT/'docs/verification/wiring-guide/checks.json').read_text())['sha256']
            for file in ['electronics/icom-ctcss-board.kicad_pcb','electronics/icom-ctcss-board.kicad_sch']:
                check(file+' matches wiring source snapshot',hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==expected[file])
            report['passed']=True
        except Exception as exc:
            report['error']=type(exc).__name__+': '+str(exc)
        json.dump(report,output,indent=2)
        output.write('\n')
    print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}))
    return 0 if report['passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
