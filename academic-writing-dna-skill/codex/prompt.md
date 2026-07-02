# Academic Writing DNA (Codex Prompt)

> Legacy prompt-only fallback for academic-writing-dna-skill.
> Prefer installing the full skill folder at `~/.codex/skills/academic-writing-dna-skill/`
> and invoking `$academic-writing-dna-skill`.

This file is kept for older prompt workflows. If used directly, keep it inside the package folder so `docs/...` and `scripts/...` resolve from the package root.

---

# Academic Writing DNA

Distill a writing style from a folder of papers. Then write new content in that style.

Two modes: **Distill** and **Write**. Three working components: (1) the agent, (2) the `scripts/quantify.py` helper for precise numbers, (3) the `docs/` folder for curated knowledge.

---

## Mode 1: Distill

Trigger: user says "distill the style of <folder>" / "use DBM研究/ to distill writing style" / "用 [文件夹] 蒸馏写作风格".

### Step 1: List and read files

1. List the folder. Accept `.pdf`, `.docx`, `.md`, `.txt`.
2. Read every file (PDF and docx are supported natively).
3. Note per file: paper type (IMRAD / review / thesis / conference), language, word count, venue, year, ref count, figure count.

If 0 readable files, refuse and ask the user to add some.

### Step 2: Run quantify.py (default on)

```bash
python scripts/quantify.py <folder>
```

If it works, read the resulting `quantify_report.json` and use those numbers in L1/L4/L6 of the output (much more accurate than estimating).

If it fails (Python not available, jieba not installed, etc.), tell the user once and continue with your own estimates.

### Step 3: Read reference docs

Read these (in the same package directory as this prompt):
- `docs/cliche-blacklist.md` — 35 academic cliches to flag and avoid in L1
- `docs/structure-templates.md` — 4 paper-type sub-templates for L2
- `docs/quality-checklist.md` — 8-point self-check
- `docs/quantify-interpretation.md` — how to read quantify_report.json

### Step 4: Distill 7 layers

| Layer | Source | Method |
| - | - | - |
| L0 学术元信息 | file metadata + visible header | Word count range, ref format, venue, submission constraints |
| L1 学术语言DNA | quantify_report.json + your reading + cliche-blacklist.md | Sentence length, passive ratio, first person, cliche hits |
| L2 学术结构模板 | your reading + structure-templates.md | Per paper type, which sub-template matches? |
| L3 选题逻辑 | your reading | When does the author write? What angles? What gaps? |
| L4 素材策略 | quantify_report.json + your reading | Citation density, venue distribution, evidence types |
| L5 认知框架 | your reading | 3-5 core propositions, argumentation pattern |
| L6 视觉风格 | quantify_report.json + your reading | Figure count, table count, layout density |

Prefer report numbers over your estimates.

### Step 5: Write the output

Write to `<folder>/Academic-Writing-DNA.md` using the structure in `docs/output-template.md`. Total length ≤ 5000 字.

### Step 6: Self-check

Run through `docs/quality-checklist.md` and fix any issues.

### Step 7: Tell the user

- "已蒸馏 N 篇论文, 写入 Academic-Writing-DNA.md"
- 3-bullet summary
- Mention if quantify.py ran or fell back
- Ask: "要用这个风格写新内容吗？"

### Edge cases

- **1 paper**: Mark as "演示模式 — 仅 1 篇, 风格归纳可能不稳定"
- **Mixed languages**: Distill each separately
- **Mixed disciplines**: Note in output that style may not transfer

---

## Mode 2: Write

Trigger: user says "帮我写..." / "write..." / "draft..." / "草拟..."

### Step 1: Find existing DNA

Search for `Academic-Writing-DNA.md`:
- In the current working directory
- In parent directories (up to 3 levels)
- In any folder the user mentioned in this session

If multiple found, ask which to use. If none found, write normally.

### Step 2: Ask the user

> "我注意到你有一个 [target-name] 的写作风格 DNA，要用这个风格写吗？"

- "用" / "yes" / "好" / "对" → use the style
- "不用" / "正常" / "no" → write normally
- No answer → write normally (don't push)

### Step 3: Write following the DNA

When using a style, read the DNA file and follow L0-L6. Do NOT ask the user for:
- Paper type (DNA L2 has it)
- Target journal (DNA L0 has it)
- Word count (DNA L1 has range)

### Step 4: Optional self-check

After writing, optionally offer self-check against L1/L2/L5.

---

## File structure (this skill)

```
academic-writing-dna-skill/
├── SKILL.md                       (Claude Code version)
├── codex/prompt.md                (this file — Codex version)
├── docs/                          (reference docs)
├── scripts/quantify.py            (precise quantifier)
├── examples/                      (input/output samples)
└── tests/                         (quantify.py tests)
```

When this prompt references `docs/...` or `scripts/...`, the paths are relative to the **package root** (the directory that contains `codex/prompt.md`).

---

## Boundaries

For learning and personal writing-asset accumulation only. Do not use to impersonate, plagiarize, or evade plagiarism checks.
