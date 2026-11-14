"""Offline acceptance/rejection tests; no instrument access."""
from pathlib import Path
import runpy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
evaluate = runpy.run_path(str(Path(__file__).resolve().parents[1]/'check-idle-pwm.py'))['evaluate']


class IdlePwmTests(unittest.TestCase):
    def waveform(self, period=100, width=50):
        raw = bytes(220 if i % period < width else 2 for i in range(20000))
        p = dict(points=len(raw), xincrement=1e-6, yorigin=0, yreference=0, yincrement=.02)
        return raw, p

    def test_good(self):
        self.assertTrue(evaluate(*self.waveform())['passed'])

    def test_wrong_frequency(self):
        self.assertFalse(evaluate(*self.waveform(110,55))['passed'])

    def test_wrong_duty(self):
        self.assertFalse(evaluate(*self.waveform(100,60))['passed'])

    def test_incomplete(self):
        raw, p = self.waveform()
        with self.assertRaises(ValueError):
            evaluate(raw[:-1], p)

    def test_static(self):
        raw, p = self.waveform()
        with self.assertRaises(ValueError):
            evaluate(bytes([220])*len(raw), p)

    def test_clipped(self):
        raw, p = self.waveform()
        raw = bytes(255 if value==220 else value for value in raw)
        self.assertFalse(evaluate(raw, p)['passed'])

    def test_wrong_level(self):
        raw, p = self.waveform()
        p['yincrement'] = .01
        self.assertFalse(evaluate(raw, p)['passed'])


if __name__ == '__main__':
    unittest.main()
