# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Plan/Checks)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Use a live control process in the same process group to prove that a signal reaches only the selected PID.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C15 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

### L-002 - Exercise a stale process identity through the UI and assert the resulting refresh, not only the backend rejection.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C16 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

### L-003 - Assert stdout and stderr separately when the CLI contract names an output stream.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C30 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

### L-004 - Start the installed terminal executable in a pseudoterminal with runtime import paths isolated from build tooling.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C31 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

### L-005 - Execute a real shell when proving that command execution preserves source history files.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C32 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

### L-006 - Exercise both mouse and keyboard confirmation paths for permission and stale-target failures.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `terminal-tests` · harmful: 0
- features: wslazy
- evidence: verification.md round 1 C35 (terminal-tests)
- last seen: 2026-10-05T04:58:37Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
