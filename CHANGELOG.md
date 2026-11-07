# Changelog

All notable changes to Cold Email Coach are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.1.1] - 2026-11-07

### Changed
- `install.py` copies `LICENSE` into the installed skill and includes it in `--check`.

## [1.1.0] - 2026-11-07

### Changed
- Moved the runtime skill to `skills/cold-email-coach/` to match the suite layout.
- Updated the installer to copy from the skill folder and added `--dry-run`.
- Added Claude and Cursor plugin manifests.
- Normalized frontmatter, headings, and description triggers.
- Added a `When Not to Use` section with a handoff table.
- Kept hyphens as the only dash character across the documentation.
- Added a Russian README and a CI workflow.

## [1.0.0] - 2026-11-07

### Added
- Initial release: WRITE, REVIEW, and REWRITE modes for cold outreach email.
- 11-point checklist with PASS/FAIL reasons and a score out of 11.
- References for Josh Braun's problem-first approach and Will Allred's brevity rules.
- Optional `scripts/email_lint.py` heuristic linter.
- Installer for Claude Code, OpenCode, and portable agents.
- 15 test cases with expected behavior.
