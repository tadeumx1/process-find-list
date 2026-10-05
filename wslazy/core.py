"""Linux collectors and explicit operations, independent of the terminal UI."""
from collections import deque
from dataclasses import dataclass, field
import os
from pathlib import Path
import pwd
import re
import shutil
import signal
import subprocess
import time


class SourceError(Exception):
    """A source or operation failed; safe to display to the user."""


@dataclass
class Process:
    pid: int
    uid: int
    user: str
    name: str
    command: str
    state: str
    cpu: float | None
    memory: int | None
    start: int


@dataclass
class Application:
    name: str
    uid: int
    processes: list
    cpu: float | None
    memory: int | None


@dataclass
class Port:
    protocol: str
    address: str
    port: int
    owners: list


@dataclass
class Service:
    name: str
    scope: str
    state: str
    description: str


@dataclass
class Entry:
    command: str
    shell: str
    source: str
    position: int


@dataclass
class Item:
    key: object
    cells: tuple
    details: str
    payload: object

    @property
    def search(self):
        return (' '.join(self.cells) + '\n' + self.details).casefold()


@dataclass
class Snapshot:
    items: list
    error: str = ''


def error_text(exc):
    return 'Permissão negada' if isinstance(exc, PermissionError) else str(exc)


def stat_fields(path):
    # comm may contain spaces and parentheses; the final ')' delimits it.
    text = path.read_text()
    return text[text.rindex(')') + 2:].split()


def process_start(pid, root=Path('/proc')):
    return int(stat_fields(root / str(pid) / 'stat')[19])


class ProcessSampler:
    def __init__(self, root=Path('/proc')):
        self.root = Path(root)
        self.previous = {}
        self.clock = os.sysconf('SC_CLK_TCK')
        self.page = os.sysconf('SC_PAGE_SIZE')
        self.users = {}

    def sample(self, now=None):
        now = time.monotonic() if now is None else now
        result, previous = [], {}
        try:
            paths = list(self.root.iterdir())
        except OSError as exc:
            raise SourceError(f'/proc: {error_text(exc)}') from exc
        for path in paths:
            if not path.name.isdigit():
                continue
            try:
                fields = stat_fields(path / 'stat')
                start, ticks = int(fields[19]), int(fields[11]) + int(fields[12])
                pid = int(path.name)
                key = (pid, start)
                old = self.previous.get(key)
                cpu = max(0.0, (ticks - old[0]) / self.clock / (now - old[1]) * 100) if old and now > old[1] else None
                previous[key] = (ticks, now)
                status = (path / 'status').read_text()
                uid = int(re.search(r'^Uid:\s+(\d+)', status, re.M)[1])
                if uid not in self.users:
                    try:
                        self.users[uid] = pwd.getpwuid(uid).pw_name
                    except KeyError:
                        self.users[uid] = str(uid)
                try:
                    name = (path / 'comm').read_text().strip()
                except OSError:
                    name = '—'
                try:
                    command = (path / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip() or f'[{name}]'
                except OSError:
                    command = '—'
                # Reject a PID that changed identity while individual files were read.
                if process_start(pid, self.root) != start:
                    continue
                result.append(Process(pid, uid, self.users[uid], name, command,
                                      fields[0], cpu, int(fields[21]) * self.page, start))
            except (OSError, ValueError, IndexError, TypeError):
                continue
        self.previous = previous
        return result


def find_process(pid):
    # One fresh read for a port owner; no stale PID-only action is permitted.
    for p in ProcessSampler().sample():
        if p.pid == pid:
            return p
    raise SourceError('Processo não está mais disponível')


def group_apps(processes):
    groups = {}
    for p in processes:
        groups.setdefault((p.name, p.uid), []).append(p)
    return [Application(name, uid, sorted(ps, key=lambda p: p.pid),
                        sum(p.cpu for p in ps if p.cpu is not None) if any(p.cpu is not None for p in ps) else None,
                        sum(p.memory for p in ps if p.memory is not None) if any(p.memory is not None for p in ps) else None)
            for (name, uid), ps in groups.items()]


def run_capture(argv, timeout=5):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, errors='replace',
                                timeout=timeout, env={**os.environ, 'LC_ALL': 'C'}, stdin=subprocess.DEVNULL)
    except FileNotFoundError as exc:
        raise SourceError(f'{argv[0]}: não encontrado') from exc
    except subprocess.TimeoutExpired as exc:
        raise SourceError(f'{argv[0]}: limite de {timeout} segundos; estado final não confirmado') from exc
    except OSError as exc:
        raise SourceError(f'{argv[0]}: {error_text(exc)}') from exc
    if result.returncode:
        message = (result.stderr or result.stdout).strip() or f'código {result.returncode}'
        if 'denied' in message.lower() or 'authentication' in message.lower():
            message = f'Permissão negada: {message}'
        raise SourceError(f'{argv[0]}: {message}')
    return result.stdout


def list_ports():
    output = run_capture(['ss', '-H', '-lntup'])
    result = []
    for line in output.splitlines():
        parts = line.split(None, 6)
        if len(parts) < 6:
            continue
        address, _, port = parts[4].rpartition(':')
        if parts[0] not in ('tcp', 'udp') or not port.isdigit():
            continue
        owners = [(name, int(pid)) for name, pid in re.findall(r'\("([^"\n]+)",pid=(\d+)', line)]
        result.append(Port(parts[0], address, int(port), list(dict.fromkeys(owners))))
    return sorted(result, key=lambda p: (p.port, p.protocol, p.address))


def list_services():
    result, errors = [], []
    for scope in ('sistema', 'usuário'):
        argv = ['systemctl', *( ['--user'] if scope == 'usuário' else []),
                'list-units', '--type=service', '--all', '--plain', '--no-pager', '--no-legend']
        try:
            output = run_capture(argv)
        except SourceError as exc:
            errors.append(f'{scope}: {exc}')
            continue
        for line in output.splitlines():
            parts = line.strip().lstrip('● ').split(None, 4)
            if len(parts) >= 4 and parts[0].endswith('.service'):
                result.append(Service(parts[0], scope, f'{parts[2]}/{parts[3]}', parts[4] if len(parts) == 5 else ''))
    return sorted(result, key=lambda s: (s.scope, s.name)), errors


def _history_commands(path, shell):
    """Stream logical entries; the 2,000-entry bound is applied before deduplication."""
    pending = []
    timestamped = False
    continuation = False
    with path.open(errors='replace') as source:
        for raw in source:
            line = raw.rstrip('\n')
            if shell == 'zsh':
                match = re.match(r'^: \d+:\d+;(.*)$', line)
                if match and not continuation:
                    if pending:
                        yield '\n'.join(pending)
                        pending = []
                    line = match[1]
                continuation = line.endswith('\\')
                pending.append(line[:-1] if continuation else line)
                if not continuation:
                    yield '\n'.join(pending)
                    pending = []
            elif re.fullmatch(r'#\d{3,}', line) and not continuation:
                timestamped = True
                if pending:
                    yield '\n'.join(pending)
                    pending = []
            else:
                pending.append(line)
                continuation = line.endswith('\\') and (len(line) - len(line.rstrip('\\'))) % 2 == 1
                if not timestamped and not continuation:
                    yield '\n'.join(pending)
                    pending = []
        if pending:
            yield '\n'.join(pending)


def read_history(home=None, histfile=None):
    home = Path.home() if home is None else Path(home)
    paths = []
    if histfile:
        guessed = 'zsh' if 'zsh' in str(histfile).lower() else ('zsh' if Path(os.environ.get('SHELL', '')).name == 'zsh' else 'bash')
        paths.append((Path(histfile).expanduser(), guessed))
    paths.extend([(home / '.bash_history', 'bash'), (home / '.zsh_history', 'zsh')])
    seen_paths, entries = set(), []
    for path, shell in paths:
        resolved = path.resolve()
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        # A conventional filename overrides the current shell for HISTFILE.
        if path.name == '.bash_history': shell = 'bash'
        if path.name == '.zsh_history': shell = 'zsh'
        if not path.exists():
            continue
        try:
            commands = deque(_history_commands(path, shell), maxlen=2000)
        except OSError as exc:
            raise SourceError(f'{path}: {error_text(exc)}') from exc
        seen_commands = set()
        for pos in range(len(commands) - 1, -1, -1):
            command = commands[pos]
            if command.strip() and command not in seen_commands:
                seen_commands.add(command)
                entries.append(Entry(command, shell, str(path), pos))
    return sorted(entries, key=lambda e: (-e.position, e.source))


def signal_process(process, sig):
    if sig not in (signal.SIGTERM, signal.SIGKILL):
        raise SourceError('Sinal inválido')
    # pidfd pins the process so a recycle between verification and signal cannot
    # redirect the operation. Refuse on older kernels instead of a racy kill(pid).
    if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
        raise SourceError('Encerramento seguro exige suporte a pidfd neste Python/kernel')
    try:
        fd = os.pidfd_open(process.pid)
        try:
            if process_start(process.pid) != process.start:
                raise SourceError('Processo não está mais disponível')
            signal.pidfd_send_signal(fd, sig)
        finally:
            os.close(fd)
    except (ProcessLookupError, FileNotFoundError):
        raise SourceError('Processo não está mais disponível') from None
    except PermissionError:
        raise SourceError('Permissão negada') from None
    return f'{signal.Signals(sig).name} enviado ao PID {process.pid}'


def service_action(service, action):
    verbs = {'iniciar': 'start', 'parar': 'stop', 'reiniciar': 'restart'}
    argv = ['systemctl', '--no-ask-password', *( ['--user'] if service.scope == 'usuário' else []),
            verbs[action], '--', service.name]
    run_capture(argv, timeout=10)
    return f'Operação {action} aceita para {service.name}; atualizando estado'


def command_argv(command, shell):
    if shell not in ('bash', 'zsh'):
        raise SourceError(f'Shell {shell} não suportado')
    executable = shutil.which(shell)
    if not executable:
        raise SourceError(f'Shell {shell} não encontrado')
    return [executable, '-c', command]


def run_command(command, shell, cwd):
    return subprocess.run(command_argv(command, shell), cwd=cwd).returncode


def human_memory(value):
    if value is None: return '—'
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        if value < 1024: return f'{value:.1f} {unit}'
        value /= 1024
    return f'{value:.1f} PiB'


def percent(value):
    return '—' if value is None else f'{value:.1f}%'


def process_details(p):
    return (f'PID: {p.pid}\nUsuário: {p.user} (UID {p.uid})\nEstado: {p.state}\n'
            f'CPU: {percent(p.cpu)}\nMemória: {human_memory(p.memory)}\nInício (ticks): {p.start}\n\nComando:\n{p.command}')


def make_snapshot(view, objects, error=''):
    items = []
    if view == 0:
        for p in sorted(objects, key=lambda p: (-(p.cpu or 0), p.pid)):
            items.append(Item((p.pid, p.start), (str(p.pid), p.user, percent(p.cpu), human_memory(p.memory), p.command), process_details(p), p))
    elif view == 1:
        for a in sorted(objects, key=lambda a: (-(a.cpu or 0), a.name, a.uid)):
            details = f'{a.name}\nUID: {a.uid}\nProcessos: {len(a.processes)}\nCPU: {percent(a.cpu)}\nMemória: {human_memory(a.memory)}\n\n'
            details += '\n\n'.join(process_details(p) for p in a.processes)
            items.append(Item((a.name, a.uid), (a.name, str(a.uid), str(len(a.processes)), percent(a.cpu), human_memory(a.memory)), details, a))
    elif view == 2:
        for p in sorted(objects, key=lambda p: (p.port, p.protocol, p.address)):
            owners = ', '.join(f'{name} (PID {pid})' for name, pid in p.owners) or 'proprietário indisponível'
            items.append(Item((p.protocol, p.address, p.port), (p.protocol.upper(), str(p.port), p.address, owners),
                              f'{p.protocol.upper()} {p.address}:{p.port}\n\n{owners}', p))
    elif view == 3:
        for s in sorted(objects, key=lambda s: (s.scope, s.name)):
            items.append(Item((s.scope, s.name), (s.name, s.scope, s.state, s.description),
                              f'Unidade: {s.name}\nEscopo: {s.scope}\nEstado: {s.state}\n\n{s.description}', s))
    else:
        for e in sorted(objects, key=lambda e: (-e.position, e.source)):
            items.append(Item((e.source, e.command), (e.shell, e.command.replace('\n', ' ↵ ')),
                              f'Shell: {e.shell}\nOrigem: {e.source}\n\n{e.command}', e))
    return Snapshot(items, error)


class Backend:
    def __init__(self):
        self.samplers = {0: ProcessSampler(), 1: ProcessSampler()}

    def collect(self, view):
        try:
            if view in (0, 1):
                ps = self.samplers[view].sample()
                return make_snapshot(view, ps if view == 0 else group_apps(ps))
            if view == 2: return make_snapshot(view, list_ports())
            if view == 3:
                services, errors = list_services()
                return make_snapshot(view, services, '\n'.join(errors))
            return make_snapshot(view, read_history(histfile=os.environ.get('HISTFILE')))
        except (SourceError, OSError) as exc:
            return Snapshot([], error_text(exc))

    signal_process = staticmethod(signal_process)
    service_action = staticmethod(service_action)
