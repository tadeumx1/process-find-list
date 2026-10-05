# WSLazy state

## Decisions

| ID | Status | Decision | Reason |
| --- | --- | --- | --- |
| AD-001 | active | Python >=3.10, curses, Linux /proc, wslazy command; no third-party runtime dependencies | Original approved architecture and direct execution in WSL. |
| AD-002 | active | tlc-spec-lean light profile | Independent verification with located evidence, without fault injection. |
| AD-003 | active | English application-authored UI, source code and user documentation | Explicit user language revision supersedes the original Portuguese copy. |
| AD-004 | active | Public GitHub repository with English description | Explicitly authorized by the user in this update. |

## Handoff

**Feature**: english-content
**Where**: English UI, code, README, CONTRIBUTING.MD, docs/running.md and GitHub description implemented. Public visibility confirmed. All 44 tests and documentation/repository assertion commands pass.
**Next step**: independent verification of C1–C7, then commit the report and push all changes as requested.
**Blockers**: none.

Run `python3 -m wslazy`. Host test command: `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`. Packaging tools are isolated under /tmp. The original WSLazy report remains tied to its verified commit; its Portuguese text is historical.

Automated validation uses simulated service operations, real disposable processes and shells, and real pseudoterminal tests with a temporary lazydocker executable. Human usability review has not been performed.
