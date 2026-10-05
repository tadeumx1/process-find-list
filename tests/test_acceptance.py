"""Acceptance tests authored from the approved WSLazy plan, before implementation."""
import curses
import dataclasses
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from wslazy import core
from wslazy.ui import App, VIEWS


class Screen:
    def __init__(self, height=30, width=120):
        self.height, self.width = height, width
        self.writes = []
    def getmaxyx(self): return self.height, self.width
    def erase(self): self.writes.clear()
    def addnstr(self, y, x, text, n, *args): self.writes.append((y, x, text[:n]))
    def refresh(self): pass
    def text(self): return '\n'.join(s for _, _, s in self.writes)


class Backend:
    def __init__(self):
        self.calls, self.operations = [], []
        self.result = core.Snapshot([])
    def collect(self, view):
        self.calls.append(view)
        return self.result
    def signal_process(self, process, sig): self.operations.append(('signal', process.pid, sig))
    def service_action(self, service, action): self.operations.append(('service', service.name, action))


def process(pid=123, cpu=12.0, memory=4096, name='python', uid=1000, start=100):
    return core.Process(pid, uid, 'alice', name, f'{name} app.py', 'S', cpu, memory, start)


def settle(app):
    deadline = time.monotonic() + 2
    while app.busy() and time.monotonic() < deadline:
        time.sleep(.005)
        app.tick()
    if app.busy(): raise AssertionError('background job did not settle')


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.backend = Backend()
        self.screen = Screen()
        self.app = App(self.screen, backend=self.backend, runner=lambda argv, cwd: 0)
    def show(self, view, objects):
        self.app.view = view
        self.app.set_snapshot(view, core.make_snapshot(view, objects))
        self.app.render()
    def click(self, label):
        region = next(r for r in self.app.regions if r.label == label)
        self.app.mouse(region.x, region.y, curses.BUTTON1_CLICKED)
        self.app.render()
    def fake_proc(self, pid=123, start=100, ticks=50):
        root = self.home / 'proc'
        p = root / str(pid)
        p.mkdir(parents=True, exist_ok=True)
        fields = ['S', '1'] + ['0'] * 9 + [str(ticks), '0'] + ['0'] * 6 + [str(start), '0', '2']
        (p/'stat').write_text(f'{pid} (python worker) ' + ' '.join(fields))
        (p/'status').write_text('Name:\tpython\nUid:\t1000\t1000\t1000\t1000\n')
        (p/'cmdline').write_bytes(b'python\0app.py\0')
        (p/'comm').write_text('python\n')
        return root

    def test_ac01(self):
        self.assertEqual(VIEWS, ('Processes','Applications','Ports','Services','History'))
        self.show(0, [process()])
        text = self.screen.text()
        for name in VIEWS: self.assertIn(name, text)
        self.assertIn('Details', text)
        self.assertIn('python app.py', text)

    def test_ac02(self):
        sampler = core.ProcessSampler(self.fake_proc())
        p = sampler.sample(now=1)[0]
        self.assertEqual((p.pid,p.uid,p.name,p.command,p.state,p.memory,p.start),
                         (123,1000,'python','python app.py','S',2*os.sysconf('SC_PAGE_SIZE'),100))
        self.assertIsNone(p.cpu)
        self.fake_proc(ticks=150)
        p = sampler.sample(now=2)[0]
        self.assertAlmostEqual(p.cpu, 10000/os.sysconf('SC_CLK_TCK'))
        self.assertTrue(p.user)
        self.assertIn('—', core.make_snapshot(0, [dataclasses.replace(p,cpu=None)]).items[0].cells)

    def test_ac03(self):
        self.show(0,[process(123),process(456)])
        self.app.selected[0] = 1
        self.app.set_snapshot(0, core.make_snapshot(0,[process(456),process(123)]))
        self.assertEqual(self.app.current().payload.pid,456)
        self.app.last_refresh[0] = 10
        self.app.tick(now=11.9)
        self.assertEqual(self.backend.calls,[])
        self.app.tick(now=12)
        settle(self.app)
        self.assertEqual(self.backend.calls,[0])

    def test_ac04(self):
        groups=core.group_apps([process(1),process(2,cpu=3,memory=1024),process(3,uid=0)])
        self.assertEqual(len(groups),2)
        g=next(g for g in groups if g.uid==1000)
        self.assertEqual((g.name,g.cpu,g.memory,[p.pid for p in g.processes]),('python',15,5120,[1,2]))
        row=core.make_snapshot(1,[g]).items[0]
        self.assertIn('2',row.cells)
        self.assertIn('1',row.details)
        self.assertIn('2',row.details)

    def test_ac05(self):
        out='tcp LISTEN 0 128 [::]:8000 [::]:* users:(("python",pid=12,fd=3),("worker",pid=13,fd=3))\nudp UNCONN 0 0 127.0.0.1:53 0.0.0.0:*\n'
        with patch('wslazy.core.run_capture',return_value=out): ports=core.list_ports()
        self.assertEqual([(p.protocol,p.address,p.port) for p in ports],[('udp','127.0.0.1',53),('tcp','[::]',8000)])
        self.assertEqual(ports[1].owners,[('python',12),('worker',13)])

    def test_ac06(self):
        p=core.Port('tcp','0.0.0.0',9000,[])
        s=core.make_snapshot(2,[p])
        self.assertEqual(len(s.items),1)
        self.assertIn('owner unavailable',s.items[0].details)

    def test_ac07(self):
        out='db.service loaded active running Database\nidle.service loaded inactive dead Idle\n'
        with patch('wslazy.core.run_capture',return_value=out): services,errors=core.list_services()
        self.assertEqual(errors,[])
        self.assertEqual([(s.scope,s.name,s.state,s.description) for s in services],
            [('system','db.service','active/running','Database'),('system','idle.service','inactive/dead','Idle'),
             ('user','db.service','active/running','Database'),('user','idle.service','inactive/dead','Idle')])

    def test_ac08(self):
        for error,expected in [(FileNotFoundError(),'not found'),(subprocess.TimeoutExpired('ss',5),'5'),(core.SourceError('ss: failed'),'failed')]:
            with self.subTest(error=error), patch('wslazy.core.subprocess.run',side_effect=error):
                s=core.Backend().collect(2)
                self.assertIn('ss',s.error)
                self.assertIn(expected,s.error)
                self.app.set_snapshot(2,s)
                self.app.view=2
                self.app.render()
                self.assertIn('ss',self.screen.text())
                self.app.key('\t')
                self.assertEqual(self.app.view,3)
        with patch('wslazy.core.subprocess.run',return_value=subprocess.CompletedProcess([],1,'','broken')):
            self.assertIn('broken',core.Backend().collect(2).error)

    def test_ac09(self):
        self.show(0,[process(123),process(456,name='node')])
        for query,expected in [('PYTHON',123),('123',123),('NODE',456)]:
            self.app.queries[0]=query
            self.assertEqual([i.payload.pid for i in self.app.filtered()],[expected])
        self.show(2,[core.Port('tcp','127.0.0.1',8123,[('node',456)])])
        self.app.queries[2]='8123'
        self.assertEqual(len(self.app.filtered()),1)

    def test_ac10(self):
        self.show(0,[])
        self.assertIn('No results',self.screen.text())
        self.show(0,[process()]); self.app.queries[0]='nonexistent'; self.app.render()
        self.assertIn('No results',self.screen.text())

    def test_ac11(self):
        self.app.render()
        self.assertIn('Loading',self.screen.text())
        self.app.key('\t'); self.assertEqual(self.app.view,1)
        self.app.key('q'); self.assertFalse(self.app.running)

    def test_ac12(self):
        self.assertEqual([i.payload.pid for i in core.make_snapshot(0,[process(5,cpu=1),process(3,cpu=8),process(2,cpu=8)]).items],[2,3,5])
        gs=core.group_apps([process(1,cpu=1,name='a'),process(2,cpu=8,name='b')])
        self.assertEqual([i.payload.name for i in core.make_snapshot(1,gs).items],['b','a'])
        self.assertEqual([i.payload.port for i in core.make_snapshot(2,[core.Port('tcp','*',80,[]),core.Port('udp','*',53,[])]).items],[53,80])
        ss=[core.Service('z.service','user','active/running','Z'),core.Service('b.service','system','inactive/dead','B')]
        self.assertEqual([i.payload.name for i in core.make_snapshot(3,ss).items],['b.service','z.service'])
        es=[core.Entry('old','bash','b',0),core.Entry('new','bash','a',1),core.Entry('other','zsh','b',1)]
        self.assertEqual([i.payload.command for i in core.make_snapshot(4,es).items],['new','other','old'])

    def test_ac13(self):
        self.show(0,[process()])
        for action,sig in [('term','SIGTERM'),('kill','SIGKILL')]:
            self.app.action(action); self.app.render()
            self.assertIn('123',self.screen.text()); self.assertIn('python app.py',self.screen.text())
            self.assertIn(sig,self.screen.text()); self.assertEqual(self.backend.operations,[])
            self.app.key('\x1b')

    def test_ac14(self):
        self.show(0,[process()]); self.app.action('term'); self.app.key('\x1b')
        self.assertIsNone(self.app.dialog); self.assertEqual(self.backend.operations,[])
        self.assertEqual(self.app.view,0)

    def test_ac15(self):
        for sig in (signal.SIGTERM,signal.SIGKILL):
            child=subprocess.Popen(['sleep','30'],preexec_fn=os.setpgrp)
            control=subprocess.Popen(['sleep','30'],preexec_fn=lambda: os.setpgid(0,child.pid))
            try:
                p=next(p for p in core.ProcessSampler().sample() if p.pid==child.pid)
                core.signal_process(p,sig)
                self.assertEqual(child.wait(timeout=2),-sig)
                self.assertIsNone(control.poll(), 'signal must not reach another PID in the same group')
            finally:
                if child.poll() is None: child.kill(); child.wait()
                if control.poll() is None: control.kill(); control.wait()

    def test_ac16(self):
        child=subprocess.Popen(['sleep','30'])
        try:
            p=next(p for p in core.ProcessSampler().sample() if p.pid==child.pid)
            with self.assertRaisesRegex(core.SourceError,'Process is no longer available'):
                core.signal_process(dataclasses.replace(p,start=p.start+1),signal.SIGTERM)
            self.assertIsNone(child.poll())
            self.show(0,[dataclasses.replace(p,start=p.start+1)])
            with patch.object(self.backend,'signal_process',side_effect=core.signal_process):
                self.app.action('term'); self.app.confirm(); settle(self.app)
            self.assertIn('Process is no longer available',self.app.message)
            self.assertIn(0,self.backend.calls)
            self.assertEqual(self.app.filtered(),[])
            self.assertIsNone(child.poll())
            child.terminate(); child.wait()
            with self.assertRaisesRegex(core.SourceError,'Process is no longer available'):
                core.signal_process(p,signal.SIGTERM)
        finally:
            if child.poll() is None: child.kill(); child.wait()

    def test_ac17(self):
        self.show(0,[process()])
        with patch.object(self.backend,'signal_process',side_effect=PermissionError()):
            self.app.action('term'); self.app.confirm(); settle(self.app)
        self.assertIn('Permission denied',self.app.message)
        self.assertTrue(self.app.running)

    def test_ac18(self):
        ps=[process(1),process(2)]
        self.show(1,core.group_apps(ps)); self.app.action('term')
        self.assertEqual(self.app.dialog.kind,'choose')
        self.app.key('j'); self.app.key('\n'); self.app.render()
        self.assertEqual(self.app.dialog.kind,'confirm')
        self.assertIn('PID: 2',self.screen.text())
        self.assertEqual(self.backend.operations,[])
        self.app.key('\x1b')
        self.show(2,[core.Port('tcp','*',8000,[('python',1),('python',2)])])
        with patch('wslazy.ui.core.find_process',side_effect=lambda pid: process(pid)):
            self.app.action('term')
        self.assertEqual(self.app.dialog.kind,'choose')

    def test_ac19(self):
        self.show(3,[core.Service('demo.service','user','active/running','Demo')])
        for action in ('start','stop','restart'):
            self.app.action(action); self.app.render()
            for value in ('demo.service','user',action): self.assertIn(value,self.screen.text())
            self.assertEqual(self.backend.operations,[])
            self.app.key('\x1b')

    def test_ac20(self):
        for scope in ('system','user'):
            s=core.Service('demo.service',scope,'active/running','Demo')
            for action,verb in [('start','start'),('stop','stop'),('restart','restart')]:
                with patch('wslazy.core.subprocess.run',return_value=subprocess.CompletedProcess([],0,'','')) as run:
                    result=core.service_action(s,action)
                    argv=run.call_args.args[0]
                    self.assertIn(verb,argv); self.assertIn('demo.service',argv)
                    self.assertEqual('--user' in argv,scope=='user')
                    self.assertEqual(run.call_args.kwargs['timeout'],10)
                    self.assertIn('accepted',result)
            with patch('wslazy.core.subprocess.run',side_effect=subprocess.TimeoutExpired('systemctl',10)) as run:
                with self.assertRaisesRegex(core.SourceError,'10'): core.service_action(s,'stop')
                self.assertEqual(run.call_count,1)
            with patch('wslazy.core.subprocess.run',return_value=subprocess.CompletedProcess([],1,'','unit failed')):
                with self.assertRaisesRegex(core.SourceError,'unit failed'): core.service_action(s,'stop')

    def test_ac21(self):
        self.show(0,[process()]); self.app.action('term'); self.app.confirm(); settle(self.app)
        self.assertIn(0,self.backend.calls)
        self.assertIn('sent',self.app.message)
        self.assertNotIn('terminated',self.app.message)
        self.show(3,[core.Service('demo.service','system','active/running','Demo')])
        self.app.action('stop'); self.app.confirm(); settle(self.app)
        self.assertIn(3,self.backend.calls)

    def test_ac22(self):
        bash=self.home/'.bash_history'; bash.write_text(''.join(f'echo {i}\n' for i in range(2003)))
        (self.home/'.zsh_history').write_text(': 1:0;echo zsh\n')
        entries=core.read_history(self.home,str(bash))
        b=[e for e in entries if e.shell=='bash']
        self.assertEqual(len(b),2000)
        self.assertEqual({e.command for e in b},{f'echo {i}' for i in range(3,2003)})
        self.assertEqual(len(entries),2001)

    def test_ac23(self):
        (self.home/'.bash_history').write_text('#100\necho a\n#101\nprintf "a\nb"\n#102\necho a\n')
        (self.home/'.zsh_history').write_text(': 1:0;echo z\n: 2:0;echo first\\\necho second\n: 3:0;echo z\n')
        entries=core.read_history(self.home,None)
        b=[e.command for e in entries if e.shell=='bash']
        z=[e.command for e in entries if e.shell=='zsh']
        self.assertEqual(b,['echo a','printf "a\nb"'])
        self.assertEqual(z,['echo z','echo first\necho second'])
        self.assertTrue(all(e.source for e in entries))

    def test_ac24(self):
        self.show(4,[core.Entry('echo old','bash','history',0)])
        with patch.object(self.app,'runner') as run:
            self.app.action('execute'); self.app.render()
            self.assertEqual(self.app.dialog.kind,'edit')
            for value in ('echo old','bash',os.getcwd()): self.assertIn(value,self.screen.text())
            self.app.key('!')
            self.assertEqual(self.app.dialog.text,'echo old!')
            self.assertFalse(run.called)

    def test_ac25(self):
        output=self.home/'result'
        code=core.run_command(f'pwd > "{output}"; exit 7','bash',self.home)
        self.assertEqual(code,7)
        self.assertEqual(output.read_text().strip(),str(self.home))
        calls=[]
        self.app.runner=lambda argv,cwd: calls.append((argv,cwd)) or 7
        self.show(4,[core.Entry('echo old','bash','history',0)])
        self.app.action('execute'); self.app.dialog.text='echo revised'; self.app.confirm()
        self.assertEqual(calls[0][0][-2:],['-c','echo revised'])
        self.assertEqual(calls[0][1],os.getcwd())
        self.assertIn('7',self.app.message)
        self.assertIsNone(self.app.dialog)

    def test_ac26(self):
        with patch('wslazy.core.shutil.which',return_value=None):
            with self.assertRaisesRegex(core.SourceError,'Shell.*not found'): core.run_command('true','zsh',self.home)
        self.show(4,[core.Entry('true','bash','history',0)])
        self.app.runner=lambda argv,cwd: (_ for _ in ()).throw(OSError('cannot start'))
        self.app.action('execute'); self.app.confirm()
        self.assertIn('cannot start',self.app.message); self.assertTrue(self.app.running)

    def test_ac27(self):
        self.show(0,[process(1),process(2)])
        self.app.key('j'); self.assertEqual(self.app.selected[0],1)
        self.app.key('k'); self.assertEqual(self.app.selected[0],0)
        self.app.key(curses.KEY_DOWN); self.assertEqual(self.app.selected[0],1)
        self.app.key(curses.KEY_UP); self.assertEqual(self.app.selected[0],0)
        self.app.key('\t'); self.assertEqual(self.app.view,1)
        self.app.key(curses.KEY_BTAB); self.assertEqual(self.app.view,0)
        self.app.key('/'); self.assertTrue(self.app.searching)
        self.app.key('\x1b'); self.assertFalse(self.app.searching)
        self.app.key('?'); self.assertEqual(self.app.dialog.kind,'help')
        self.app.key('\x1b'); self.assertIsNone(self.app.dialog)
        self.app.key('q'); self.assertFalse(self.app.running)
        from tests.terminal import exercise_terminal
        result=exercise_terminal()
        self.assertEqual(result['exit'],0)
        self.assertTrue(result['restored'])
        self.assertIn('WSLazy',result['text'])

    def test_ac28(self):
        self.screen.width=60; self.screen.height=15; self.app.render()
        self.assertIn('80',self.screen.text()); self.assertIn('24',self.screen.text())
        self.screen.width=120; self.screen.height=30; self.app.render()
        self.assertIn('Processes',self.screen.text())
        self.screen.width=40; self.app.render(); self.app.key('q'); self.assertFalse(self.app.running)

    def test_ac29(self):
        root=self.fake_proc()
        (root/'999').mkdir(); (root/'999'/'stat').write_text('invalid')
        self.assertEqual([p.pid for p in core.ProcessSampler(root).sample()],[123])
        original=Path.read_text
        def read(path,*a,**kw):
            if str(path).endswith('/999/stat'): raise PermissionError()
            return original(path,*a,**kw)
        with patch.object(Path,'read_text',read):
            self.assertEqual([p.pid for p in core.ProcessSampler(root).sample()],[123])

    def test_ac30(self):
        for flags,code,text in [([],1,'Interactive terminal required'),(['--help'],0,'usage'),(['--version'],0,'0.1.0'),(['--unknown'],2,'error')]:
            r=subprocess.run([sys.executable,'-m','wslazy',*flags],capture_output=True,text=True)
            self.assertEqual(r.returncode,code)
            self.assertIn(text,r.stdout+r.stderr)
            if code:
                self.assertIn(text,r.stderr)
                self.assertEqual(r.stdout,'')
            else:
                self.assertIn(text,r.stdout)
                self.assertEqual(r.stderr,'')

    def test_ac31(self):
        from tests.install import exercise_install
        result=exercise_install(self.home)
        self.assertEqual(result['version'],'WSLazy 0.1.0')
        self.assertEqual(result['module'],'WSLazy 0.1.0')
        self.assertEqual(result['requires'],[])
        self.assertEqual(result['interactive']['exit'],0)
        self.assertTrue(result['interactive']['restored'])
        self.assertIn('WSLazy',result['interactive']['text'])
        self.assertIn('Processes',result['interactive']['text'])
        readme=Path('README.md').read_text()
        self.assertIn('python3 -m wslazy',readme)
        self.assertIn('pip install .',readme)

    def test_ac32(self):
        p=self.home/'.bash_history'; p.write_text('printf harmless\n')
        before=p.read_bytes()
        entries=core.read_history(self.home,str(p))
        self.show(4,entries); self.app.queries[4]='harmless'
        self.app.action('execute'); self.app.confirm()
        self.assertEqual(p.read_bytes(),before)
        zsh=self.home/'.zsh_history'; zsh.write_text(': 100:0;printf harmless\n')
        original={p:p.read_bytes(),zsh:zsh.read_bytes()}
        ran=[]
        def actual_shell(argv,cwd):
            result=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,
                                  env={**os.environ,'HISTFILE':str(p if 'bash' in argv[0] else zsh)})
            ran.append((Path(argv[0]).name,result.stdout,result.returncode))
            return result.returncode
        self.app.runner=actual_shell
        for shell in ('bash','zsh'):
            entries=core.read_history(self.home,str(p))
            self.show(4,[e for e in entries if e.shell==shell])
            self.app.action('execute'); self.app.confirm()
            self.assertEqual(p.read_bytes(),original[p])
            self.assertEqual(zsh.read_bytes(),original[zsh])
        self.assertEqual(ran,[('bash','harmless',0),('zsh','harmless',0)])

    def test_ac33(self):
        for index,name in enumerate(VIEWS):
            self.app.render(); self.click(name); self.assertEqual(self.app.view,index)
        self.show(0,[process(1),process(2)])
        self.click('row:1'); self.assertEqual(self.app.current().payload.pid,2)
        self.click('Search'); self.assertTrue(self.app.searching)
        self.app.key('\x1b'); self.app.render(); self.click('Terminate'); self.assertEqual(self.app.dialog.kind,'confirm')
        self.app.key('\x1b'); self.app.render(); self.click('Help'); self.assertEqual(self.app.dialog.kind,'help')
        self.app.key('\x1b'); self.app.render(); self.click('Quit'); self.assertFalse(self.app.running)
        self.app.running=True; self.show(4,[core.Entry('echo hi','bash','history',0)])
        self.click('Run'); self.click('Editor'); self.app.key('!')
        self.assertEqual(self.app.dialog.text,'echo hi!')

    def test_ac34(self):
        self.show(0,[process(i) for i in range(1,50)])
        r=next(r for r in self.app.regions if r.label=='row:0')
        self.app.mouse(r.x,r.y,curses.BUTTON5_PRESSED)
        self.assertGreater(self.app.selected[0],0)
        self.app.mouse(r.x,r.y,curses.BUTTON4_PRESSED)
        self.assertEqual(self.app.selected[0],0)
        r=next(r for r in self.app.regions if r.label=='Details')
        self.app.mouse(r.x,r.y,curses.BUTTON5_PRESSED)
        self.assertGreater(self.app.detail_scroll,0)
        self.assertEqual(self.app.selected[0],0)

    def test_ac35(self):
        self.show(0,[process()]); self.app.action('term'); self.app.render(); self.click('Cancel')
        self.assertEqual(self.backend.operations,[])
        self.app.action('term'); self.app.render(); self.click('Confirm'); settle(self.app)
        self.assertEqual(self.backend.operations,[('signal',123,signal.SIGTERM)])
        self.show(1,core.group_apps([process(1),process(2)])); self.app.action('term'); self.app.render()
        self.click('pid:1'); self.assertEqual(self.app.dialog.kind,'confirm')
        self.assertEqual(self.app.dialog.target.pid,2)
        self.app.key('\x1b')
        for use_mouse in (False,True):
            for error,message in [(PermissionError(),'Permission denied'),
                                  (core.SourceError('Process is no longer available'),'Process is no longer available')]:
                with self.subTest(mouse=use_mouse,error=message):
                    before=list(self.backend.operations)
                    self.show(0,[process()])
                    with patch.object(self.backend,'signal_process',side_effect=error):
                        if use_mouse:
                            self.click('Terminate'); self.click('Confirm')
                        else:
                            self.app.key('x'); self.app.key('\t'); self.app.key('\n')
                        settle(self.app)
                    self.assertIn(message,self.app.message)
                    self.assertEqual(self.backend.operations,before)
                    self.assertTrue(self.app.running)
                    self.assertIsNone(self.app.dialog)

    def test_ac36(self):
        self.app.key('?'); self.app.render()
        text=self.screen.text()
        for key in ('Tab','j/k','/','D','x','K','s','t','r','Enter','q'): self.assertIn(key,text)
        self.app.key('\x1b')
        with patch('wslazy.ui.curses.mousemask',side_effect=curses.error()): self.app.enable_mouse()
        self.app.key('\t'); self.assertEqual(self.app.view,1)
        self.app.key('q'); self.assertFalse(self.app.running)

    def test_ac37(self):
        exe=self.home/'lazydocker'; exe.write_text('#!/bin/sh\nprintf "%s" "$PWD" > marker\nexit 4\n'); exe.chmod(0o755)
        calls=[]
        def runner(argv,cwd):
            calls.append((argv,cwd))
            return subprocess.run(argv,cwd=cwd).returncode
        self.app.runner=runner
        with patch.dict(os.environ,{'PATH':str(self.home)}), patch('wslazy.ui.os.getcwd',return_value=str(self.home)):
            self.app.render(); self.click('Lazydocker')
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0],[str(exe)])
        self.assertEqual((self.home/'marker').read_text(),str(self.home))
        with patch.dict(os.environ,{'PATH':str(self.home)}), patch('wslazy.ui.os.getcwd',return_value=str(self.home)):
            self.app.key('D')
        self.assertEqual(len(calls),2)

    def test_ac38(self):
        self.show(0,[process(1),process(2)])
        self.app.selected[0]=1; self.app.queries[0]='python'
        self.app.runner=lambda argv,cwd: 4
        with patch('wslazy.ui.shutil.which',return_value='/bin/lazydocker'):
            self.app.action('lazydocker')
        self.assertEqual((self.app.view,self.app.selected[0],self.app.queries[0]),(0,1,'python'))
        self.assertIn('4',self.app.message)
        self.app.key('k'); self.assertEqual(self.app.selected[0],0)
        self.app.render(); self.click('Applications'); self.assertEqual(self.app.view,1)

    def test_ac39(self):
        with patch('wslazy.ui.shutil.which',return_value=None): self.app.action('lazydocker')
        self.assertIn('Lazydocker not found in PATH',self.app.message)
        self.assertTrue(self.app.running)

    def test_ac40(self):
        self.app.runner=lambda argv,cwd: (_ for _ in ()).throw(OSError('launch failed'))
        with patch('wslazy.ui.shutil.which',return_value='/bin/lazydocker'): self.app.action('lazydocker')
        self.assertIn('launch failed',self.app.message)
        self.assertTrue(self.app.running)
        self.app.key('\t'); self.assertEqual(self.app.view,1)
        self.app.render(); self.click('Processes'); self.assertEqual(self.app.view,0)
