# English interface and project content

## Problem

WSLazy displays Portuguese interface text and documents installation in Portuguese. The user now requires the entire interface, source code and README to be in English.

This is a user-authorized language revision to the already approved WSLazy feature. The latest explicit request supersedes the original Portuguese copy requirements; it does not change operations or shortcuts.

## Flow

Reuse the existing CLI, collectors, curses interface and acceptance suite.

1. `wslazy.__main__` (exists) displays English CLI help and startup errors.
2. `wslazy.core` (exists) collects the same resources, using English labels, service scopes and action names.
3. `wslazy.ui` (exists) displays English tabs, details, dialogs, help and feedback, with existing keyboard and mouse controls.
4. The README, CONTRIBUTING.MD, docs/running.md and package metadata describe installation, use and contribution in English.
5. The existing GitHub repository receives the requested English description and public visibility; local changes are committed and pushed as authorized.

## Impact

| Front | What changes |
| --- | --- |
| interface | Processes, Applications, Ports, Services, History; all application-authored messages become English. |
| domain | Service scopes become `system` and `user`; internal service actions become `start`, `stop`, `restart`. |
| stored data | None; original command text, resource names and history files are preserved. |
| tests | Update language-specific expectations to the newly requested English values; retain behavioral assertions. |

## Relations

None - no stored-data shape changes.

## Surface

None - no new CLI flags, exit codes or external API signatures.

## Landing

None - replacing labels and internal action names requires no dependency, data migration or architectural change.

## Criteria

**Acceptance Criteria**

1. The system SHALL display English application-authored text in all five views, dialogs, help, status messages and CLI output.
2. The source code SHALL use English comments, docstrings, identifiers and internal service values `system`, `user`, `start`, `stop`, `restart`.
3. The README and package description SHALL be in English, retaining installation commands and the keyboard/mouse usage instructions.
4. WHEN the existing acceptance and regression suites run with updated English copy expectations THEN the system SHALL preserve all 44 existing test outcomes, including terminal restoration, mouse navigation, process identity checks and installed execution.
5. The GitHub repository SHALL use the description `Terminal manager for WSL processes, ports, services, and command history, with keyboard and mouse controls and lazydocker access.`
6. The project SHALL include English `CONTRIBUTING.MD` contribution instructions and `docs/running.md` execution documentation, linked from the README, with credit to Codex and the `tlc-spec-lean` skill.
7. The GitHub repository SHALL have public visibility as explicitly requested by the user.

## Out of scope

| Excluded | Why |
| --- | --- |
| Translating user commands, usernames, paths or external tool output | These are source data and must retain their original meaning. |
| Locale switching | The user requested English, not multiple interface languages. |
| Rewriting historical verification reports and user quotations | They record what was approved and tested at earlier commits. |

## Assumptions

None - the user explicitly requires English for the interface, code and README. The `tlc-spec-lean` light profile remains in effect.

**Open questions:** none.

## Observable

| Surface | Decision | Landing |
| --- | --- | --- |
| Five views and dialogs | Content, empty/loading/error states, confirmations and help | AC 1 |
| CLI | Help, error text, existing flags and exit codes | AC 1, 4 |
| Code and test fixtures | English names and text | AC 2 |
| README, CONTRIBUTING.MD, docs and metadata | English instructions, credits and product description | AC 3, 6 |
| GitHub repository | Description and visibility | AC 5, 7 |
| Mouse and keyboard | Existing navigation and actions | AC 4 |
| External content | Preserve user-controlled data | Out of scope; no translation of source data |

## Sources

- User: the entire interface, all code and the README must be in English.
- User: perform all of these tasks using `tlc-spec-lean`.
- Original approved WSLazy plan: existing functionality remains required; this explicit language revision supersedes its Portuguese labels.

- User additionally requested that the current Portuguese GitHub repository description be translated to English.

- User additionally requested public visibility, CONTRIBUTING.MD, Codex/skill attribution, documentation under docs/, and commit/push of all changes.
