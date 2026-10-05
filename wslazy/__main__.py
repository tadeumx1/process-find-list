"""Public CLI; --help and --version work without an interactive terminal."""
import argparse
import locale
import os
import sys
from . import __version__


def main():
    parser = argparse.ArgumentParser(prog='wslazy', description='Manage WSL processes, ports, services, and commands in one terminal.')
    parser.add_argument('--version', action='version', version=f'WSLazy {__version__}')
    parser.parse_args()
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Interactive terminal required', file=sys.stderr)
        return 1
    if not sys.platform.startswith('linux') or not os.path.isdir('/proc'):
        print('WSLazy requires Linux with /proc (including WSL).', file=sys.stderr)
        return 1
    if os.environ.get('TERM','dumb') == 'dumb':
        print('Terminal does not support curses; configure TERM in your terminal.', file=sys.stderr)
        return 1
    import curses
    from .ui import App
    try:
        locale.setlocale(locale.LC_ALL, '')
        curses.wrapper(lambda screen: App(screen).start())
    except KeyboardInterrupt:
        return 0
    except (curses.error, OSError) as exc:
        print(f'Could not initialize the terminal: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
