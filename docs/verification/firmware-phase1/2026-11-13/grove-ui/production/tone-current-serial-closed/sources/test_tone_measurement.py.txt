"""Independent synthetic PWM acceptance/rejection tests; no hardware access."""
import math
import unittest
from tone_measurement import evaluate_tone


def waveform(hz, peak=37.5):
    raw = b''.join(bytes([220])*width+bytes([2])*(100-width)
                   for width in (round(50+peak*math.sin(2*math.pi*hz*n/10000))
                                 for n in range(30000)))
    return raw, dict(points=len(raw), xincrement=1e-6)


class ToneTests(unittest.TestCase):
    def test_endpoints_and_middle(self):
        for hz in (67,151.4,254.1):
            with self.subTest(hz=hz):
                self.assertTrue(evaluate_tone(*waveform(hz),hz)['passed'])

    def test_wrong_frequency(self):
        self.assertFalse(evaluate_tone(*waveform(151.4),100)['passed'])

    def test_missing_period(self):
        raw,p=waveform(151.4)
        raw=raw[:100000]+bytes([2])*100+raw[100100:]
        self.assertFalse(evaluate_tone(raw,p,151.4)['passed'])

    def test_no_modulation(self):
        with self.assertRaises(ValueError):
            evaluate_tone(*waveform(151.4,0),151.4)

    def test_insufficient_modulation(self):
        self.assertFalse(evaluate_tone(*waveform(151.4,10),151.4)['passed'])

    def test_incomplete(self):
        raw,p=waveform(151.4)
        with self.assertRaises(ValueError):
            evaluate_tone(raw[:-1],p,151.4)


if __name__ == '__main__':
    unittest.main()
