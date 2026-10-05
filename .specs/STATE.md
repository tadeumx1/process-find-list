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
**Where**: completed; English UI, code, README, CONTRIBUTING.MD, docs/running.md and GitHub description verified. Public visibility confirmed. Independent PASS for C1–C7 and all 44 tests at c1f3daf1c7c92e3050633bfe397fe886e6db0eb5. Completion gate passed.
**Next step**: user operation; no implementation work remains. The final report commit is included in the authorized push to origin/main.
**Blockers**: none.

Run `python3 -m wslazy` or `.venv/bin/wslazy`; the local installed package has been refreshed with English content. Host test command: `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`. Packaging tools are isolated under /tmp. The original WSLazy report remains tied to its verified commit; its Portuguese text is historical.

Automated validation uses simulated service operations, real disposable processes and shells, and real pseudoterminal tests with a temporary lazydocker executable. Human usability review has not been performed.
