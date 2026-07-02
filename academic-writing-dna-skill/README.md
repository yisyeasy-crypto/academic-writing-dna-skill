# academic-writing-dna-skill

> Distill an author's writing style from a folder of papers, then write new content in that style.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](tests/)

A Claude Code/Codex-compatible skill that learns an academic author's writing style from a folder of papers and lets you write new content in that style.

**Supported CLIs**:
- **Claude Code** — install to `~/.claude/skills/`, invoke as `/academic-writing-dna-skill`
- **Codex** — install the full folder to `~/.codex/skills/academic-writing-dna-skill/`, invoke as `$academic-writing-dna-skill`

## What it does

1. **Distill** — Drop 1-10 papers (PDF, docx, md, or txt) into a folder. The skill reads them, runs an optional quantifier for precise numbers across all four formats, and generates an `Academic-Writing-DNA.md` describing the author's style.
2. **Write** — When you ask the skill to write something, it offers to use the distilled style. You say "yes" and it writes in that style — no need to specify paper type, journal, or word count (the DNA file already knows).

## Quick start

**Distill**:
```
把 DBM研究/ 这个文件夹的论文蒸馏成写作风格
```

**Write**:
```
帮我写一段关于 X 的内容
```
The skill asks: "要用 [已蒸馏的] 风格吗？" — answer "用" and it writes in that style.

## Install

### Claude Code
```bash
ln -s /path/to/academic-writing-dna-skill ~/.claude/skills/
```

### Codex
```bash
mkdir -p ~/.codex/skills
cp -R /path/to/academic-writing-dna-skill ~/.codex/skills/academic-writing-dna-skill
```

Verify by starting Codex and asking it to use `$academic-writing-dna-skill`.

### Optional: precise numbers
```bash
pip install -r requirements.txt   # jieba + pypdf + pytest
```
The skill runs `scripts/quantify.py` automatically when Python is available.

## What's in the package

```
academic-writing-dna-skill/
├── SKILL.md                       Main skill entry
├── agents/openai.yaml             Codex UI metadata
├── references/zh-workflow.md      Chinese reference workflow
├── codex/prompt.md                Legacy prompt-only fallback
├── docs/                          Curated knowledge
│   ├── cliche-blacklist.md        35 academic cliches to avoid
│   ├── structure-templates.md     4 paper-type sub-templates
│   ├── output-template.md         Standard structure for the DNA file
│   ├── quality-checklist.md       8-point self-check
│   └── quantify-interpretation.md How to read quantify_report.json
├── scripts/quantify.py            Optional precise quantifier for md/txt/pdf/docx
├── examples/                      Input/output samples
├── tests/                         pytest tests (25 tests)
├── README.md                      This file
├── DELIVERY.md                    Detailed usage and delivery guide
├── CHANGELOG.md                   Version history
├── CONTRIBUTING.md                How to contribute
├── LICENSE                        MIT
└── requirements.txt               jieba, pytest (optional)
```

The skill is intentionally compact: 5 categories (workflow, knowledge, tools, samples, docs) and ~15 files.

## Use cases

- Match a target journal's style when submitting a paper
- Learn a senior coauthor's voice before collaborating
- Distill your own past papers into a personal style template
- Train a new lab member on the lab's writing conventions

## Requirements

- Python 3.10+ (only for the optional quantifier)
- Claude Code or Codex

## Documentation

- [DELIVERY.md](DELIVERY.md) — detailed usage and delivery guide
- [CHANGELOG.md](CHANGELOG.md) — version history
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [docs/](docs/) — curated knowledge referenced by the skill

## License

MIT — see [LICENSE](LICENSE).
