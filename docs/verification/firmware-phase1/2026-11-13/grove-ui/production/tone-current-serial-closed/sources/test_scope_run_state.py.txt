"""Scope run-state preservation tests, without USB access."""
import unittest
from rigol_scope import Scope


class RunStateTests(unittest.TestCase):
    def model(self,state):
        scope=Scope();commands=[];current=[state]
        scope.q=lambda command:current[0]
        def write(command):
            commands.append(command);current[0]='STOP' if command==':STOP' else 'WAIT'
        scope.write=write
        return scope,commands
    def test_preserves_already_stopped_single(self):
        s,commands=self.model('STOP');s.running(False);self.assertEqual(commands,[])
    def test_preserves_already_running(self):
        s,commands=self.model('WAIT');s.running(True);self.assertEqual(commands,[])
    def test_stops_running(self):
        s,commands=self.model('WAIT');s.running(False);self.assertEqual(commands,[':STOP'])
    def test_starts_stopped(self):
        s,commands=self.model('STOP');s.running(True);self.assertEqual(commands,[':RUN'])


if __name__=='__main__':unittest.main()
