"""Offline bypass/PWM response checks, with no instrument access."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bench.bypass_measurement import evaluate


def records(enabled,delay=.005,change=True):
    edge=.04
    source=bytes([220 if enabled else 2])*40000+bytes([2 if enabled else 220])*80000
    parts=[]
    for n in range(1200):
        t=n/10000
        envelope=max(0,min(1,(t-edge-delay)/.005)) if change else 0
        if enabled:envelope=1-envelope
        width=round(50+37.5*envelope*math.sin(2*math.pi*151.4*t))
        parts.append(bytes([220])*width+bytes([2])*(100-width))
    pwm=b''.join(parts)
    p=dict(points=120000,xincrement=1e-6,xreference=0,xorigin=-.04)
    return source,p,pwm,p.copy(),enabled


class BypassTests(unittest.TestCase):
    def test_suppression(self):
        r=evaluate(*records(True));self.assertTrue(r['passed']);self.assertLess(r['settled_midpoint_ms'],11)
    def test_resumption(self):
        r=evaluate(*records(False));self.assertTrue(r['passed']);self.assertLess(r['full_modulation_span_ms'],20)
    def test_late_suppression(self):self.assertFalse(evaluate(*records(True,delay=.04))['passed'])
    def test_never_suppresses(self):self.assertFalse(evaluate(*records(True,change=False))['passed'])
    def test_never_resumes(self):self.assertFalse(evaluate(*records(False,change=False))['passed'])
    def test_misaligned(self):
        a,p,b,q,enabled=records(True);q['xorigin']+=1e-6
        with self.assertRaises(ValueError):evaluate(a,p,b,q,enabled)
    def test_missing_carrier(self):
        a,p,b,q,enabled=records(True)
        with self.assertRaises(ValueError):evaluate(a,p,bytes([2])*len(b),q,enabled)


if __name__=='__main__':unittest.main()
