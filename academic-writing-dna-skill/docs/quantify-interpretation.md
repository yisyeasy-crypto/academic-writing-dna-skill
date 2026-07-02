# quantify_report.json 解读指南

> 蒸馏 L1/L4/L6 时，agent 应该读这个文件并用其中的数字。
> 这里说明每个字段的含义、单位、合理范围。

---

## 文件位置

`<folder>/quantify_report.json`，由 `python scripts/quantify.py <folder>` 生成。

## 顶层结构

```json
{
  "folder": "<absolute path>",
  "paper_count": N,
  "per_paper": [...],   // 每篇论文的详细数据
  "aggregate": {...}    // 所有论文的均值
}
```

**优先使用 `aggregate` 字段**——是 N 篇论文的均值，比单篇更稳定。

---

## aggregate 字段详解

### L1 相关（语言风格）

| 字段 | 含义 | 典型范围 | 怎么用 |
| - | - | - | - |
| `avg_language_stats_avg_sentence_length` | 平均句长（字） | 15-30 | DNA 里写"平均句长 X 字" |
| `avg_language_stats_short_sentence_ratio` | 短句 (≤15字) 占比 | 0.2-0.5 | DNA 里写"短句占 X%" |
| `avg_language_stats_long_sentence_ratio` | 长句 (≥50字) 占比 | 0.05-0.25 | DNA 里写"长句占 X%" |
| `avg_language_stats_passive_ratio` | 被动语态比例 (英文) | 0.1-0.3 | DNA 里写"被动语态 X%" |
| `avg_language_stats_first_person_ratio` | 第一人称出现率 (英文) | 0-0.2 | DNA 里写"用 'we' 不用 'I'" |
| `cliche_hits_top10` | 出现最多的 10 个套话 | dict | DNA 里写"必须规避的套话" |
| (punctuation_density) | 标点密度 | dict | DNA 里写"标点偏好"（仅在 quantify.py 输出里有） |

### L4 相关（素材策略）

| 字段 | 含义 | 典型范围 | 怎么用 |
| - | - | - | - |
| `avg_citation_stats_citations_per_1000_words` | 每千字引文数 | 5-15 | DNA 里写"引文密度 X/1000 字" |
| `avg_citation_stats_ref_count` | 平均参考文献数 | 20-80 | DNA 里写"参考文献 X 篇" |
| `venue_distribution_top10` | 引用最多的 10 个期刊 | dict | DNA 里写"主要引用 X 期刊" |

### L6 相关（视觉风格）

| 字段 | 含义 | 典型范围 | 怎么用 |
| - | - | - | - |
| `avg_figure_stats_figure_count` | 平均图表数 | 3-8 | DNA 里写"平均 X 个图" |
| `avg_figure_stats_table_row_count` | 平均表格行数 | 5-30 | DNA 里写"平均 X 行表格" |
| `avg_meta_section_count` | 平均章节数 | 4-10 | DNA 里写"X 个章节" |

---

## 使用示例

**Step 1**: 运行 `quantify.py` 后看到：
```json
"aggregate": {
  "avg_language_stats_avg_sentence_length": 22.4,
  "avg_language_stats_passive_ratio": 0.22,
  "avg_citation_stats_citations_per_1000_words": 9.5,
  "venue_distribution_top10": {"Nature": 8, "Cell": 5, "Science": 2},
  "cliche_hits_top10": {"novel insight": 12, "first time": 8, "leverages": 6}
}
```

**Step 2**: Claude 在 L1 节写：
> 平均句长 22.4 字；被动语态 22%；常出现"novel insight" (12 次) / "first time" (8 次) / "leverages" (6 次) 等套话，必须规避。

**Step 3**: 在 L4 节写：
> 引文密度 9.5/1000 字；主要引用 Nature (8) / Cell (5) / Science (2)。

---

## 异常处理

- **空字段**：如果某字段缺失，说明 `quantify.py` 没在那个维度上跑出结果。Claude 用估的。
- **N=1**：aggregate 就是单篇数据，加 "演示模式" 标注。
- **数字看着离谱**（如 avg_sentence_length > 100）：可能是句子分割问题。Claude 用 L2 兜底。

---

## 与 LLM 估值的对比

| 字段 | quantify.py 精度 | Claude 估值精度 |
| - | - | - |
| 句长 | 字符级精确 | ±30% |
| 引文密度 | 字符级精确 | ±50%（取决于 LLM 仔细程度）|
| 期刊分布 | 字符串匹配（24 个期刊）| 可能漏掉不在白名单的期刊 |
| 套话命中 | 子串匹配 | 可能误判（语境理解） |
| 图表数 | 解析 `![]()` 和 `\| \|` | 容易看错 |

**结论**：能跑 quantify.py 就跑，不要让 Claude 估数字。
