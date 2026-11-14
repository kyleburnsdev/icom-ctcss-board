"""Offline watchdog-runner verdict checks; all serial/discovery calls mocked."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('watchdog_runner',ROOT/'tools/usb-watchdog-test.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class Clock:
    def __init__(self): self.now=0
    def monotonic(self): self.now+=.01; return self.now
    def sleep(self,seconds): self.now+=seconds


class WatchdogRunnerTests(unittest.TestCase):
    def experiment(self,disappears=True,changed=False,missing=False):
        commands=[]; calls=[]
        good=dict(bench=1,tx=0,fault=0,busy=0,bypass=0,saved=1514,active=1514,armed=1)
        def status(port,transcript):
            calls.append(port)
            if missing: raise runner.serial.SerialException('simulated absent Arduino')
            state=good.copy()
            if changed and len(calls)>1: state['saved']=1000
            return state
        class Serial:
            def __init__(self,*args,**kwargs): pass
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def write(self,data): commands.append(data)
            def flush(self): pass
        scratch=ROOT/'.agent-scratch/firmware'; scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            output=Path(directory)/'result.json'
            discovery=SimpleNamespace(comports=lambda: [] if disappears else [SimpleNamespace(device='MOCK')])
            with patch.object(runner,'status',status), patch.object(runner.serial,'Serial',Serial), \
                 patch.object(runner,'list_ports',discovery), patch.object(runner,'time',Clock()), \
                 patch('sys.argv',['test','--pro','MOCK','--cycles','2','--output',str(output)]):
                error=None
                try: runner.main()
                except Exception as caught: error=caught
            return json.loads(output.read_text()),commands,error

    def test_success_requires_two_disconnect_recover_cycles(self):
        report,commands,error=self.experiment()
        self.assertIsNone(error)
        self.assertTrue(report['passed'])
        self.assertEqual(commands,[b'HANG\n',b'HANG\n'])
        self.assertTrue(all(x['usb_disappearance_observed'] for x in report['cycles']))

    def test_unchanged_usb_presence_cannot_pass(self):
        report,_,error=self.experiment(disappears=False)
        self.assertIsNotNone(error); self.assertFalse(report['passed'])
        self.assertIn('inconclusive',report['error'])

    def test_changed_saved_setting_cannot_pass(self):
        report,_,error=self.experiment(changed=True)
        self.assertIsNotNone(error); self.assertFalse(report['passed'])

    def test_missing_device_never_sends_hang(self):
        report,commands,error=self.experiment(missing=True)
        self.assertIsNotNone(error); self.assertFalse(report['passed'])
        self.assertEqual(commands,[])


if __name__=='__main__': unittest.main()
