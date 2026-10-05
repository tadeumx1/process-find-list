# Running WSLazy

WSLazy is a local terminal application for exploring processes, applications, ports, systemd services, and saved Bash/Zsh command history. Its interface supports keyboard and mouse.

## Requirements

- Linux, including WSL, with `/proc` mounted.
- Python 3.10 or newer with the standard-library `curses` module.
- An interactive terminal at least **80 columns × 24 rows**. Mouse support depends on the terminal forwarding mouse events; keyboard navigation remains available without it.
- `ss` from `iproute2` for the Ports view.
- `systemctl` and a running systemd instance for the corresponding system or user Services scope.
- Bash and/or Zsh to execute commands from that shell's history.
- Optional: `lazydocker` on `PATH` and a working Docker environment for its features.

WSLazy has no third-party Python runtime dependencies. Missing optional sources are reported in the affected view; you can still use other views.

On Ubuntu/WSL, the packages used for installation and ports can be installed with:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip iproute2
```

For development tests that exercise both shells, also install Zsh if it is missing:

```bash
sudo apt install zsh
```

## Run from source

Open a terminal inside the WSL distribution you want to inspect:

```bash
git clone https://github.com/tadeumx1/process-find-list.git
cd process-find-list
python3 -m wslazy
```

This mode does not require pip or a virtual environment. Keep the repository as your current directory so Python can find the package.

## Install the command

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
wslazy
```

In a new terminal, activate the environment again or use its executable directly:

```bash
/path/to/process-find-list/.venv/bin/wslazy
```

Replace `/path/to/process-find-list` with your actual checkout path. To make `wslazy` available without activation, add that environment's `bin` directory to your shell's `PATH`.

Run WSLazy from the directory you intend to use for commands: the History review shows that current working directory before executing anything.

## First run

1. Start WSLazy and open **Processes**. Wait for a second sample to see CPU usage; the first sample displays `—`.
2. Press `/` or click **Search**, type a process name or PID, and press Enter to finish editing the filter.
3. Switch with `Tab`, `Shift+Tab`, `1`–`5`, or a click on a view tab.
4. Select an item with `j`/`k`, the arrow keys, or a click. Scroll the list or details with the mouse wheel.
5. Press `?` or click **Help** for the complete shortcut list. Press `q` or click **Quit** to exit.

To see a local server in the application, run this in a separate WSL terminal:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open **Ports** and search for `8000`. The server also appears in **Processes** and in its Python group under **Applications**. This applies to servers launched manually or by tools such as Codex within the same distribution and relevant namespaces. Applications group by executable name and UID rather than project name. The Services view is specifically for systemd units.

Stop the example server with Ctrl+C in its terminal, or select its PID in WSLazy and use **Terminate**. Confirm only after checking the PID and command shown in the dialog.

## Process and service actions

- `x` or **Terminate** sends `SIGTERM` after confirmation.
- `K` or **Kill** sends `SIGKILL` after confirmation.
- If an application or port has multiple PIDs, choose one first.
- In **Services**, `s`, `t`, and `r` request start, stop, and restart for the selected unit and scope.
- A confirmation initially focuses Cancel. Use Tab and Enter to confirm, or click **Confirm**. Esc cancels.

WSLazy uses your Linux permissions and does not automatically elevate privileges. Process identity is checked with PID/start time and pidfd before signaling. A service action has a ten-second wait limit; a timeout does not prove the requested operation was rolled back. Check the refreshed service state before retrying.

## Command history

The application reads `$HISTFILE` when exported, plus `~/.bash_history` and `~/.zsh_history`, deduplicating repeated paths. It considers up to 2,000 recent entries from each source and shows the most recent occurrence of repeated commands within that source.

If a recent command is missing, save the current shell's pending history before starting WSLazy:

```bash
# Bash
history -a
```

```zsh
# Zsh
fc -AI
```

For a custom history location, export the path in your shell before launching the application:

```bash
export HISTFILE="$HOME/.bash_history"
python3 -m wslazy
```

Choose a History item and press Enter or click **Run**. The review shows its command, shell, and current directory. Edit before confirming; `Ctrl+N` inserts a newline, `Ctrl+U` clears the editor, and Esc cancels. Commands use `bash -c` or `zsh -c`; the original session's aliases, functions, variables, and directory are not reconstructed.

After the command exits, its exit code is shown. Press Enter to return to WSLazy. The application does not rewrite the source history files; the command itself retains its usual effects.

## Open lazydocker

Install lazydocker separately using the [official project instructions](https://github.com/jesseduffield/lazydocker). Check that the executable is available:

```bash
command -v lazydocker
```

Press `D` or click **Lazydocker**. WSLazy yields the same terminal to the external tool and restores its view, selection, and filter when lazydocker exits. Lazydocker controls its own interface while it is open. WSLazy does not install it or start Docker automatically.

## Update an installed checkout

```bash
git pull --ff-only
source .venv/bin/activate
python -m pip install --upgrade .
wslazy
```

If running directly from source, pulling the changes is enough; restart `python3 -m wslazy`.

## Troubleshooting

| Message or symptom | What to check |
| --- | --- |
| `Interactive terminal required` | Run from a real terminal, not redirected input/output or a noninteractive job. |
| Missing pip or virtual environment support | Install your distribution's `python3-venv` and `python3-pip` packages, or run directly from source. |
| Terminal does not support curses | Use a terminal with a valid `TERM`; avoid a `dumb` terminal or launching through a noninteractive output panel. |
| Window-size message | Resize to at least 80×24; the interface redraws when space is available. |
| Mouse clicks do nothing | Check that the terminal or terminal multiplexer forwards mouse events. All actions have keyboard controls. |
| `ss: not found` | Install `iproute2`. |
| `owner unavailable` | Socket ownership was not returned by `ss`, often due to permissions; the port remains listed. |
| systemd source unavailable | Check `systemctl list-units --type=service` and `systemctl --user list-units --type=service` for the affected scope. WSL setups without systemd can still use the other views. |
| `Permission denied` | Your user is not permitted to signal that process or control that unit. WSLazy does not bypass that restriction. |
| `Process is no longer available` | The selected process exited or its PID was reused; select the current item after refresh. |
| pidfd support required | The kernel or Python lacks safe process-signaling support; listing still works. |
| `Lazydocker not found in PATH` | Install lazydocker separately and ensure its executable directory is in `PATH`. |
| Missing recent history | Save pending shell history and export a custom `HISTFILE` if you use one. |
| Port or process is missing | Check the WSL distribution and Linux namespaces; Windows processes, other distributions, and isolated container networks are not all visible from the current namespace. |

## Development notes

This project was built using Codex and the `tlc-spec-lean` skill. See [CONTRIBUTING.MD](../CONTRIBUTING.MD) for development setup, test prerequisites, and the verification workflow.
