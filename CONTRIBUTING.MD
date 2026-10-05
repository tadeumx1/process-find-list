# Contributing to WSLazy

Thanks for helping improve WSLazy. Keep changes focused on inspecting and managing local Linux/WSL resources from the terminal.

This project was built using **Codex** and the **`tlc-spec-lean` skill**. Contributions can be written with or without an AI assistant; the same review and validation expectations apply.

## Development setup

Use Linux or WSL with Python 3.10+ and curses. See the [running guide](docs/running.md) for system packages and optional tools.

```bash
git clone https://github.com/tadeumx1/process-find-list.git
cd process-find-list
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install setuptools wheel
python -m wslazy
```

For an external contribution, fork the repository on GitHub and clone your fork instead. Create a branch for your change:

```bash
git switch -c fix/short-description
```

## Project layout

- `wslazy/core.py`: Linux collectors, history parsing, process signals, service actions, and display data.
- `wslazy/ui.py`: curses rendering, keyboard/mouse input, confirmation dialogs, and external terminal handoff.
- `wslazy/__main__.py`: CLI entry point and startup validation.
- `tests/`: acceptance and regression tests, including pseudoterminal and installation fixtures.
- `docs/`: user-facing documentation.
- `.specs/`: plans, executable checks, decisions, and independent verification records.

## Language and style

Write code identifiers, comments, docstrings, application-authored UI messages, tests, and user documentation in **English**. Preserve original user-controlled commands, resource names, paths, and external output.

Use the existing Python style and standard library where practical. Keep the application free of third-party runtime dependencies unless a requirement justifies a reviewed architectural change. Keep curses calls on the UI thread and slow collectors off it.

## Requirements and verification

The project follows the `tlc-spec-lean` workflow:

1. Capture the intended behavior and relevant design decisions in a plan for review.
2. Derive checks with concrete expected outcomes and executable proofs before implementation.
3. Implement the change, run its proofs, and commit coherent changes.
4. Have someone other than the author verify the complete change and record the result.

For work using the skill, follow its instructions and validators. Plans and reports live in `.specs/features/<feature>/`. The current profile is `light`; do not describe it as mutation testing or a completed human usability review.

Do not remove, skip, or weaken tests to make a change pass. If an approved requirement changes, record the new decision and update the affected expectations explicitly. Keep historical reports tied to their original commits.

## Testing

From the activated development environment:

```bash
python -m unittest discover -v
git diff --check
```

Run a focused test while iterating, then the full suite for changes affecting shared UI or collector behavior:

```bash
python -m unittest tests.test_acceptance.Acceptance.test_ac15 -v
```

The installation fixture requires pip, setuptools, and wheel. It creates a temporary environment, builds and installs local code, and launches the installed CLI in a pseudoterminal. Bash and Zsh must be available for the real-shell history checks. Test-controlled `sleep` processes are created and cleaned up; service actions are simulated.

Use disposable processes, temporary history files, and local test servers. Do not target unrelated processes, production services, or your real command history in automated tests. Preserve confirmation, PID identity, permission handling, and terminal restoration behavior.

For UI changes, manually check all five views at 80×24 and a larger size. Exercise both keyboard and mouse, cancellation, resizing, and return from an external command. Report what you tested and any unavailable environment dependencies.

## Pull requests

Use a short Conventional Commit message such as `fix(ui): preserve selection after refresh`. In the pull request:

- Describe the problem and resulting behavior.
- Link the relevant plan/checks or issue when available.
- Include the validation commands and results.
- Update the README or running guide if installation or interaction changes.
- Note limitations and any system-dependent behavior you could not exercise.

Do not include `.venv/`, build output, credentials, or personal history files. Those local artifacts are not project source.

## Reporting issues

Include the WSL distribution, Python version, terminal application, steps to reproduce, and the relevant error text. Redact sensitive commands, paths, and process arguments before sharing terminal output.
