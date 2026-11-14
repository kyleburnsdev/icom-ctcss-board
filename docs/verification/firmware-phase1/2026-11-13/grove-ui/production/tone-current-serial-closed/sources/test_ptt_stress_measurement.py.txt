import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bench.ptt_stress_measurement import evaluate


class StressTests(unittest.TestCase):
    def data(self,delay=.005):
        p=dict(points=600000,xincrement=1e-5,xorigin=-3.,xreference=0,
               yincrement=.02,yorigin=0,yreference=0)
        a=bytearray([220])*600000;b=bytearray([20])*600000
        for pair in range(8):
            first=300000+pair*12000;last=first+4000;d=round(delay/1e-5)
            a[first:last]=bytes([40])*4000
            b[first+d:last+d]=bytes([220])*4000
        return a,p,b,p.copy()

    def test_all_edges_measured(self):
        r=evaluate(*self.data(),8)
        self.assertEqual(r['transitions'],16)
        self.assertAlmostEqual(r['max_latency_ms'],5)

    def test_late_response(self):
        with self.assertRaises(ValueError):evaluate(*self.data(.03),8)

    def test_extra_output_glitch(self):
        a,p,b,q=self.data();b[200000:200010]=bytes([220])*10
        with self.assertRaises(ValueError):evaluate(a,p,b,q,8)

    def test_missing_output(self):
        a,p,b,q=self.data();b[300500:304500]=bytes([20])*4000
        with self.assertRaises(ValueError):evaluate(a,p,b,q,8)

    def test_missing_samples(self):
        a,p,b,q=self.data()
        with self.assertRaises(ValueError):evaluate(a[:-1],p,b,q,8)

    def test_axis_mismatch(self):
        a,p,b,q=self.data();q['xorigin']+=.001
        with self.assertRaises(ValueError):evaluate(a,p,b,q,8)

    def test_untriggered_record(self):
        a,p,b,q=self.data();p['xorigin']=-2.;q['xorigin']=-2.
        with self.assertRaises(ValueError):evaluate(a,p,b,q,8)

    def test_insufficient_posthistory(self):
        a,p,b,q=self.data();p['xincrement']=q['xincrement']=1e-5
        # Add expected events near the end, reducing post-release confirmation.
        a[596000:599000]=bytes([40])*3000;b[596500:599500]=bytes([220])*3000
        with self.assertRaises(ValueError):evaluate(a,p,b,q,9)


if __name__=='__main__':unittest.main()
