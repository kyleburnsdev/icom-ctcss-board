"""Offline loaded-collector acceptance tests; no hardware access."""
from pathlib import Path
import runpy
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
evaluate = runpy.run_path(str(Path(__file__).resolve().parents[1]/'check-board-ptt.py'))['evaluate']


class BoardPttTests(unittest.TestCase):
    def data(self, pressed=True, delay=5000, collector_low=4):
        p = dict(points=120000,xincrement=1e-6,xorigin=-.06,xreference=0,yorigin=0,yreference=0,yincrement=.025)
        high,low = (200,40) if pressed else (40,200)
        ih = bytes([high])*60000 + bytes([low])*60000
        before,after = (200,collector_low) if pressed else (collector_low,200)
        oh = bytes([before])*(60000+delay)+bytes([after])*(60000-delay)
        return ih,p,oh,p,pressed

    def test_press_and_release(self):
        for pressed in [True,False]:
            result = evaluate(*self.data(pressed))
            self.assertTrue(result['passed'])
            self.assertAlmostEqual(result['latency_ms'],5)

    def test_slow_response(self):
        self.assertFalse(evaluate(*self.data(delay=30000))['passed'])

    def test_bad_sink_voltage(self):
        self.assertFalse(evaluate(*self.data(collector_low=40))['passed'])

    def test_mismatched_axes(self):
        ir,ip,oh,op,pressed = self.data()
        with self.assertRaises(ValueError):
            evaluate(ir,ip,oh,dict(op,xorigin=0),pressed)

    def test_missing_transition(self):
        ir,ip,oh,op,pressed = self.data()
        with self.assertRaises(ValueError):
            evaluate(ir,ip,bytes([200])*len(oh),op,pressed)

    def test_extra_pulse(self):
        ir,ip,oh,op,pressed = self.data()
        bad = oh[:10000]+bytes([4])*100+oh[10100:]
        with self.assertRaises(ValueError):
            evaluate(ir,ip,bad,op,pressed)


if __name__=='__main__':
    unittest.main()
