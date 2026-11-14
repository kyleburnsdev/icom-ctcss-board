"""Small exclusive-owner client for the two firmware text protocols."""
import time
import serial


class Device:
    def __init__(self,port,kind,transcript):
        self.port,self.kind,self.transcript=port,kind,transcript
        self.connection=serial.Serial(port,115200,timeout=.1,write_timeout=1)
        time.sleep(.2)
        self.connection.reset_input_buffer()

    def command(self,command):
        self.connection.write((command+'\n').encode('ascii'))
        raw=bytearray();until=time.monotonic()+2
        while not raw.endswith(b'\n'):
            if time.monotonic()>until:raise TimeoutError(f'{self.port}: incomplete {command} reply')
            raw.extend(self.connection.read(1))
        reply=raw.decode('ascii').strip()
        self.transcript.append({'port':self.port,'command':command,'reply':reply})
        if reply.startswith('ERR'):raise RuntimeError(f'{self.port}: {reply}')
        return reply

    def status(self):
        reply=self.command('STATUS')
        prefix='CTCSS1 ' if self.kind=='arduino' else 'STATUS '
        if not reply.startswith(prefix):raise RuntimeError(f'Unexpected status: {reply}')
        return {k:int(v) for word in reply.split() if '=' in word for k,v in [word.split('=',1)]}

    def close(self):self.connection.close()

    def reopen(self):
        self.connection.close()
        self.connection=serial.Serial(self.port,115200,timeout=.1,write_timeout=1)
        time.sleep(.2)
        self.connection.reset_input_buffer()

    def save(self,tone):
        # Wait for any already queued durable save before restoring a selection.
        until=time.monotonic()+2
        while self.status()['busy']:
            if time.monotonic()>until:raise TimeoutError('Prior save did not finish')
            time.sleep(.02)
        if not self.command(f'SAVE {tone}').startswith('OK'):raise RuntimeError('Save not queued')
        until=time.monotonic()+2
        while time.monotonic()<until:
            state=self.status()
            if not state['busy']:
                if state['saved']!=tone:raise RuntimeError('Saved selection mismatch')
                return
            time.sleep(.02)
        raise TimeoutError('Durable save did not finish')
