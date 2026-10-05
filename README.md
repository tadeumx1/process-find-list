# WSLazy

A terminal manager for WSL processes, applications, ports, services, and command history, inspired by lazydocker. Use **keyboard or mouse** to explore local resources and act on a selected process. The **Lazydocker [D]** button opens lazydocker in the same terminal and returns to WSLazy when it exits.

```text
 WSLazy     your WSL, in one place            Lazydocker [D]  Help [?]

 Processes [1]  Applications [2]  Ports [3]  Services [4]  History [5]

 / Search: python

 PID     USER     CPU      MEMORY     COMMAND   │ Details
 1420    you      12.4%    48.0 MiB    python …  │ PID: 1420
                                              │ Command:
                                              │ python app.py

 Terminate [x]  Kill [K]  Refresh [F5]                     Quit [q]
```

## Getting started

Requires **Linux/WSL and Python 3.10+ with curses**. There are no third-party Python runtime dependencies.

```bash
git clone https://github.com/tadeumx1/process-find-list.git
cd process-find-list
python3 -m wslazy
```

To install the `wslazy` command in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
wslazy
```

On Ubuntu/WSL, install `python3-venv` and `python3-pip` if the virtual environment tools are missing. Running directly with `python3 -m wslazy` does not require pip.

See the [running guide](docs/running.md) for requirements, installation, an example local server, updates, and troubleshooting.

## Views

| View | Contents |
| --- | --- |
| Processes | Readable processes in the current Linux `/proc`, including PID, user, CPU, resident memory, and command. State and start time are in the details. |
| Applications | Processes grouped by executable name and UID, with total usage and individual PIDs. Multiple Node servers appear together under `node`, not necessarily their project names. |
| Ports | Listening TCP and bound UDP sockets, including IPv4/IPv6 and owners when available. |
| Services | Loaded systemd `.service` units in the system and user scopes, including inactive units. |
| History | Recent Bash and Zsh commands, their source files, and an editable review before execution. |

Servers launched by Codex or another tool appear when they run in the same WSL distribution and relevant Linux namespaces. For example, a Node development server can appear in Processes, Applications and Ports; the Services view specifically lists systemd units.

Resource collection repeats two seconds after the previous collection finishes. CPU is shown as `—` for the first sample and can exceed 100% when a process uses multiple cores. Windows processes and other WSL distributions are outside this application's scope. A source failure is shown in its view without blocking navigation.

## Controls

| Action | Keyboard | Mouse |
| --- | --- | --- |
| Switch views | `Tab`, `Shift+Tab`, `1`–`5` | Click a tab |
| Select an item | `↑` / `↓`, `j` / `k`, `PgUp` / `PgDn` | Click a row or scroll over the list |
| Scroll details | `[` / `]` | Scroll over the details |
| Search | `/`, type, `Enter` to finish | Click Search, then type |
| Clear search | `Ctrl+U` in the field or `Esc` outside it | Click the field and use `Ctrl+U` |
| Open full details | `Enter` | Read and scroll the details panel |
| Terminate a process | `x` → `Tab` → `Enter` | Terminate → Confirm |
| Kill a process | `K` → `Tab` → `Enter` | Kill → Confirm |
| Start / stop / restart a service | `s` / `t` / `r` → `Tab` → `Enter` | Action button → Confirm |
| Review a history command | `Enter` in History | Run |
| Open lazydocker | `D` | Lazydocker |
| Refresh now | `F5` | Refresh |
| Help | `?` | Help |
| Quit | `q` | Quit |

A process confirmation shows the **PID, command, and signal**. `Esc` or **Cancel** abandons the action. If an application or port has multiple processes, choose a single PID first. Terminate sends `SIGTERM`; Kill sends `SIGKILL`. WSLazy checks process identity and uses `pidfd` to avoid signaling a different process after PID reuse. It refuses this action on a kernel without that support.

Operations use your current permissions without automatic privilege escalation. An accepted operation or sent signal does not guarantee the resource has already changed state; WSLazy refreshes the list to check. A supervisor may restart a process you terminate.

## Command history

WSLazy reads up to the last 2,000 entries from each available file among `$HISTFILE`, `~/.bash_history`, and `~/.zsh_history`. Repeated paths are read once. Duplicate commands in a source retain their most recent occurrence. Ordering follows each file's position, not a global timeline across shells.

Only history **already written to disk** is available. Before opening WSLazy, use `history -a` in Bash or `fc -AI` in Zsh to save pending entries if needed. Export `HISTFILE` to pass a custom history path to the application. Bash history without timestamps or continuations may not contain enough information to reconstruct every multiline command.

The review shows the complete command, shell, and **current working directory**. Edit with arrow keys, `Home`, `End`, `Backspace`, `Delete`, and `Ctrl+U`; `Ctrl+N` inserts a newline. `Enter` in the editor or **Confirm** executes the reviewed text. `Tab` switches between the editor and buttons; `Esc` cancels.

Commands run through `bash -c` or `zsh -c`. WSLazy does not recreate the original session's directory, variables, aliases, or functions. After execution, the exit code is shown; press Enter to return. WSLazy does not add or rewrite entries in the source history files. Commands you execute retain their normal shell effects.

## Development and validation

```bash
python -m pip install setuptools wheel
python -m unittest discover -v
```

The installation test needs pip, setuptools, and wheel in the development environment. These are build/test tools, not application runtime dependencies. It builds a local wheel, installs from source, and launches the installed command in an isolated virtual environment without network access during installation.

The suite exercises disposable processes, temporary histories, real pseudoterminal input, and a temporary lazydocker substitute. Service actions use a simulated executor instead of changing real services.

Read [CONTRIBUTING.MD](CONTRIBUTING.MD) before proposing a change. The [original plan](.specs/features/wslazy/plan.md) and [English-content revision](.specs/features/english-content/plan.md) record the requirements. Historical reports retain the language used when those versions were reviewed.

## Built with

This project was built using **Codex** and the **`tlc-spec-lean` skill**. The workflow records requirements, derives executable checks, builds the change, and uses an independent verifier. Verification currently uses the `light` profile; automated checks do not replace human usability review.
