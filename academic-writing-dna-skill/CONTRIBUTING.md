# Contributing to academic-writing-dna-skill

Thanks for your interest in improving this skill! Contributions of all kinds are welcome.

## How to contribute

### Report bugs or request features

Open an [issue](../../issues) with:
- A clear title
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Your environment (OS, Python version, CLI version)

### Submit code changes

1. **Fork** the repository
2. **Create a branch** for your change: `git checkout -b fix/your-change`
3. **Make your changes** following the conventions below
4. **Add or update tests** — all changes should keep tests passing
5. **Run the test suite**: `python -m pytest tests/ -v`
6. **Commit** with a clear message: `git commit -m "fix: short description"`
7. **Push** to your fork: `git push origin fix/your-change`
8. **Open a Pull Request** describing what changed and why

### Improve documentation

Docs are in `SKILL.md`, `references/zh-workflow.md`, `README.md`, `DELIVERY.md`, and `docs/`. Fixes to typos, unclear wording, or missing examples are very welcome.

### Add to the cliche blacklist

The blacklist at `docs/cliche-blacklist.md` covers 35 common academic cliches. If you find one that's missing, open a PR adding it (both English and Chinese versions).

## Conventions

### Code style

- Python 3.10+ syntax
- Type hints on public functions
- Module-level regex compilation (compiled once, reused)
- Docstrings on public functions
- `from scripts.lib.text_utils import ...` for shared utilities

### Tests

- All new code must have corresponding tests in `tests/`
- Tests use `pytest`, not unittest
- One test = one behavior
- Use `tmp_path` fixture for filesystem tests
- Tests must pass before PR is mergeable

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: ...` for new features
- `fix: ...` for bug fixes
- `docs: ...` for documentation only
- `refactor: ...` for code changes that don't fix bugs or add features
- `test: ...` for test-only changes
- `chore: ...` for maintenance

## Architecture notes

- `SKILL.md` (and Chinese version) — main workflow, read by the AI
- `docs/` — curated knowledge (cliches, structure templates, etc.)
- `scripts/quantify.py` — optional precise quantifier
- `examples/` — input/output samples
- `tests/` — pytest tests for the quantifier

When adding new features, prefer extending existing files over creating new top-level ones. The skill is intentionally compact.

## Code of conduct

Be respectful and constructive. This is a small, friendly project.
