---
name: academic-writing-dna-skill
description: Distill academic writing style from a folder of papers (PDF, docx, md, txt), then write in that style. Use when the user asks to distill, learn, imitate, or apply an academic author's, lab's, or journal's writing style. Works in Claude Code and Codex as a full skill folder. Produces a single Academic-Writing-DNA.md.
---

# Academic Writing DNA

Distill a writing style from a folder of papers. Then write new content in that style.

**Supported CLIs**:
- **Claude Code** — installs to `~/.claude/skills/`, invoked as `/academic-writing-dna-skill`
- **Codex** — installs as the full folder at `~/.codex/skills/academic-writing-dna-skill/`, invoked as `$academic-writing-dna-skill`

The skill has **two modes** (Distill, Write) and **3 working components**:
1. **The agent** — read files, infer style, write output
2. **scripts/quantify.py** — precise numbers (word counts, sentence length, citation density, etc.; supports `.md`, `.txt`, `.pdf`, `.docx`)
3. **docs/** — curated references (cliche blacklist, 4 paper-type structure templates, quality checklist)

---

## Mode 1: Distill

User says: "蒸馏 [folder] 的写作风格" / "distill the style of [folder]" / "用 DBM研究/ 蒸馏风格".

### Step 1: List and read files

1. List the folder with Bash. Identify all readable files. Accept `.pdf`, `.docx`, `.md`, `.txt`.
2. Read every file using available file-reading tools. For precise quantification, `scripts/quantify.py` can extract text from `.md`, `.txt`, `.pdf`, and `.docx`.
3. For each file, note: paper type (IMRAD / review / thesis / conference), language (en/zh/mixed), approximate word count, venue, year, ref count, figure count.

If the folder has 0 readable files, refuse and ask user to add some.

### Step 2: Run quantify.py for precise numbers (default on)

Try to run the helper script to get precise quantitative numbers:

```bash
python scripts/quantify.py <folder>
```

If it succeeds, read the resulting `quantify_report.json`. Use these numbers in L1/L4/L6 of the output (much more accurate than estimating).

If it fails (Python not available, jieba not installed, etc.), tell the user once:
> "scripts/quantify.py 跑不起来（原因：X）。我直接用估的。如果需要精确数字，可以 pip install jieba 后重试。"

Then continue with your own estimates.

### Step 3: Read reference docs

Read these to inform the distillation (this is the curated knowledge that makes the skill valuable):
- `docs/cliche-blacklist.md` — 35 academic cliches to flag and avoid in L1
- `docs/structure-templates.md` — 4 paper-type sub-templates for L2 (IMRAD, review, thesis, conference)
- `docs/quality-checklist.md` — 8-point self-check for after distillation
- `docs/quantify-interpretation.md` — how to interpret quantify_report.json fields

### Step 4: Distill 7 layers

| Layer | Source | Method |
| - | - | - |
| **L0 学术元信息** | file metadata + visible header | Word count range, ref format, venue conventions, submission constraints |
| **L1 学术语言DNA** | quantify_report.json + your reading + cliche-blacklist.md | Sentence length (use aggregate), passive ratio, first person, cliche hits (use counts from report) |
| **L2 学术结构模板** | your reading + structure-templates.md | Per paper type: which sub-template matches? |
| **L3 选题逻辑** | your reading | When does the author write? What angles? What gaps? |
| **L4 素材策略** | quantify_report.json + your reading | Citation density (use report number), venue distribution (use report's top venues), evidence types |
| **L5 认知框架** | your reading | 3-5 core propositions, argumentation pattern (claim → evidence → limitation → rebuttal → conclusion) |
| **L6 视觉风格** | quantify_report.json + your reading | Figure count (use report avg), table count, layout density |

For each layer, prefer report numbers over your estimates.

### Step 5: Write the output

Write to `<folder>/Academic-Writing-DNA.md` using the structure in `docs/output-template.md`. Keep total length ≤ 5000 字. The structure:

```
# Academic-Writing-DNA: [Target Name]
> 蒸馏自 N 篇论文, 日期 YYYY-MM-DD
## L0 学术元信息
## L1 学术语言DNA
## L2 学术结构模板
## L3 选题逻辑
## L4 素材策略
## L5 认知框架
## L6 视觉风格
## 适用与不适用
## 边界
```

### Step 6: Self-check

After writing, run through `docs/quality-checklist.md` and fix any issues.

### Step 7: Tell the user

- "已蒸馏 N 篇论文, 写入 Academic-Writing-DNA.md"
- 3-bullet summary of what was found
- Mention if quantify.py ran or fell back
- Ask: "要用这个风格写新内容吗？"

### Edge cases

- **1 paper**: Mark output as "演示模式 — 仅 1 篇, 风格归纳可能不稳定"
- **Mixed languages**: Distill each language separately
- **Mixed disciplines**: Note in output that style may not transfer

---

## Mode 2: Write

Trigger: user says "帮我写..." / "write..." / "draft..." / "草拟...".

### Step 1: Find existing DNA

Search for `Academic-Writing-DNA.md`:
- In the current working directory
- In parent directories (up to 3 levels)
- In any folder the user mentioned in this session

If multiple found, ask: "你有多个 DNA: A, B, C. 用哪个？"
If none found, write normally (optionally offer to distill first).

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

Just write. The DNA file is the spec.

### Step 4: Optional self-check

After writing, optionally offer:
> "需要我对照 L1/L2/L5 自检一下吗？"

If yes, compare the draft against the DNA's L1 (cliches), L2 (structure), L5 (argumentation).

---

## What's in the package (so this isn't "just a prompt")

```
academic-writing-dna-skill/
├── SKILL.md                       ← you are here. The workflow. (Claude Code)
├── references/zh-workflow.md       ← Chinese reference workflow (not a second skill entry)
├── codex/
│   └── prompt.md                  ← Legacy prompt-only fallback; prefer full skill install
├── docs/
│   ├── cliche-blacklist.md        ← 35 academic cliches (curated knowledge)
│   ├── structure-templates.md     ← 4 paper-type sub-templates (curated knowledge)
│   ├── output-template.md         ← Standard structure for the DNA file
│   ├── quality-checklist.md       ← 8-point self-check
│   └── quantify-interpretation.md ← How to read quantify_report.json
├── scripts/
│   └── quantify.py                ← Precise stats (default on, jieba optional)
├── examples/
│   ├── sample_paper.md            ← Example input
│   └── sample-distilled-dna.md    ← Example output
└── tests/                          ← quantify.py tests
```

Without `docs/` and `scripts/`, the skill can work but produces thinner output. With them, you get precise numbers + curated knowledge + consistent format.

---

## Boundaries

For learning and personal writing-asset accumulation only. Do not use to impersonate, plagiarize, or evade plagiarism checks.
