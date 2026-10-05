# English content checks

Profile: light
Plan: `.specs/features/english-content/plan.md`

## Checks

**C1** - All five view names, dialog controls, help and CLI use English text (AC 1).
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac01 tests.test_acceptance.Acceptance.test_ac10 tests.test_acceptance.Acceptance.test_ac11 tests.test_acceptance.Acceptance.test_ac13 tests.test_acceptance.Acceptance.test_ac24 tests.test_acceptance.Acceptance.test_ac30 tests.test_acceptance.Acceptance.test_ac33 tests.test_acceptance.Acceptance.test_ac35 tests.test_acceptance.Acceptance.test_ac36 tests.test_acceptance.Acceptance.test_ac39 -v`

**C2** - Service scopes/actions and backend failure messages use English; code and fixture prose are reviewed in English (AC 2).
Proof: `python3 -m unittest tests.test_acceptance.Acceptance.test_ac06 tests.test_acceptance.Acceptance.test_ac07 tests.test_acceptance.Acceptance.test_ac08 tests.test_acceptance.Acceptance.test_ac16 tests.test_acceptance.Acceptance.test_ac17 tests.test_acceptance.Acceptance.test_ac19 tests.test_acceptance.Acceptance.test_ac20 tests.test_acceptance.Acceptance.test_ac26 -v`

**C3** - The README has English installation, controls, history and development sections, and the package description is English (AC 3).
Proof: `python3 -c 'from pathlib import Path; r=Path("README.md").read_text(); assert all(h in r for h in ("## Getting started", "## Controls", "## Command history", "## Development and validation")); assert "processes, applications, ports, services" in Path("pyproject.toml").read_text()'`

**C4** - Existing behavioral proofs retain their assertions and pass with translated copy (AC 4).
Proof: `python3 -m unittest tests.test_acceptance tests.test_regressions -v`

**C5** - GitHub repository description is exactly `Terminal manager for WSL processes, ports, services, and command history, with keyboard and mouse controls and lazydocker access.` (AC 5).
Proof: `python3 -c 'import json,subprocess; r=json.loads(subprocess.check_output(["gh","repo","view","tadeumx1/process-find-list","--json","description"])); assert r["description"] == "Terminal manager for WSL processes, ports, services, and command history, with keyboard and mouse controls and lazydocker access."'`

**C6** - English contribution and run documentation exist, are linked, and credit Codex and tlc-spec-lean (AC 6).
Proof: `python3 -c 'from pathlib import Path; r=Path("README.md").read_text(); c=Path("CONTRIBUTING.MD").read_text(); d=Path("docs/running.md").read_text(); assert all(x in r for x in ("CONTRIBUTING.MD", "docs/running.md", "Codex", "tlc-spec-lean")); assert all(x in c for x in ("## Development setup", "## Testing", "## Pull requests", "Codex", "tlc-spec-lean")); assert all(x in d for x in ("## Requirements", "## Run from source", "## Install the command", "## Troubleshooting", "python3 -m wslazy"))'`

**C7** - Repository visibility is public (AC 7).
Proof: `python3 -c 'import json,subprocess; r=json.loads(subprocess.check_output(["gh","repo","view","tadeumx1/process-find-list","--json","isPrivate"])); assert r["isPrivate"] is False'`

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| Views (5) | Processes C1 · Applications C1 · Ports C1 · Services C1 · History C1 | - |
| Interface copy (6) | navigation C1 · empty C1 · loading C1 · confirmations C1 · help C1 · errors C2 | - |
| Service scopes (2) | system C2 · user C2 | - |
| Service actions (3) | start C2 · stop C2 · restart C2 | - |
| Project prose (5) | source C2 · README C3 · metadata C3 · CONTRIBUTING.MD C6 · docs/running.md C6 | - |
| GitHub settings (2) | description C5 · public C7 | - |
| Input methods (2) | keyboard C4 · mouse C4 | - |

The verifier also reads the changed source and README for language consistency; marker assertions are not a substitute for that review. No assertion is removed, weakened or skipped. C4 deliberately names the existing two test classes' modules: all 44 named tests must appear and pass, not merely an aggregate runner exit.

## Swept

- validation: C1, C2 — English empty and error states; existing input rules unchanged
- failure modes: C2, C4 — same handling with translated messages
- idempotency: existing - UI confirmation and external_active guards; C4 retains their tests
- authorization: existing - core pidfd identity and permission checks; C4 retains their tests
- concurrency: existing - UI result queue and background collectors; C4 retains their tests
- data lifecycle: existing - history remains read-only; C4 retains real-shell preservation tests
- dependency failure: C2 — missing tools and shell errors translated
- state transitions: C2, C4 — same service actions and keyboard/mouse confirmation paths
- observability: C1, C2 — English status and error feedback

## Handoff

Approximately 80 KB of source, tests and README / 4 = 20k tokens, plus 5k for the amendment and review. Under the default 150k budget: one builder, followed by an independent verifier. Base: `2db2fd88ad24246053903eadc2e9031957991ff9`. Build tooling on this host remains under `/tmp/wslazy-build-tools`; run proofs with that directory in PYTHONPATH when building the installation fixture.

Status: implemented; 44 tests passed and C3/C5/C6/C7 assertion commands passed. Independent verification pending.
