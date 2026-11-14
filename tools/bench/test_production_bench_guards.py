"""Production regression tools must never issue bench SAVE/HANG commands."""
import contextlib
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


class ReachedScope(Exception):pass


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class ProductionGuards(unittest.TestCase):
    def check(self,name,save=False,watchdog=False,tone=1514,allowed=False):
        module=load(name);commands=[]

        class Device:
            def __init__(self,port,kind,log):self.kind=kind
            def command(self,text):
                commands.append((self.kind,text))
                if text=='ID':return 'STANDIN1 phase=1 board=NUCLEO-F767ZI '
                return 'OK'
            def status(self):
                if self.kind=='fixture':return dict(armed=0,drive=0)
                return dict(bench=0,armed=1,tx=0,bypass=0,fault=0,busy=0,lcd=1,saved=tone)
            def save(self,value):raise AssertionError('Production SAVE attempted')
            def close(self):pass

        def scope():raise ReachedScope()
        args=SimpleNamespace(pro='P',standin='F',save_before_edge=save,watchdog=watchdog,display_fault=False)
        report={'transcript':[]}
        with patch.object(module,'Device',Device),patch.object(module,'Scope',scope), \
             patch.object(module,'ownership',contextlib.nullcontext),patch.object(module.time,'sleep'):
            with self.assertRaises(ReachedScope if allowed else RuntimeError):module.run(args,report)
        self.assertFalse(any(text.startswith(('SAVE','HANG')) for kind,text in commands))
        self.assertEqual(report['fixture_final']['drive'],0)

    def test_ptt_production_baseline(self):self.check('check-ptt-timing',allowed=True)
    def test_ptt_production_save_rejected(self):self.check('check-ptt-timing',save=True)
    def test_ptt_production_hang_rejected(self):self.check('check-ptt-timing',watchdog=True)
    def test_bypass_production_baseline(self):self.check('check-bypass-timing',allowed=True)
    def test_bypass_production_save_rejected(self):self.check('check-bypass-timing',save=True)
    def test_bypass_production_wrong_tone_rejected(self):self.check('check-bypass-timing',tone=1000)


if __name__=='__main__':unittest.main()
