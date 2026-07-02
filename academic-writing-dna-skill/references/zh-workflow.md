# 学术写作蒸馏器

> 英文名：academic-writing-dna-skill

**支持的 CLI**：
- **Claude Code** — 安装到 `~/.claude/skills/`，用 `/academic-writing-dna-skill` 调用
- **Codex** — 安装完整 skill 文件夹到 `~/.codex/skills/academic-writing-dna-skill/`，用 `$academic-writing-dna-skill` 调用

两种模式：**蒸馏** 和 **写作**。
3 个工作组件：(1) AI agent 读文件 + 推理；(2) scripts/quantify.py 算精确数字；(3) docs/ 提供 4 份参考。

---

## 模式 1：蒸馏

用户说："蒸馏 [文件夹] 的写作风格" / "distill the style of [folder]"

### 步骤

#### Step 1: 列文件 + 读

1. 用 Bash 列出文件夹，识别 `.pdf` / `.docx` / `.md` / `.txt` 文件
2. 用 Read 工具逐个读取（PDF 和 docx 原生支持）
3. 对每篇记录：论文类型（IMRAD / 综述 / 学位论文 / 会议）、语言（中/英）、字数、期刊、年份、参考文献数、图表数

0 个可读文件：拒绝，让用户加料。

#### Step 2: 跑 quantify.py（默认开启）

```bash
python scripts/quantify.py <文件夹>
```

- 成功：读 `quantify_report.json`，用里面的数字填充 L1/L4/L6
- 失败：告诉用户一次（"Python 不可用 / jieba 没装"），用 Claude 估的值继续

#### Step 3: 读参考文档

必须读：
- `docs/cliche-blacklist.md` — 35 条学术套话
- `docs/structure-templates.md` — 4 类论文子模板
- `docs/quality-checklist.md` — 蒸馏后 8 项自检

#### Step 4: 蒸馏 7 层

| 层 | 数据来源 |
| - | - |
| L0 学术元信息 | 论文头部可见的元信息 |
| L1 学术语言DNA | quantify_report.json + 套话黑名单 |
| L2 学术结构模板 | 论文结构 + structure-templates.md |
| L3 选题逻辑 | 通读理解 |
| L4 素材策略 | quantify_report.json（引文密度、期刊分布）|
| L5 认知框架 | 通读理解（论证链）|
| L6 视觉风格 | quantify_report.json（图表数）+ 通读 |

每层**优先用报告数字**，其次用估的。

#### Step 5: 写输出

写到 `<文件夹>/Academic-Writing-DNA.md`，结构见 `docs/output-template.md`，总长 ≤ 5000 字。

#### Step 6: 自检

按 `docs/quality-checklist.md` 的 8 项逐项打勾。**不合格的修订后再交付**。

#### Step 7: 告诉用户

- "已蒸馏 N 篇论文, 写入 Academic-Writing-DNA.md"
- 3 条要点总结
- 提一下 quantify.py 是否跑了
- 问"要用这个风格写新内容吗？"

### 边界

- 1 篇：标 "演示模式 — 风格归纳可能不稳定"
- 中英混合：分别归纳
- 跨学科：提示风格可能不通用

---

## 模式 2：写作

触发：用户说"帮我写..."、"write..."、"draft..."等

### 步骤

1. **找 DNA**：当前目录、向上 3 层父目录、本会话提到的文件夹，找 `Academic-Writing-DNA.md`
2. **找不到**：正常写，可选地问"需要我先蒸馏你的风格吗？"
3. **找到多个**：让用户选
4. **找到一个**：问 "我注意到你有一个 [target-name] 的写作风格 DNA，要用这个风格写吗？"
   - "用" / "好" → 按 L0-L6 规则写
   - "不用" / "正常" → 正常写
   - 不回答 → 正常写（不追问）
5. **使用风格时不要再问**：论文类型、期刊、字数（DNA 里都有）
6. **可选自检**：写完后问"要对照 L1/L2/L5 自检吗？"

---

## 文件组成（不是"只有 SKILL.md"）

```
academic-writing-dna-skill/
├── SKILL.md                       主 skill 入口
├── references/zh-workflow.md      中文工作流参考（不是第二个 skill 入口）
├── docs/                          ★ 知识库
│   ├── cliche-blacklist.md        35 条套话
│   ├── structure-templates.md     4 类论文子模板
│   ├── output-template.md         输出结构
│   ├── quality-checklist.md       8 项自检
│   └── quantify-interpretation.md 量化结果解读
├── scripts/quantify.py            ★ 工具（精确数字）
├── examples/                      ★ 参考
│   ├── sample_paper.md
│   └── sample-distilled-dna.md
└── tests/test_quantify.py         ★ 测试
```

**只装 SKILL.md 没有 docs/ 和 scripts/，skill 退化成"普通提示词"**——会失去套话黑名单、结构模板、精确量化这些核心价值。

---

## 边界

仅用于学习与个人写作资产沉淀。禁止冒充作者、抄袭、绕过查重。
