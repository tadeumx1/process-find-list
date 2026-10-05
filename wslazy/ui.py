"""Curses rendering and input; mouse and keyboard share the same action paths."""
from dataclasses import dataclass, field
import curses
import os
import queue
import shutil
import signal
import subprocess
import textwrap
import threading
import time
import unicodedata

from . import core

VIEWS = ('Processes', 'Applications', 'Ports', 'Services', 'History')
HEADERS = (('PID', 'USER', 'CPU', 'MEMORY', 'COMMAND'),
           ('APPLICATION', 'UID', 'PIDs', 'CPU', 'MEMORY'),
           ('PROTO', 'PORT', 'ADDRESS', 'OWNER'),
           ('UNIT', 'SCOPE', 'STATE', 'DESCRIPTION'), ('SHELL', 'COMMAND'))
HELP = '''NAVIGATION
Tab / Shift+Tab     next / previous view
1–5                open a view
↑ ↓ or j/k         select an item
PgUp / PgDn        scroll the list
[ / ]              scroll details
/                  search (Esc finishes; Ctrl+U clears)
Enter              details / run a history entry
F5                 refresh now

ACTIONS
x                  terminate process (SIGTERM)
K                  kill process (SIGKILL)
s / t / r          start / stop / restart service
D                  open Lazydocker in this terminal
?                  show this help
q                  quit WSLazy

DIALOGS
Tab                switch buttons / editor
Enter              activate button; in the editor, confirm execution
Esc                cancel / close
Editor: ← → Home End, Backspace, Delete, Ctrl+U clears
Ctrl+N inserts a new line; ↑ ↓ move between command lines

MOUSE
Click tabs, rows, fields, and buttons.
Scroll over the list to navigate, or over details to read more.
Mouse confirmations follow the same rules as the keyboard.

History runs in the current directory, without recreating the original session.
Lazydocker uses its own controls while it is open.
Shift + mouse selection usually copies text in your terminal.'''



@dataclass
class Region:
    label: str
    x: int
    y: int
    width: int
    height: int
    callback: object

    def contains(self, x, y):
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


@dataclass
class Dialog:
    kind: str
    title: str
    text: str = ''
    target: object = None
    action: str = ''
    choices: list = field(default_factory=list)
    selected: int = 0
    cursor: int = 0
    scroll: int = 0
    focus: int = 0
    cwd: str = ''


def safe_text(text):
    # A command/process name can contain terminal control bytes. Render them as
    # visible escapes; never let source data issue terminal commands.
    return ''.join(c if c.isprintable() else (' ' if c == '\t' else f'\\x{ord(c):02x}') for c in str(text))


def fit(text, width):
    result, used = [], 0
    for c in safe_text(text):
        size = 0 if unicodedata.combining(c) else (2 if unicodedata.east_asian_width(c) in 'WF' else 1)
        if used + size > width:
            break
        result.append(c)
        used += size
    return ''.join(result) + ' ' * max(0, width - used)


class App:
    def __init__(self, screen, backend=None, runner=None):
        self.screen = screen
        self.backend = backend or core.Backend()
        self.runner = runner or self.run_external
        self.view = 0
        self.snapshots = [None] * 5
        self.selected = [0] * 5
        self.queries = [''] * 5
        self.last_refresh = [float('-inf')] * 5
        self.collecting = set()
        self.collect_started = {}
        self.timed_out = set()
        self.results = queue.Queue()
        self.action_pending = False
        self.running = True
        self.searching = False
        self.dialog = None
        self.regions = []
        self.detail_scroll = 0
        self.message = 'Ready · click or use shortcuts · ? help'
        self.colors = False
        self.external_active = False

    def enable_mouse(self):
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            curses.mouseinterval(120)
        except curses.error:
            pass

    def start(self):
        self.screen.keypad(True)
        self.screen.timeout(100)
        curses.set_escdelay(30)
        try:
            curses.curs_set(0)
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
                for n, color in enumerate((curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_RED), 1):
                    curses.init_pair(n, color, -1)
                self.colors = True
        except curses.error:
            pass
        self.enable_mouse()
        while self.running:
            self.tick()
            self.render()
            try:
                key = self.screen.get_wch()
            except curses.error:
                continue
            if key == curses.KEY_MOUSE:
                try:
                    _, x, y, _, state = curses.getmouse()
                    self.mouse(x, y, state)
                except curses.error:
                    pass
            else:
                self.key(key)

    def busy(self):
        return bool(self.collecting or self.action_pending or not self.results.empty())

    def collect(self, view):
        if view in self.collecting:
            return
        self.collecting.add(view)
        self.collect_started[view] = time.monotonic()
        self.timed_out.discard(view)
        def worker():
            try:
                result = self.backend.collect(view)
            except Exception as exc:
                result = core.Snapshot([], core.error_text(exc))
            self.results.put(('snapshot', view, result))
        threading.Thread(target=worker, daemon=True, name=f'wslazy-collect-{view}').start()

    def tick(self, now=None):
        while True:
            try:
                kind, view, result = self.results.get_nowait()
            except queue.Empty:
                break
            if kind == 'snapshot':
                self.collecting.discard(view)
                self.collect_started.pop(view, None)
                self.timed_out.discard(view)
                self.set_snapshot(view, result)
            else:
                self.action_pending = False
                self.message = result
                self.last_refresh[view] = float('-inf')
                self.collect(view)
        now = time.monotonic() if now is None else now
        for view, started in tuple(self.collect_started.items()):
            if now-started >= 5 and view not in self.timed_out:
                source = ('/proc', '/proc', 'ss', 'systemctl', 'history')[view]
                old = self.snapshots[view]
                self.set_snapshot(view, core.Snapshot(old.items if old else [],
                    f'{source}: collection timed out after 5 seconds; waiting for the source'))
                self.timed_out.add(view)
        if now - self.last_refresh[self.view] >= 2:
            self.collect(self.view)

    def set_snapshot(self, view, snapshot):
        old = self.filtered(view)
        index = self.selected[view]
        identity = old[index].key if 0 <= index < len(old) else None
        self.snapshots[view] = snapshot
        new = self.filtered(view)
        self.selected[view] = next((i for i, row in enumerate(new) if row.key == identity), min(index, max(0, len(new)-1)))
        self.last_refresh[view] = time.monotonic()

    def filtered(self, view=None):
        view = self.view if view is None else view
        snapshot = self.snapshots[view]
        query = self.queries[view].casefold()
        return [item for item in snapshot.items if query in item.search] if snapshot else []

    def current(self):
        items = self.filtered()
        return items[min(self.selected[self.view], len(items)-1)] if items else None

    def switch(self, view):
        self.view = view % 5
        self.searching = False
        self.detail_scroll = 0

    def move(self, delta):
        self.selected[self.view] = max(0, min(self.selected[self.view] + delta, len(self.filtered())-1))
        self.detail_scroll = 0

    def attr(self, color=0, bold=False):
        return (curses.color_pair(color) if self.colors and color else 0) | (curses.A_BOLD if bold else 0)

    def put(self, y, x, text, width=None, attr=0):
        h, w = self.screen.getmaxyx()
        if not (0 <= y < h and 0 <= x < w):
            return
        width = max(0, min(w-x-1, width if width is not None else w-x-1))
        if not width:
            return
        try:
            self.screen.addnstr(y, x, fit(text, width), width * 2, attr)
        except curses.error:
            pass

    def region(self, label, x, y, width, height, callback):
        self.regions.append(Region(label, x, y, width, height, callback))

    def button(self, label, key, y, x, callback, selected=False):
        text = f' {label} [{key}] ' if key else f' {label} '
        self.put(y, x, text, len(text), curses.A_REVERSE if selected else self.attr(1, True))
        self.region(label, x, y, len(text), 1, callback)
        return x + len(text) + 1

    def columns(self, view, width):
        if view == 0: fixed = [7, 10, 7, 11]
        elif view == 1: fixed = [max(12, width-32), 7, 5, 8]
        elif view == 2: fixed = [6, 7, max(14, width//3)]
        elif view == 3: fixed = [max(18, width//3), 9, 17]
        else: fixed = [7]
        # Preserve useful columns on an 80-column terminal.
        while sum(fixed) >= width-8 and max(fixed) > 6:
            largest = fixed.index(max(fixed))
            fixed[largest] -= 1
        return fixed + [max(1, width-sum(fixed))]

    def row_text(self, cells, width):
        return ''.join(fit(cell, size-1) + ' ' for cell, size in zip(cells, self.columns(self.view, width)))

    def render(self):
        self.regions = []
        self.screen.erase()
        h, w = self.screen.getmaxyx()
        if w < 80 or h < 24:
            self.put(1, 1, 'Resize the terminal to at least 80 columns × 24 rows.')
            self.put(3, 1, 'q to quit')
            self.screen.refresh()
            return
        self.put(1, 2, 'WSLazy', 8, self.attr(1, True))
        self.put(1, 11, 'your WSL, in one place', w-52, self.attr(0))
        self.button('Lazydocker', 'D', 1, w-37, lambda: self.action('lazydocker'))
        self.button('Help', '?', 1, w-18, lambda: self.action('help'))
        x = 2
        for index, name in enumerate(VIEWS):
            x = self.button(name, str(index+1), 3, x, lambda i=index: self.switch(i), self.view == index)
        self.put(5, 2, f' / Search: {self.queries[self.view]}' + ('▏' if self.searching else ''), w-4,
                 self.attr(1) if self.searching else curses.A_DIM)
        self.region('Search', 2, 5, w-4, 1, self.begin_search)
        split = max(44, int(w * .61))
        width = split - 3
        self.put(7, 2, self.row_text(HEADERS[self.view], width), width, self.attr(1, True))
        self.put(7, split+2, 'Details · [ / ] or mouse wheel', w-split-4, self.attr(1, True))
        rows = h - 15
        items = self.filtered()
        index = min(self.selected[self.view], max(0, len(items)-1))
        self.selected[self.view] = index
        top = max(0, index - rows + 1)
        snapshot = self.snapshots[self.view]
        if snapshot is None:
            self.put(9, 2, 'Loading…', width, self.attr(3))
        elif not items:
            self.put(9, 2, 'No results', width, curses.A_DIM)
        for offset, item in enumerate(items[top:top+rows]):
            row_index = top + offset
            self.put(8+offset, 2, self.row_text(item.cells, width), width,
                     curses.A_REVERSE if row_index == index else 0)
            self.region(f'row:{row_index}', 2, 8+offset, width, 1, lambda i=row_index: self.select_row(i))
        current = self.current()
        detail_width = w - split - 4
        details = current.details if current else 'Select an item in the list.'
        lines = self.wrap(details, detail_width)
        for i, line in enumerate(lines[self.detail_scroll:self.detail_scroll+rows]):
            self.put(8+i, split+2, line, detail_width)
        self.region('Details', split+1, 8, w-split-2, rows, lambda: None)
        for y in range(7, h-6):
            self.put(y, split, '│', 1, curses.A_DIM)
        count = f'{len(items)} items · refresh 2s' + (' · collecting…' if self.view in self.collecting else '')
        self.put(h-6, 2, count, w-4, curses.A_DIM)
        if snapshot and snapshot.error:
            self.put(h-5, 2, snapshot.error.replace('\n', ' · '), w-4, self.attr(3))
        x = 2
        if self.view in (0, 1, 2):
            actions = [('Terminate','x','term'), ('Kill','K','kill')]
        elif self.view == 3:
            actions = [('Start','s','start'), ('Stop','t','stop'), ('Restart','r','restart')]
        else:
            actions = [('Run','Enter','execute')]
        for label, key, action in actions:
            x = self.button(label, key, h-4, x, lambda a=action: self.action(a))
        self.button('Refresh', 'F5', h-4, x, lambda: self.action('refresh'))
        self.button('Quit', 'q', h-4, w-13, lambda: self.action('quit'))
        self.put(h-2, 2, self.message, w-4, self.attr(2))
        if self.dialog:
            self.render_dialog()
        self.screen.refresh()

    @staticmethod
    def wrap(text, width):
        lines = []
        for line in text.split('\n'):
            lines.extend(textwrap.wrap(safe_text(line), max(1, width), replace_whitespace=False, drop_whitespace=False) or [''])
        return lines

    def render_dialog(self):
        d = self.dialog
        h, w = self.screen.getmaxyx()
        left, right, top, bottom = 4, w-5, 5, h-3
        width = right-left-2
        # Modal hit regions replace the background, preventing click-through.
        self.regions = []
        for y in range(top, bottom+1):
            self.put(y, left, ' ', right-left)
        self.put(top, left, '─'*(right-left), right-left, self.attr(1))
        self.put(top+1, left+2, d.title, width, self.attr(1, True))
        start = top+3
        available = bottom-start-2
        if d.kind == 'edit':
            self.put(start, left+2, f'Shell: {d.target.shell} · Directory: {d.cwd}', width)
            self.put(start+1, left+2, 'Review the full command · Enter runs · Ctrl+N new line · Esc cancels', width, curses.A_DIM)
            start += 3
            available -= 3
            # Display the insertion point as a visible marker, including multiline commands.
            text = d.text[:d.cursor] + '▏' + d.text[d.cursor:]
            lines = self.wrap(text, width)
            before = self.wrap(d.text[:d.cursor] + '▏', width)
            cursor_line = len(before)-1
            d.scroll = min(d.scroll, cursor_line)
            if cursor_line >= d.scroll + available:
                d.scroll = cursor_line-available+1
            self.region('Editor', left+2, start, width, max(1,available), lambda: self.editor_focus())
        elif d.kind == 'choose':
            lines = []
            offset = max(0, d.selected-available+1)
            for i, p in enumerate(d.choices[offset:offset+available], offset):
                y = start+i-offset
                self.put(y, left+2, f'PID {p.pid} · {p.command}', width, curses.A_REVERSE if d.selected == i else 0)
                self.region(f'pid:{i}', left+2, y, width, 1, lambda n=i: self.choose_pid(n))
        else:
            lines = self.wrap(d.text, width)
        if d.kind != 'choose':
            for i, line in enumerate(lines[d.scroll:d.scroll+available]):
                self.put(start+i, left+2, line, width)
        if d.kind == 'help':
            self.button('Close', 'Esc', bottom-1, left+2, lambda: self.close_dialog())
        else:
            self.button('Cancel', 'Esc', bottom-1, left+2, lambda: self.close_dialog(),
                        d.focus == (2 if d.kind == 'edit' else 0))
            if d.kind != 'choose':
                self.button('Confirm', 'Enter', bottom-1, right-24, self.confirm, d.focus == 1)

    def select_row(self, index):
        self.selected[self.view] = index
        self.detail_scroll = 0

    def begin_search(self):
        self.searching = True

    def editor_focus(self):
        if self.dialog: self.dialog.focus = 0

    def close_dialog(self):
        self.dialog = None

    def mouse(self, x, y, state):
        wheel_up = getattr(curses, 'BUTTON4_PRESSED', 0)
        wheel_down = getattr(curses, 'BUTTON5_PRESSED', 0)
        if state & (wheel_up | wheel_down):
            delta = -3 if state & wheel_up else 3
            if self.dialog:
                if self.dialog.kind == 'choose':
                    self.dialog.selected = max(0, min(len(self.dialog.choices)-1, self.dialog.selected+delta))
                else:
                    self.dialog.scroll = max(0, self.dialog.scroll+delta)
            elif any(r.label == 'Details' and r.contains(x,y) for r in self.regions):
                self.detail_scroll = max(0, self.detail_scroll+delta)
            elif y >= 8:
                self.move(delta)
            return
        # Request discrete clicks rather than both press and release: one gesture,
        # one action, even when launching and returning from an external TUI.
        if state & (curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED):
            for region in reversed(self.regions):
                if region.contains(x,y):
                    region.callback()
                    return

    def key(self, key):
        if key == curses.KEY_RESIZE:
            return
        h, w = self.screen.getmaxyx()
        if w < 80 or h < 24:
            if key == 'q': self.running = False
            return
        if self.dialog:
            self.dialog_key(key)
            return
        if self.searching:
            if key in ('\x1b', '\n', '\r'):
                self.searching = False
            elif key in ('\b', '\x7f', curses.KEY_BACKSPACE):
                self.queries[self.view] = self.queries[self.view][:-1]
            elif key == '\x15':
                self.queries[self.view] = ''
            elif isinstance(key,str) and key.isprintable():
                self.queries[self.view] += key
            self.selected[self.view] = 0
            return
        if key == '\t': self.switch(self.view+1)
        elif key == curses.KEY_BTAB: self.switch(self.view-1)
        elif isinstance(key,str) and key in ('1','2','3','4','5'): self.switch(int(key)-1)
        elif key in ('j',curses.KEY_DOWN): self.move(1)
        elif key in ('k',curses.KEY_UP): self.move(-1)
        elif key == curses.KEY_NPAGE: self.move(max(1,h-15))
        elif key == curses.KEY_PPAGE: self.move(-max(1,h-15))
        elif key == ']': self.detail_scroll += 3
        elif key == '[': self.detail_scroll = max(0,self.detail_scroll-3)
        elif key == '/': self.begin_search()
        elif key == '\x1b': self.queries[self.view] = ''; self.detail_scroll = 0
        else:
            actions = {'q':'quit','?':'help','D':'lazydocker','x':'term','K':'kill',
                       's':'start','t':'stop','r':'restart',curses.KEY_F5:'refresh',
                       '\n':'execute' if self.view == 4 else 'details', '\r':'execute' if self.view == 4 else 'details'}
            if key in actions: self.action(actions[key])

    def dialog_key(self, key):
        d = self.dialog
        if key == '\x1b':
            self.close_dialog()
            return
        if d.kind == 'choose':
            if key in ('j',curses.KEY_DOWN,'\t'): d.selected = min(len(d.choices)-1,d.selected+1)
            elif key in ('k',curses.KEY_UP,curses.KEY_BTAB): d.selected = max(0,d.selected-1)
            elif key in ('\n','\r'): self.choose_pid(d.selected)
            return
        if key in ('\t', curses.KEY_BTAB):
            d.focus = (d.focus+1) % (3 if d.kind == 'edit' else 2)
            return
        if key in ('\n','\r'):
            if d.kind == 'help': self.close_dialog()
            elif d.kind == 'edit' and d.focus != 2: self.confirm()
            elif d.kind == 'confirm' and d.focus == 1: self.confirm()
            else: self.close_dialog()
            return
        if d.kind == 'edit' and d.focus == 0:
            if key == curses.KEY_LEFT: d.cursor = max(0,d.cursor-1)
            elif key == curses.KEY_RIGHT: d.cursor = min(len(d.text),d.cursor+1)
            elif key == curses.KEY_HOME: d.cursor = d.text.rfind('\n',0,d.cursor)+1
            elif key == curses.KEY_END:
                end = d.text.find('\n',d.cursor)
                d.cursor = len(d.text) if end < 0 else end
            elif key == curses.KEY_UP:
                start = d.text.rfind('\n',0,d.cursor)+1
                previous = d.text.rfind('\n',0,max(0,start-1))+1
                d.cursor = min(max(0,start-1),previous+d.cursor-start)
            elif key == curses.KEY_DOWN:
                start = d.text.rfind('\n',0,d.cursor)+1
                following = d.text.find('\n',d.cursor)
                if following >= 0:
                    end = d.text.find('\n',following+1)
                    d.cursor = min(len(d.text) if end < 0 else end,following+1+d.cursor-start)
            elif key in ('\b','\x7f',curses.KEY_BACKSPACE):
                if d.cursor: d.text = d.text[:d.cursor-1]+d.text[d.cursor:]; d.cursor -= 1
            elif key == curses.KEY_DC: d.text = d.text[:d.cursor]+d.text[d.cursor+1:]
            elif key == '\x15': d.text = ''; d.cursor = 0
            elif key == '\x0e' or isinstance(key,str) and key.isprintable():
                char = '\n' if key == '\x0e' else key
                d.text = d.text[:d.cursor]+char+d.text[d.cursor:]
                d.cursor += len(char)
        elif key in ('j',curses.KEY_DOWN,curses.KEY_NPAGE): d.scroll += 1
        elif key in ('k',curses.KEY_UP,curses.KEY_PPAGE): d.scroll = max(0,d.scroll-1)

    def action(self, action):
        if self.dialog or self.external_active:
            return
        if action == 'quit': self.running = False; return
        if action == 'help': self.dialog = Dialog('help','Shortcuts and help',HELP); return
        if action == 'refresh': self.collect(self.view); return
        if action == 'lazydocker': self.launch_lazydocker(); return
        item = self.current()
        if not item:
            self.message = 'Select an item first'
            return
        if action == 'details': self.dialog = Dialog('help','Details',item.details); return
        if self.action_pending:
            self.message = 'Wait for the current operation'
            return
        if action == 'execute' and self.view == 4:
            entry = item.payload
            self.dialog = Dialog('edit','Run command · review',entry.command,entry,
                                 cursor=len(entry.command),cwd=os.getcwd())
        elif action in ('term','kill') and self.view in (0,1,2):
            try:
                if self.view == 0: choices = [item.payload]
                elif self.view == 1: choices = item.payload.processes
                else:
                    choices = [core.find_process(pid) for _,pid in item.payload.owners]
                if not choices:
                    self.message = 'owner unavailable'
                elif len(choices) == 1:
                    self.signal_dialog(choices[0],action)
                else:
                    self.dialog = Dialog('choose','Choose a single PID',action=action,choices=choices)
            except (OSError, core.SourceError) as exc:
                self.message = core.error_text(exc)
                self.collect(self.view)
        elif action in ('start','stop','restart') and self.view == 3:
            s = item.payload
            self.dialog = Dialog('confirm',f'Confirm: {action}',
                                 f'Unit: {s.name}\nScope: {s.scope}\nAction: {action}',s,action)

    def signal_dialog(self, process, action):
        sig = 'SIGTERM' if action == 'term' else 'SIGKILL'
        self.dialog = Dialog('confirm',f'Send {sig}?',f'PID: {process.pid}\nCommand: {process.command}\nSignal: {sig}\n\nOnly this process will receive the signal.',process,action)

    def choose_pid(self, index):
        d = self.dialog
        self.signal_dialog(d.choices[index],d.action)

    def confirm(self):
        d = self.dialog
        if d is None: return
        if d.kind == 'edit':
            if not d.text.strip():
                self.message = 'Command is empty'
                return
            try:
                argv = core.command_argv(d.text,d.target.shell)
                self.dialog = None
                self.run_tool(argv,d.cwd,'Command')
            except (OSError, core.SourceError) as exc:
                self.dialog = None
                self.message = core.error_text(exc)
            return
        if d.kind != 'confirm' or self.action_pending:
            return
        self.dialog = None
        self.action_pending = True
        view = self.view
        self.message = 'Running operation…'
        def worker():
            try:
                if d.action in ('term','kill'):
                    sig = signal.SIGTERM if d.action == 'term' else signal.SIGKILL
                    result = self.backend.signal_process(d.target,sig) or f'{signal.Signals(sig).name} sent to PID {d.target.pid}'
                else:
                    result = self.backend.service_action(d.target,d.action) or f'Operation {d.action} accepted; refreshing state'
            except Exception as exc:
                result = core.error_text(exc)
            self.results.put(('action',view,result))
        threading.Thread(target=worker,daemon=True,name='wslazy-action').start()

    def launch_lazydocker(self):
        executable = shutil.which('lazydocker')
        if not executable:
            self.message = 'Lazydocker not found in PATH'
            return
        self.run_tool([executable],os.getcwd(),'Lazydocker')

    def run_tool(self, argv, cwd, label):
        self.external_active = True
        try:
            code = self.runner(argv,cwd)
            self.message = f'{label} finished · exit code {code}'
        except (OSError, core.SourceError) as exc:
            self.message = f'{label}: {core.error_text(exc)}'
        finally:
            self.external_active = False
            self.last_refresh[self.view] = float('-inf')

    def run_external(self, argv, cwd):
        # All curses calls stay on the UI thread. Child shares the foreground
        # terminal; a caught (not ignored) SIGINT restores default handling on exec.
        curses.def_prog_mode()
        curses.mousemask(0)
        curses.endwin()
        handler = signal.signal(signal.SIGINT, lambda *_: None)
        try:
            code = subprocess.run(argv,cwd=cwd).returncode
            if len(argv) > 1 and argv[1] == '-c':
                print(f'\nCommand finished · exit code {code}')
                try: input('Press Enter to return to WSLazy…')
                except EOFError: pass
            return code
        finally:
            signal.signal(signal.SIGINT,handler)
            curses.reset_prog_mode()
            self.screen.keypad(True)
            self.screen.timeout(100)
            self.enable_mouse()
            curses.flushinp()
            self.screen.clear()
            self.screen.refresh()
