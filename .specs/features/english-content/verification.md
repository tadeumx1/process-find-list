# English content verification

**Verdict**: PASS
**Profile**: light
**Diff range**: 2db2fd88ad24246053903eadc2e9031957991ff9..c1f3daf1c7c92e3050633bfe397fe886e6db0eb5
**Round**: 1 - full
**Verifier**: independent sub-agent (author != verifier)
**Verified at**: c1f3daf1c7c92e3050633bfe397fe886e6db0eb5, 2026-10-05

## Checks

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| C1 | Five views, dialogs, help, and CLI use English | Batched unittest discovery below; every C1 test passed; manual reading of changed UI and CLI text | `tests/test_acceptance.py:80` — `self.assertEqual(VIEWS, ('Processes','Applications','Ports','Services','History'))`; `tests/test_acceptance.py:167` — `self.assertIn('No results',self.screen.text())`. Manual review includes `wslazy/ui.py:17` view/header/help copy, `wslazy/ui.py:277` rendering, `wslazy/ui.py:517` action dialogs, and `wslazy/__main__.py:10` CLI copy. | PASS |
| C2 | English service scopes/actions, backend messages, source and fixtures | Batched unittest discovery; every C2 test passed; source/comment/docstring review | `tests/test_acceptance.py:137` — `self.assertEqual([(s.scope,s.name,s.state,s.description) for s in services], [('system','db.service','active/running','Database'),('system','idle.service','inactive/dead','Idle'),('user','db.service','active/running','Database'),('user','idle.service','inactive/dead','Idle')])`; `tests/test_acceptance.py:269` — `self.assertIn(verb,argv)` with local literal cases `('start','start'),('stop','stop'),('restart','restart')` at line 265. `tests/test_acceptance.py:237` asserts `Permission denied`. | PASS |
| C3 | English README installation, controls, history, development, and package description | Executed the C3 assertions in a batched Python invocation; exit 0, `C3 PASS`; manually read README and metadata | `.specs/features/english-content/checks.md:15` — `assert all(h in r for h in ("## Getting started", "## Controls", "## Command history", "## Development and validation"))` and `assert "processes, applications, ports, services" in Path("pyproject.toml").read_text()`. Content at `README.md:21`, `README.md:57`, `README.md:80`, `README.md:90`, `pyproject.toml:8`. | PASS |
| C4 | All 44 behavioral tests remain and pass with translated expectations | `PYTHONPATH=/tmp/wslazy-build-tools python3 -m unittest discover -v`; exit 0; 44 passed in 6.645s; complete feature diff inspected | `tests/test_acceptance.py:395` — `self.assertTrue(result['interactive']['restored'])`; `tests/test_regressions.py:92` — `self.assertEqual(termios.tcgetattr(slave),before)`. PID safety remains asserted at `tests/test_acceptance.py:217`; mouse confirmation at `tests/test_acceptance.py:455` asserts `[('signal',123,signal.SIGTERM)]`. No assertion, test, or skip policy was removed or weakened. | PASS |
| C5 | Exact requested English GitHub description | Read-only `gh repo view tadeumx1/process-find-list --json description` through C5 assertion; exit 0, `C5 PASS` | `.specs/features/english-content/checks.md:21` — `assert r["description"] == "Terminal manager for WSL processes, ports, services, and command history, with keyboard and mouse controls and lazydocker access."`; live result matched exactly. | PASS |
| C6 | English contribution/run guides, README links, Codex and skill credit | Executed C6 assertions; exit 0, `C6 PASS`; manually read both guides and their links | `.specs/features/english-content/checks.md:24` — `assert all(x in r for x in ("CONTRIBUTING.MD", "docs/running.md", "Codex", "tlc-spec-lean"))`; the same located proof asserts all required contribution and run-guide headings. Real relative links at `README.md:41`, `README.md:101`; credits at `README.md:105`, `CONTRIBUTING.MD:5`, `docs/running.md:160`. | PASS |
| C7 | GitHub repository is public | Read-only `gh repo view tadeumx1/process-find-list --json isPrivate` through C7 assertion; exit 0, `C7 PASS: {'isPrivate': False}` | `.specs/features/english-content/checks.md:27` — `assert r["isPrivate"] is False`; independently observed live result was false. | PASS |

## Proof execution

The checkout was clean and HEAD matched the stated endpoint before verification. One unittest process covered C1, C2, and C4, rather than rerunning each check separately. Each of the following test names appeared individually with `ok`:

```text
tests.test_acceptance.Acceptance.test_ac01
tests.test_acceptance.Acceptance.test_ac02
tests.test_acceptance.Acceptance.test_ac03
tests.test_acceptance.Acceptance.test_ac04
tests.test_acceptance.Acceptance.test_ac05
tests.test_acceptance.Acceptance.test_ac06
tests.test_acceptance.Acceptance.test_ac07
tests.test_acceptance.Acceptance.test_ac08
tests.test_acceptance.Acceptance.test_ac09
tests.test_acceptance.Acceptance.test_ac10
tests.test_acceptance.Acceptance.test_ac11
tests.test_acceptance.Acceptance.test_ac12
tests.test_acceptance.Acceptance.test_ac13
tests.test_acceptance.Acceptance.test_ac14
tests.test_acceptance.Acceptance.test_ac15
tests.test_acceptance.Acceptance.test_ac16
tests.test_acceptance.Acceptance.test_ac17
tests.test_acceptance.Acceptance.test_ac18
tests.test_acceptance.Acceptance.test_ac19
tests.test_acceptance.Acceptance.test_ac20
tests.test_acceptance.Acceptance.test_ac21
tests.test_acceptance.Acceptance.test_ac22
tests.test_acceptance.Acceptance.test_ac23
tests.test_acceptance.Acceptance.test_ac24
tests.test_acceptance.Acceptance.test_ac25
tests.test_acceptance.Acceptance.test_ac26
tests.test_acceptance.Acceptance.test_ac27
tests.test_acceptance.Acceptance.test_ac28
tests.test_acceptance.Acceptance.test_ac29
tests.test_acceptance.Acceptance.test_ac30
tests.test_acceptance.Acceptance.test_ac31
tests.test_acceptance.Acceptance.test_ac32
tests.test_acceptance.Acceptance.test_ac33
tests.test_acceptance.Acceptance.test_ac34
tests.test_acceptance.Acceptance.test_ac35
tests.test_acceptance.Acceptance.test_ac36
tests.test_acceptance.Acceptance.test_ac37
tests.test_acceptance.Acceptance.test_ac38
tests.test_acceptance.Acceptance.test_ac39
tests.test_acceptance.Acceptance.test_ac40
tests.test_regressions.Regressions.test_bash_escaped_continuation
tests.test_regressions.Regressions.test_click_does_not_confirm_twice
tests.test_regressions.Regressions.test_slow_collector_keeps_ui_responsive
tests.test_regressions.Regressions.test_terminals_suspend_and_resume_mouse
```

Named C1/C2 tests were located with `rg -n -A 22` over their test definitions; regression tests with `rg -n -A 40 '^    def test_' tests/test_regressions.py`. These searches exposed the relevant assertions beside their literal expected values. The feature changes the English expectations in both test modules. Unchanged tests such as confirmation contents and history review are supplementary behavioral preservation proofs, not the sole evidence of translated copy.

C3, C5, C6, and C7 used the assertions and `gh repo view` arguments recorded in checks.md, batched into one `python3` heredoc. All four emitted PASS; both GitHub queries were read-only. These are observations of the live repository on the verification date, not assertions inferred from local configuration.

`git diff --check 2db2fd88ad24246053903eadc2e9031957991ff9..c1f3daf1c7c92e3050633bfe397fe886e6db0eb5` exited 0 without output.

## Manual review and proof level

Read the complete application/source changes, test changes, README, CONTRIBUTING.MD, docs/running.md, and package description. Application-authored labels, help, confirmation text, status messages, errors, and CLI output are English. Identifiers, comments, docstrings, and fixture prose are English. An additional `rg -n -i` search for Portuguese terms across `wslazy`, `tests`, README, CONTRIBUTING.MD, docs, metadata, and setup.py returned no matches. Tokenized comments and docstrings were also read. Historical Portuguese specification reports remain intentionally outside this language revision.

The two service scopes and three service action values were translated consistently through collection, UI keyboard mappings, buttons, confirmation handling, backend execution, and test fixtures. External systemctl verbs and `--user` selection preserve their previous meaning. The Details mouse-region rename is matched by its event lookup. No changed control flow, subprocess arguments other than translated internal values, process identity guard, timeout, or terminal handoff behavior was found. Test changes preserve the assertions and behavioral cases; translated expectation literals follow the explicit revised language requirement.

Documentation accurately describes source/installed execution, prerequisites, existing shortcuts, current-directory command execution, source history preservation, systemd scope, optional lazydocker, and permission/PID constraints. README links resolve to the new local documents. Codex and tlc-spec-lean attribution appears in all three user documents.

Proof level is appropriate for this language-only revision: render/input tests cover UI labels and actions; subprocess CLI and installation tests cross the public entry-point boundary; pseudoterminal tests cover terminal restoration; GitHub settings are read from the actual remote. Marker assertions alone cannot establish English consistency, so C1–C3 and C6 also rely on the manual textual review explicitly requested in checks.md. This does not claim exhaustive automated assertions for every sentence.

## Swept existing constraints

| Existing row | Re-read evidence | Assessment |
| --- | --- | --- |
| Idempotency | `wslazy/ui.py:518` blocks actions during dialogs/external tools; `wslazy/ui.py:579` guards confirmation while an action is pending; `tests/test_regressions.py:55` asserts one signal operation after two clicks. | Constraint remains present. |
| Authorization | `wslazy/core.py:290` opens a pidfd; line 292 checks start-time identity; line 294 signals the pinned process; line 299 handles permission denial. `tests/test_acceptance.py:217` and line 237 retain their rejection assertions. | Constraint remains present. |
| Concurrency | `wslazy/ui.py:168` prevents duplicate collectors, line 178 queues results, line 179 starts the worker, and line 184 drains results on the UI path. `tests/test_regressions.py:35` asserts navigation while collection is delayed. | Constraint remains present. |
| Data lifecycle | `wslazy/core.py:221` opens history for reading; `wslazy/core.py:270` consumes its entries without writes. `tests/test_acceptance.py:422` and line 423 assert unchanged Bash/Zsh bytes after actual shell runs. | Constraint remains present. |

## Limitations

- Human usability testing was not performed. Automated render and pseudoterminal tests do not establish human usability or visual quality in every terminal.
- Profile light does not require fault injection, a recomputed coverage join, or Test policy verdicts. No faults were injected; checks.md has no Test policy section. There are no external binding visual artifacts requiring the ui-profile review.
- Service operations use simulated execution in the tests; this verification did not change live systemd services. GitHub public visibility and description were verified live.
- The installation fixture validated a fresh temporary install of this HEAD. The orchestrator separately reports refreshing the workspace's ignored `.venv`; that installation was not independently reviewed here. Committing this report and pushing the remaining commits are final delivery tasks outside C1–C7 and this read-only implementation review.

## Gate

Application proofs: 44 tests passed, 0 failed, 0 skipped. C3/C5/C6/C7 assertion proofs passed. Seven of seven checks have located evidence; no grounded gaps found.

Completion gate: `python3 /home/matheus/.codex/skills/tlc-spec-lean/scripts/validate_verification.py /home/matheus/process-find-list/.specs/features/english-content` — exit 0; `validate_verification: 0 error(s), 0 warning(s) across [english-content]`.
