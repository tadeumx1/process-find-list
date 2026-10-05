"""Exercise the actual curses entry point in a pseudoterminal."""
import fcntl
import os
import pty
import select
import signal
import struct
import subprocess
import sys
import termios
import time


def exercise_terminal():
    master, slave = pty.openpty()
    fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',30,120,0,0))
    before=termios.tcgetattr(slave)
    proc=subprocess.Popen([sys.executable,'-m','wslazy'],stdin=slave,stdout=slave,stderr=slave,
                          env={**os.environ,'TERM':'xterm-256color'},start_new_session=True)
    output=bytearray()
    def drain(seconds):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if select.select([master],[],[],min(.05,max(0,end-time.monotonic())))[0]:
                try: output.extend(os.read(master,65536))
                except OSError: break
    try:
        drain(.5)
        for _ in range(5):
            os.write(master,b'\t'); drain(.12)
        # SGR mouse: select second view; wheel, help, then resize and recover.
        os.write(master,b'\x1b[<0;22;4M\x1b[<0;22;4m'); drain(.15)
        os.write(master,b'?'); drain(.12)
        os.write(master,b'\x1b'); drain(.15)
        fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',15,60,0,0))
        proc.send_signal(signal.SIGWINCH); drain(.15)
        fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',30,120,0,0))
        proc.send_signal(signal.SIGWINCH); drain(.15)
        os.write(master,b'q'); drain(.2)
        code=proc.wait(timeout=3)
        restored=termios.tcgetattr(slave)==before
        return {'exit':code,'restored':restored,'text':output.decode(errors='replace')}
    finally:
        if proc.poll() is None: proc.kill(); proc.wait()
        os.close(master); os.close(slave)
