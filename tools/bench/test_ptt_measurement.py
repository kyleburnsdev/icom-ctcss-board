"""Offline tests of paired-channel physical latency evaluation."""
import unittest
from ptt_measurement import evaluate


def record(at,rising):
    return bytes([2 if rising else 220])*at+bytes([220 if rising else 2])*(60000-at)


class PttTests(unittest.TestCase):
    def p(self):return dict(points=60000,xincrement=1e-6,xreference=0,xorigin=-.02)
    def test_press(self):
        result=evaluate(record(20000,False),self.p(),record(25000,True),self.p(),True)
        self.assertTrue(result['passed']);self.assertAlmostEqual(result['latency_ms'],5)
    def test_release(self):
        self.assertTrue(evaluate(record(20000,True),self.p(),record(25000,False),self.p(),False)['passed'])
    def test_too_late(self):
        self.assertFalse(evaluate(record(20000,False),self.p(),record(46000,True),self.p(),True)['passed'])
    def test_output_precedes_input(self):
        self.assertFalse(evaluate(record(20000,False),self.p(),record(15000,True),self.p(),True)['passed'])
    def test_extra_output_pulse(self):
        raw=record(25000,True);raw=raw[:35000]+bytes([2])*1000+raw[36000:]
        with self.assertRaises(ValueError):evaluate(record(20000,False),self.p(),raw,self.p(),True)
    def test_missing_output(self):
        with self.assertRaises(ValueError):evaluate(record(20000,False),self.p(),bytes([2])*60000,self.p(),True)
    def test_axes_misaligned(self):
        p=self.p();p['xorigin']+=1e-6
        with self.assertRaises(ValueError):evaluate(record(20000,False),self.p(),record(25000,True),p,True)
    def test_incomplete(self):
        with self.assertRaises(ValueError):evaluate(record(20000,False),self.p(),record(25000,True)[:-1],self.p(),True)
    def bounced(self,pressed):
        raw=bytearray([220 if pressed else 2])*60000
        for n in range(9):
            start=20000+n*1000
            raw[start:]=bytes([2 if ((n%2)==0)==pressed else 220])*(60000-start)
        return bytes(raw)
    def test_bounce_press_uses_final_stable_edge(self):
        r=evaluate(self.bounced(True),self.p(),record(33000,True),self.p(),True,bouncing=True)
        self.assertTrue(r['passed']);self.assertAlmostEqual(r['latency_ms'],5)
    def test_bounce_release_uses_final_stable_edge(self):
        self.assertTrue(evaluate(self.bounced(False),self.p(),record(33000,False),self.p(),False,bouncing=True)['passed'])
    def test_bounce_extra_output_pulse_rejected(self):
        raw=record(33000,True);raw=raw[:22000]+bytes([220])*1000+raw[23000:]
        with self.assertRaises(ValueError):evaluate(self.bounced(True),self.p(),raw,self.p(),True,bouncing=True)


if __name__=='__main__':unittest.main()
