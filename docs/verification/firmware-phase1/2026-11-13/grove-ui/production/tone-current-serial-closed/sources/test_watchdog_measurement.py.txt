"""Offline tests for the physical pre-HANG marker / D8 release evaluator."""
import unittest
from ptt_measurement import watchdog


def records():
    source=bytearray([2])*600000
    for start in (270000,270200,270400,270600):source[start:start+100]=bytes([220])*100
    output=bytes([220])*300000+bytes([2])*300000
    p=dict(points=600000,xincrement=1e-5,xreference=0,xorigin=-3,yincrement=.02,yorigin=0,yreference=0)
    return bytes(source),p,output,p.copy()


class WatchdogMeasurements(unittest.TestCase):
    def test_good_upper_bound(self):
        r=watchdog(*records());self.assertTrue(r['passed']);self.assertAlmostEqual(r['release_upper_bound_ms'],293)
    def test_late_release(self):
        a,p,_,q=records();output=bytes([220])*450000+bytes([2])*150000
        self.assertFalse(watchdog(a,p,output,q)['passed'])
    def test_rekey_rejected(self):
        a,p,b,q=records();b=b[:400000]+bytes([220])*10000+b[410000:]
        with self.assertRaises(ValueError):watchdog(a,p,b,q)
    def test_missing_marker(self):
        a,p,b,q=records()
        with self.assertRaises(ValueError):watchdog(bytes([2])*len(a),p,b,q)
    def test_oversized_marker_pulse(self):
        a,p,b,q=records();a=a[:270000]+bytes([220])*150+a[270150:]
        with self.assertRaises(ValueError):watchdog(a,p,b,q)
    def test_incomplete(self):
        a,p,b,q=records()
        with self.assertRaises(ValueError):watchdog(a[:-1],p,b,q)


if __name__=='__main__':unittest.main()
