"""quantify.py 的基础测试"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

# 确保可导入 quantify
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.quantify import (
    load_text,
    collect_paper_files,
    detect_lang,
    split_sentences,
    count_words_en,
    count_words_zh,
    analyze_language,
    analyze_citations,
    analyze_figures,
    aggregate,
    load_cliche_blacklist,
)


def write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    import zipfile

    body = "".join(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs)
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            "</Types>",
        )
        zf.writestr("word/document.xml", document_xml)


def write_minimal_pdf(path: Path, text: str) -> None:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {len(escaped) + 37} >>\nstream\nBT /F1 12 Tf 72 72 Td ({escaped}) Tj ET\nendstream\nendobj\n".encode("latin-1"),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    chunks = [b"%PDF-1.4\n"]
    offsets = []
    for obj in objects:
        offsets.append(sum(len(c) for c in chunks))
        chunks.append(obj)
    xref_start = sum(len(c) for c in chunks)
    xref = [b"xref\n0 6\n0000000000 65535 f \n"]
    xref.extend(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets)
    chunks.extend(xref)
    chunks.append(f"trailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii"))
    path.write_bytes(b"".join(chunks))


def test_load_text_strips_bom(tmp_path):
    p = tmp_path / "a.md"
    p.write_bytes(b"\xef\xbb\xbfhello")
    assert load_text(p) == "hello"


def test_collect_paper_files_includes_pdf_and_docx(tmp_path):
    for name in ["a.md", "b.txt", "c.pdf", "d.docx", "ignore.png"]:
        (tmp_path / name).write_text("x", encoding="utf-8")

    files = [p.name for p in collect_paper_files(tmp_path)]

    assert files == ["a.md", "b.txt", "c.pdf", "d.docx"]


def test_load_text_reads_docx(tmp_path):
    p = tmp_path / "paper.docx"
    write_minimal_docx(p, ["This is the abstract.", "This is the conclusion."])

    text = load_text(p)

    assert "This is the abstract." in text
    assert "This is the conclusion." in text


def test_load_text_reads_simple_pdf(tmp_path):
    p = tmp_path / "paper.pdf"
    write_minimal_pdf(p, "This PDF sentence was extracted.")

    text = load_text(p)

    assert "This PDF sentence was extracted." in text


def test_detect_lang_pure_english():
    assert detect_lang("This is English text") == "en"


def test_detect_lang_pure_chinese():
    assert detect_lang("这是一段中文") == "zh"


def test_count_words_en():
    assert count_words_en("I love NLP") == 3
    assert count_words_en("Hello, world! How are you?") == 5


def test_count_words_zh():
    assert count_words_zh("我爱自然语言处理") == 8


def test_split_sentences_en():
    sents = split_sentences("First. Second. Third.", lang="en")
    assert sents == ["First.", "Second.", "Third."]


def test_split_sentences_zh():
    sents = split_sentences("第一句。第二句！第三句？", lang="zh")
    assert sents == ["第一句。", "第二句！", "第三句？"]


def test_analyze_language_basic_en():
    text = "The hypothesis was tested. The result is significant. " * 20
    stats = analyze_language(text, "en", cliches=["first time", "novel insight"])
    assert stats["avg_sentence_length"] > 0
    assert stats["passive_ratio"] > 0  # "was tested" is passive
    assert "first time" not in stats["cliche_hits"]  # not in this text


def test_analyze_language_detects_cliches():
    text = "This is a novel insight. First time we show this. " * 5
    stats = analyze_language(text, "en", cliches=["novel insight", "first time"])
    assert stats["cliche_hits"]["novel insight"] >= 5
    assert stats["cliche_hits"]["first time"] >= 5


def test_analyze_citations_vancouver():
    text = "Recent work [1,2] showed X. Others [3] confirmed.\n\n## References\n\n1. Smith J. Nature 2020.\n2. Doe A. Cell 2021.\n3. Lee K. Science 2022."
    stats = analyze_citations(text)
    assert stats["intext_citation_count"] == 3
    assert stats["ref_count"] == 3
    assert "Nature" in stats["venue_distribution"]
    assert "Cell" in stats["venue_distribution"]
    assert "Science" in stats["venue_distribution"]


def test_analyze_citations_no_refs():
    text = "No references here."
    stats = analyze_citations(text)
    assert stats["ref_count"] == 0
    assert stats["venue_distribution"] == {}


def test_analyze_figures():
    text = "Intro. ![](fig1.png)\n\nBody. ![](fig2.png)\n\n| A | B |\n|---|---|\n| 1 | 2 |"
    stats = analyze_figures(text)
    assert stats["figure_count"] == 2
    assert stats["table_row_count"] >= 2


def test_aggregate_means():
    per_paper = [
        {"language_stats": {"avg_sentence_length": 20, "passive_ratio": 0.1,
                            "short_sentence_ratio": 0.3, "long_sentence_ratio": 0.2,
                            "first_person_ratio": 0.0, "cliche_hits": {}},
         "citation_stats": {"citations_per_1000_words": 8, "ref_count": 5,
                            "venue_distribution": {"Nature": 1}},
         "figure_stats": {"figure_count": 2, "table_row_count": 1},
         "meta": {"section_count": 4}},
        {"language_stats": {"avg_sentence_length": 30, "passive_ratio": 0.3,
                            "short_sentence_ratio": 0.4, "long_sentence_ratio": 0.3,
                            "first_person_ratio": 0.1, "cliche_hits": {}},
         "citation_stats": {"citations_per_1000_words": 12, "ref_count": 10,
                            "venue_distribution": {"Nature": 2, "Cell": 1}},
         "figure_stats": {"figure_count": 4, "table_row_count": 2},
         "meta": {"section_count": 6}},
    ]
    agg = aggregate(per_paper)
    assert agg["avg_language_stats_avg_sentence_length"] == 25
    assert agg["avg_citation_stats_citations_per_1000_words"] == 10
    assert agg["avg_figure_stats_figure_count"] == 3
    assert "Nature" in agg["venue_distribution_top10"]


def test_load_cliche_blacklist():
    repo = Path(__file__).parent.parent
    cliches = load_cliche_blacklist(repo)
    assert len(cliches) >= 30  # 35 in the file
    assert "novel insight" in cliches
    assert "显著差异" in cliches


def test_cli_runs_on_examples(tmp_path):
    """End-to-end: 运行 quantify.py on examples/"""
    examples = Path(__file__).parent.parent / "examples"
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quantify.py"),
         str(examples), "--no-jieba"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "OK: analyzed" in result.stdout
    report_path = examples / "quantify_report.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert "per_paper" in data
    assert "aggregate" in data
    assert data["paper_count"] >= 2
    # Cleanup
    report_path.unlink()


# === 验证 docs/ 资源完整性（这些是 skill 的"知识库"）===

def test_docs_cliche_blacklist_exists():
    p = Path(__file__).parent.parent / "docs" / "cliche-blacklist.md"
    assert p.exists(), "Missing docs/cliche-blacklist.md — needed by SKILL.md"
    content = p.read_text(encoding="utf-8")
    # 至少包含中英各 10 条
    assert "novel insight" in content
    assert "显著差异" in content
    # 至少 30 个 bullet
    n_bullets = content.count("\n- ")
    assert n_bullets >= 30


def test_docs_structure_templates_exists():
    p = Path(__file__).parent.parent / "docs" / "structure-templates.md"
    assert p.exists(), "Missing docs/structure-templates.md — needed by SKILL.md"
    content = p.read_text(encoding="utf-8")
    # 4 个子模板
    assert "子模板 A" in content
    assert "子模板 B" in content
    assert "子模板 C" in content
    assert "子模板 D" in content
    # 4 类论文名
    assert "IMRAD" in content
    assert "综述" in content
    assert "学位论文" in content
    assert "会议" in content


def test_docs_output_template_exists():
    p = Path(__file__).parent.parent / "docs" / "output-template.md"
    assert p.exists(), "Missing docs/output-template.md"
    content = p.read_text(encoding="utf-8")
    # 7 层都列出
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        assert layer in content


def test_docs_quality_checklist_exists():
    p = Path(__file__).parent.parent / "docs" / "quality-checklist.md"
    assert p.exists(), "Missing docs/quality-checklist.md"
    content = p.read_text(encoding="utf-8")
    # 至少 8 项打勾
    assert content.count("□") >= 8


def test_docs_quantify_interpretation_exists():
    p = Path(__file__).parent.parent / "docs" / "quantify-interpretation.md"
    assert p.exists(), "Missing docs/quantify-interpretation.md"
    content = p.read_text(encoding="utf-8")
    assert "aggregate" in content
    assert "quantify_report.json" in content


def test_skill_md_references_docs():
    """SKILL.md 必须引用 docs/ 才能形成完整 skill."""
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "docs/cliche-blacklist.md" in skill
    assert "docs/structure-templates.md" in skill
    assert "scripts/quantify.py" in skill
    assert "docs/quality-checklist.md" in skill


def test_skill_md_says_quantify_runs_by_default():
    """SKILL.md 默认开启 quantify.py（用户提的硬要求）."""
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text(encoding="utf-8")
    # 找到 Step 2 上下文
    assert "Step 2" in skill
    assert "quantify.py" in skill
    # 应该表达"默认/自动/总是跑"
    assert "default" in skill.lower() or "默认" in skill or "automatically" in skill.lower() or "Run quantify" in skill


def test_codex_prompt_exists():
    """Codex legacy prompt fallback exists."""
    p = Path(__file__).parent.parent / "codex" / "prompt.md"
    assert p.exists(), "Missing codex/prompt.md — needed for Codex CLI support"
    content = p.read_text(encoding="utf-8")
    # 必须包含 7 层
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        assert layer in content, f"codex/prompt.md missing layer {layer}"
    # 必须包含两个模式
    assert "Mode 1" in content and "Mode 2" in content
    assert "~/.codex/skills" in content or ".codex/skills" in content


def test_skill_md_mentions_codex():
    """SKILL.md 应该声明同时支持 Claude Code 和 Codex CLI."""
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "Codex" in skill
    assert "~/.codex/skills" in skill or "codex" in skill.lower()


def test_chinese_workflow_is_reference_not_second_skill():
    """Chinese workflow should be a reference file, not a second skill entry."""
    repo = Path(__file__).parent.parent
    assert not list(repo.glob("*.skill.md"))
    workflow = repo / "references" / "zh-workflow.md"
    assert workflow.exists()
    assert "Codex" in workflow.read_text(encoding="utf-8")
