"""Offline supply shutdown checks; no hardware access."""
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
power=runpy.run_path(str(Path(__file__).with_name('check-board-power.py')))


class Supply:
    def __init__(self):
        self.enabled=False
        self.target=1.
        self.limit=.05
        self.ocp=True

    def state(self):
        return dict(enabled=self.enabled,voltage_target=self.target,current_limit=self.limit,
                    ocp_enabled=self.ocp,ovp_enabled=False,voltage=self.target if self.enabled else 0.,
                    current=.035 if self.enabled else 0.,regulation='CV' if self.enabled else 'CC')

    def configure(self,**values):
        if 'enabled' in values: self.enabled=values['enabled']=='yes'
        if 'voltage_target' in values: self.target=float(values['voltage_target'])
        if 'current_limit' in values: self.limit=float(values['current_limit'])
        if 'ocp_enabled' in values: self.ocp=values['ocp_enabled']=='yes'

    def off(self):
        self.enabled=False
        return self.state()


class Meter:
    def __init__(self,bad=False):
        self.values=iter([0]+([3.] if bad else [5.]*8+[0]))

    def state(self):
        return dict(function='VOLT',secondary='NONE',auto='1',rate='S',math='NONE',range='10 V',offset='0')

    def query(self,command):
        return str(next(self.values))


class BoardPowerTests(unittest.TestCase):
    def check_off(self,supply,report):
        self.assertFalse(supply.enabled)
        self.assertEqual(supply.target,1)
        self.assertEqual(supply.limit,.05)
        self.assertTrue(supply.ocp)
        self.assertFalse(report['supply_final']['enabled'])

    @patch('time.sleep')
    def test_good_shutdown(self,_):
        supply,report=Supply(),{}
        power['run'](supply,Meter(),report)
        self.assertTrue(report['measurement_checks_passed'])
        self.check_off(supply,report)

    @patch('time.sleep')
    def test_bad_vcc_shutdown(self,_):
        supply,report=Supply(),{}
        with self.assertRaises(RuntimeError): power['run'](supply,Meter(True),report)
        self.check_off(supply,report)

    @patch('time.sleep')
    @patch('subprocess.run',side_effect=subprocess.TimeoutExpired('capture',120))
    def test_capture_timeout_shutdown(self,subprocess_mock,_):
        supply,report=Supply(),{}
        experiment=dict(key='test_capture',script='unused.py',output=Path('unused'),arguments=[],timeout_s=120)
        with self.assertRaises(subprocess.TimeoutExpired):
            power['run'](supply,Meter(),report,experiment=experiment)
        self.check_off(supply,report)


if __name__=='__main__':
    unittest.main()
