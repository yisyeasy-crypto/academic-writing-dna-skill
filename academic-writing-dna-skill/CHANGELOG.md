# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-06-30

### Added
- Codex CLI support via `codex/prompt.md` (install at `~/.codex/prompts/academic-writing-dna.md`)
- Customer-facing `使用说明.docx` for end-user delivery
- 3 new tests for Codex integration (25 tests total, all passing)

### Changed
- `SKILL.md` and `学术写作蒸馏器.skill.md` now declare support for both Claude Code and Codex CLI
- `DELIVERY.md` has separate install instructions for both CLIs

## [0.3.0] - 2026-06-30

### Added
- `docs/structure-templates.md` — 4 paper-type sub-templates (IMRAD / review / thesis / conference)
- `docs/quality-checklist.md` — 8-point self-check after distillation
- `docs/quantify-interpretation.md` — how to read `quantify_report.json`
- 7 new tests verifying docs/ contents and SKILL.md references them

### Changed
- `SKILL.md` is no longer a router; it now contains the full 7-step workflow
- `scripts/quantify.py` runs by default in Mode 1 (was opt-in)
- `DELIVERY.md` install instruction: install = copy the **whole folder**, not just `SKILL.md`

## [0.2.1] - 2026-06-30

### Added
- `scripts/quantify.py` — optional helper for precise quantitative stats
  - word count, sentence length, passive ratio, first person ratio
  - citation density, ref count, venue distribution
  - figure/table count, section count
  - cliche hits from `docs/cliche-blacklist.md`
- `tests/test_quantify.py` — 15 pytest tests for the helper

## [0.2.0] - 2026-06-30

### Changed
- Rewrote as a 2-mode skill (Distill + Write) replacing the script-driven v0.1.0
- Removed 5 Python scripts, 43 unit tests, and 7 split template files
- Single output: `Academic-Writing-DNA.md` instead of 8 files
- Simplified install: zero Python dependencies required for the main flow

## [0.1.0] - 2026-06-30

### Added
- Initial implementation
- 5 Python scripts for quantitative analysis (L0/L1/L4/L5/L6)
- 7 split template files + integrated `Academic-Writing-DNA.md` entry
- 43 unit tests
- Style-call template + 8-point quality checklist
- Architecture: 7-layer distillation (L0-L6) + 2 cross-layer axes

[Unreleased]: https://github.com/<user>/academic-writing-dna-skill/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/<user>/academic-writing-dna-skill/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/<user>/academic-writing-dna-skill/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/<user>/academic-writing-dna-skill/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/<user>/academic-writing-dna-skill/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/<user>/academic-writing-dna-skill/releases/tag/v0.1.0
