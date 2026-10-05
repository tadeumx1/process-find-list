"""Additional boundary tests for the approved keyboard/mouse and process flows."""
import curses
import fcntl
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time
import threading
import unittest
from unittest.mock import patch
from tests.test_acceptance import Screen, Backend, process
from wslazy import core
from wslazy.ui import App


class Regressions(unittest.TestCase):
    def test_slow_collector_keeps_ui_responsive(self):
        gate=threading.Event()
        backend=Backend()
        backend.collect=lambda view: gate.wait(2) or core.Snapshot([])
        app=App(Screen(),backend=backend)
        try:
            app.collect(0)
            app.tick(now=app.collect_started[0]+5)
            app.render()
            self.assertIn('/proc',app.snapshots[0].error)
            self.assertIn('5 seconds',app.snapshots[0].error)
            app.key('\t'); self.assertEqual(app.view,1)
            app.key('q'); self.assertFalse(app.running)
        finally:
            gate.set()

    def test_bash_escaped_continuation(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory)
            (home/'.bash_history').write_text('echo first \\\nsecond\necho done\n')
            self.assertEqual([e.command for e in core.read_history(home)],['echo done','echo first \\\nsecond'])

    def test_click_does_not_confirm_twice(self):
        app=App(Screen(),backend=Backend())
        app.set_snapshot(0,core.make_snapshot(0,[process()]))
        app.action('term'); app.render()
        button=next(r for r in app.regions if r.label=='Confirm')
        app.mouse(button.x,button.y,curses.BUTTON1_CLICKED)
        app.mouse(button.x,button.y,curses.BUTTON1_CLICKED)
        from tests.test_acceptance import settle
        settle(app)
        self.assertEqual(app.backend.operations,[('signal',123,signal.SIGTERM)])

    def test_terminals_suspend_and_resume_mouse(self):
        # A real nested executable checks that WSLazy hands back canonical tty
        # mode, then the parent receives another real SGR click after it returns.
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory)
            tool=home/'lazydocker'; marker=home/'marker'
            tool.write_text('#!'+sys.executable+'\nimport termios,sys\nfrom pathlib import Path\n'
                +f'Path({str(marker)!r}).write_text(str(bool(termios.tcgetattr(0)[3] & termios.ICANON)))\n'
                +'sys.exit(9)\n')
            tool.chmod(0o755)
            master,slave=pty.openpty()
            fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',30,120,0,0))
            before=termios.tcgetattr(slave)
            proc=subprocess.Popen([sys.executable,'-m','wslazy'],stdin=slave,stdout=slave,stderr=slave,
                env={**os.environ,'PATH':str(home)+':'+os.environ['PATH'],'TERM':'xterm-256color'},start_new_session=True)
            data=bytearray()
            def read_until(needle, seconds=3):
                deadline=time.monotonic()+seconds
                start=len(data)
                while time.monotonic()<deadline:
                    if select.select([master],[],[],.05)[0]:
                        data.extend(os.read(master,65536))
                        if needle in bytes(data[start:]): return
                self.fail(f'Terminal did not display {needle!r}: {bytes(data[-2000:])!r}')
            try:
                read_until(b'WSLazy')
                # The toolbar button starts at x=83 (zero based), y=1.
                os.write(master,b'\x1b[<0;85;2M\x1b[<0;85;2m')
                read_until('exit code 9'.encode())
                self.assertEqual(marker.read_text(),'True')
                os.write(master,b'\x1b[<0;105;2M\x1b[<0;105;2m')
                read_until(b'Shortcuts and help')
                os.write(master,b'\x1b'); time.sleep(.08)
                os.write(master,b'q')
                self.assertEqual(proc.wait(timeout=3),0)
                self.assertEqual(termios.tcgetattr(slave),before)
            finally:
                if proc.poll() is None: proc.kill(); proc.wait()
                os.close(master); os.close(slave)
