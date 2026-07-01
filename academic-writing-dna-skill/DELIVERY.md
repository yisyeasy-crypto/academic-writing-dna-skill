# academic-writing-dna-skill · 使用说明

> 一个让 Claude 学会按某位作者风格写论文的 skill

---

## 1. 这是什么

把一组论文（PDF、docx、md、txt 都可以）放进一个文件夹，让 Claude 读一遍，生成一份 `Academic-Writing-DNA.md` 描述这个作者的写作风格。之后你让 Claude 写东西时，它会问"要用这个风格吗？"，你同意就直接按风格写。

整个 skill 由 5 类文件组成（**不是单个文件**）：

| 类型 | 文件 | 作用 |
| - | - | - |
| 工作流 | `SKILL.md` / `学术写作蒸馏器.skill.md` | Claude 启动 skill 时按这个操作 |
| 知识库 | `docs/` (4 份) | 套话黑名单、结构模板、质量清单、量化解读 |
| 工具 | `scripts/quantify.py` | 精确量化（句长、引文密度等） |
| 参考 | `examples/` | 输入输出示例 |
| 文档 | `README.md` / `DELIVERY.md` / `LICENSE` | 给**人**看的，Claude 不读 |

**安装时必须保留所有类型**——只复制 SKILL.md 会让 skill 退化成"普通提示词"。

---

## 2. 安装

**支持的 CLI**：
- **Claude Code**（用 `SKILL.md`，命令 `/academic-writing-dna-skill`）
- **Codex CLI**（用 `codex/prompt.md`，命令 `/academic-writing-dna`）

### 安装到 Claude Code

```bash
# 把整个 academic-writing-dna-skill/ 文件夹放到合适位置
# 然后：

# Linux / macOS：软链到 Claude Code skills 目录
ln -s /path/to/academic-writing-dna-skill ~/.claude/skills/

# Windows (PowerShell)：创建符号链接
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\academic-writing-dna-skill" `
  -Target "C:\path\to\academic-writing-dna-skill"
```

**重要**：软链的是**整个文件夹**，不是文件夹里的某个文件。Claude Code 会自动读取 `SKILL.md` 启动 skill，并通过它访问同目录下的 `docs/` 和 `scripts/`。

**验证**：在 Claude Code 里输入 `/academic-writing-dna-skill`，如果出现 skill 说明就是装好了。

### 安装到 Codex CLI

把 `codex/prompt.md` 复制到 `~/.codex/prompts/academic-writing-dna.md`：

```bash
# Linux / macOS
mkdir -p ~/.codex/prompts
cp /path/to/academic-writing-dna-skill/codex/prompt.md ~/.codex/prompts/academic-writing-dna.md

# Windows (PowerShell)
$dest = "$env:USERPROFILE\.codex\prompts\academic-writing-dna.md"
New-Item -ItemType File -Path $dest -Force
Copy-Item "C:\path\to\academic-writing-dna-skill\codex\prompt.md" $dest
```

**重要**：Codex prompt 引用 `docs/` 和 `scripts/`，所以也要确保 `academic-writing-dna-skill/` 文件夹**留在原位**。prompt 文件只是入口。

**验证**：在 Codex CLI 里输入 `/academic-writing-dna`，如果 prompt 加载就是装好了。

---

## 3. 使用

### 蒸馏写作风格

1. 把目标作者/期刊的论文（1-10 篇 .pdf/.docx/.md/.txt）放进一个文件夹，例如 `~/papers/smith-lab/`
2. 在 Claude Code 里说：
   ```
   蒸馏 ~/papers/smith-lab/ 这个文件夹的写作风格
   ```
3. Claude 会：
   - 读所有文件
   - 自动跑 `scripts/quantify.py`（需要 Python + jieba）获取精确数字
   - 读 `docs/cliche-blacklist.md` 和 `docs/structure-templates.md`
   - 生成 `~/papers/smith-lab/Academic-Writing-DNA.md`
4. 完成后 Claude 报"已蒸馏 N 篇"，并通过 8 项质量自检

### 用风格写新内容

直接说：

```
帮我写一段关于 [你的研究主题] 的内容
```

Claude 找到你已有的 DNA 文件，会问：

> "我注意到你有一个 Smith Lab 的写作风格 DNA，要用这个风格写吗？"

你说"用"或"好"，Claude 就按 DNA 里的 L0-L6 规则写。

你**不需要**告诉 Claude：
- 写哪种论文（DNA 里 L2 有 4 个子模板）
- 投稿哪个期刊（DNA 里 L0 写了）
- 写多少字（DNA 里 L1 有字数范围）

DNA 文件就是规范。

### 取消使用风格

说"不用"或"正常写"即可。

---

## 4. 文件说明（每个都重要）

```
academic-writing-dna-skill/
├── SKILL.md                       Claude Code 主提示词 (English)
├── 学术写作蒸馏器.skill.md          Claude Code 主提示词 (中文)
├── codex/
│   └── prompt.md                  ★ Codex CLI 主提示词
├── README.md                      项目简介
├── DELIVERY.md                    ← 本文件
├── LICENSE                        MIT
│
├── docs/                          ★ 知识库（Claude/Codex 蒸馏时读）
│   ├── cliche-blacklist.md        35 条中英学术套话
│   ├── structure-templates.md     4 类论文子模板（IMRAD/综述/学位论文/会议）
│   ├── output-template.md         Academic-Writing-DNA.md 的标准结构
│   ├── quality-checklist.md       蒸馏后 8 项自检清单
│   └── quantify-interpretation.md  怎么读 quantify_report.json
│
├── scripts/                       ★ 工具
│   └── quantify.py                精确量化（句长/引文密度/期刊分布等）
│
├── examples/                      ★ 参考
│   ├── sample_paper.md            输入示例
│   └── sample-distilled-dna.md    输出示例
│
├── tests/                         ★ 测试
│   └── test_quantify.py           quantify.py 的单元测试
│
└── requirements.txt               可选依赖 (jieba, pytest)
```

### 如果只想用基础功能

最低要求：**SKILL.md + 1 个 SKILL 文件 + scripts/ + docs/**。没有这些，skill 不完整。

### 如果 Python 不可用

仍可用：skill 退到"全 LLM 估值"模式，精度下降但功能完整。

---

## 5. 安装可选依赖

主流程不需要 Python。可选依赖（用于精确量化）：

```bash
pip install -r requirements.txt
```

依赖说明：
- `jieba` — 中文分词，quantify.py 用
- `pytest` — 运行 tests/ 用

如果只想用 quantify.py 的基础功能（英文量化），不装 jieba 也能跑：脚本自动跳过中文处理。

---

## 6. 边界

仅用于：学术写作风格学习、个人写作资产沉淀、教学
**禁止**：冒充原作者、抄袭、绕过查重

---

## 7. 反馈

发现问题或有改进建议：提 issue 或直接修改 `SKILL.md`（整个 skill 就是一个提示词 + 参考资料包，修改后立刻生效）。
