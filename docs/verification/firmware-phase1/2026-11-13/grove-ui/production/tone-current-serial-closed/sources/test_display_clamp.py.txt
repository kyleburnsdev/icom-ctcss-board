"""Offline acceptance/cleanup tests; no instrument or filesystem writes."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('qualifier',TOOLS/'qualify-display-clamp.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClampTests(unittest.TestCase):
    def run_case(self,low=.45,high=4.5,offline=True,recover=True,math='NONE',changed=False):
        state={'drive':0,'armed':0,'ever':False,'time':0,'closed':[]}

        class Device:
            def __init__(self,port,kind,log):self.kind=kind
            def command(self,text):
                if text=='ID':return 'STANDIN1 phase=1 board=NUCLEO-F767ZI '
                if text=='STOP':state.update(drive=0,armed=0)
                elif text=='ARM':state['armed']=1
                elif text=='ENCA 1':state['drive']|=8;state['ever']=True
                elif text=='BYPASS 1':state['drive']|=2
                elif text=='BYPASS 0':state['drive']&=~2
                return 'OK'
            def status(self):
                if self.kind=='fixture':return {'drive':state['drive'],'armed':state['armed']}
                lcd=0 if state['drive']&8 and offline else 1
                if state['ever'] and not state['drive'] and not recover:lcd=0
                return dict(lcd=lcd,tx=0,bypass=0,busy=0,fault=0,
                            saved=1000 if changed and state['drive']&8 else 1514)
            def close(self):state['closed'].append(self.kind)

        class Transport:
            def __enter__(self):return self
            def __exit__(self,*args):pass

        class Meter:
            def __init__(self,*args):pass
            def state(self):return dict(function='"VOLT"',math=math,auto='1',rate='S',range='10 V')
            def query(self,command):
                if command=='*IDN?':return 'OWON,XDM1251,example,V1.0.1.0.4'
                if command=='MEAS1?':return str(low if state['drive']&8 else high)
                raise AssertionError(command)

        def sleep(seconds):state['time']+=seconds
        with patch.object(module,'Device',Device),patch.object(module,'Meter',Meter), \
             patch.object(module.serial,'Serial',lambda *a,**k:Transport()), \
             patch.object(module.time,'sleep',sleep),patch.object(module.time,'monotonic',lambda:state['time']), \
             patch.object(Path,'mkdir'),patch.object(Path,'write_text') as write, \
             patch.object(sys,'argv',['qualifier','--pro','P','--standin','F','--meter','M','--output','unused']), \
             patch('builtins.print'):
            error=None
            try:module.main()
            except (RuntimeError,ValueError) as exc:error=exc
            result=json.loads(write.call_args.args[0])
        self.assertEqual(state['drive'],0)
        self.assertEqual(state['armed'],0)
        self.assertCountEqual(state['closed'],['fixture','arduino'])
        return result,error,state

    def test_valid_clamp_and_recovery(self):
        result,error,_=self.run_case()
        self.assertIsNone(error);self.assertTrue(result['passed'])
        self.assertEqual(result['clamped_V'],[.45]*3)

    def test_ineffective_clamp_rejected_and_released(self):
        result,error,_=self.run_case(low=2.5)
        self.assertIsNotNone(error);self.assertFalse(result['passed'])

    def test_wrong_meter_lead_level_rejected_before_drive(self):
        result,error,state=self.run_case(high=.01)
        self.assertIsNotNone(error);self.assertFalse(state['ever']);self.assertFalse(result['passed'])

    def test_lcd_must_actually_go_offline(self):
        result,error,_=self.run_case(offline=False)
        self.assertIsNotNone(error);self.assertFalse(result['passed'])

    def test_failed_display_recovery_cannot_pass(self):
        result,error,_=self.run_case(recover=False)
        self.assertIsNotNone(error);self.assertFalse(result['passed'])

    def test_relative_mode_rejected_before_drive(self):
        result,error,state=self.run_case(math='NULL')
        self.assertIsNotNone(error);self.assertFalse(state['ever']);self.assertFalse(result['passed'])

    def test_saved_selection_change_rejected(self):
        result,error,_=self.run_case(changed=True)
        self.assertIsNotNone(error);self.assertFalse(result['passed'])


if __name__=='__main__':unittest.main()
