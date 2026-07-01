"""quantify.py — 学术论文语料的轻量量化分析

academic-writing-dna-skill v0.2.x 的可选辅助脚本。
主流程（Claude 直接读 PDF/docx）不需要此脚本；只有需要精确数字时才跑。

Usage:
    python scripts/quantify.py <folder>
    python scripts/quantify.py <folder> --output <json-path>
    python scripts/quantify.py <folder> --no-jieba   # 跳过中文分词

Output:
    <folder>/quantify_report.json

支持文件: .md, .txt
依赖: 仅 Python 3.10+ 标准库；可选 jieba 用于中文分词
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# === 文本处理 ===

_EN_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_ZH_CHAR = re.compile(r"[一-鿿]")
_INTEXT_BRACKETED = re.compile(r"\[(\d+(?:\s*[,，、]\s*\d+)*)\]")
_INTEXT_NAMED = re.compile(r"\b([A-Z][a-z]+(?:\s+et\s+al\.?)?)\s*\((\d{4})\)")
_REF_HEADING = re.compile(
    r"^#{1,6}\s*(references|参考文献|bibliography)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_EN_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
_ZH_SENT = re.compile(r"(?<=[。！？!?])\s*")
_MATH_BLOCK = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_IMG_MD = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_PARAGRAPH = re.compile(r"\n\s*\n")
_PASSIVE_EN = re.compile(r"\b(is|was|were|are|be|been|being)\s+\w+ed\b", re.IGNORECASE)
_FIRST_PERSON = re.compile(r"\b(I|we|our|us|my)\b", re.IGNORECASE)
_ZH_FIRST_PERSON = re.compile(r"(我们|本文|本研究|笔者)")

# 已知期刊清单（用于引文统计）
_KNOWN_VENUES = [
    "Nature", "Science", "Cell", "Lancet", "NEJM", "JAMA", "BMJ",
    "PNAS", "Neuron", "Immunity", "Nat Med", "Nat Genet", "Nat Biotechnol",
    "Mol Cell", "EMBO J", "JBC", "JCI", "Gut", "Hepatology",
    "Bioinformatics", "NAR", "BMC", "PLoS", "Nat Commun",
]


def load_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="replace")


def detect_lang(text: str) -> str:
    """zh if Chinese ratio > 0.5, else en."""
    visible = [c for c in text if not c.isspace()]
    if not visible:
        return "en"
    zh = sum(1 for c in visible if _ZH_CHAR.match(c))
    return "zh" if zh / len(visible) > 0.5 else "en"


def split_sentences(text: str, lang: str) -> list[str]:
    text = _MATH_BLOCK.sub("", text).strip()
    if lang == "zh":
        return [p.strip() for p in _ZH_SENT.split(text) if p.strip()]
    return [p.strip() for p in _EN_SENT.split(text) if p.strip()]


def count_words_en(text: str) -> int:
    return len(_EN_WORD.findall(text))


def count_words_zh(text: str) -> int:
    return sum(1 for c in text if _ZH_CHAR.match(c))


# === 各维度分析 ===

def analyze_language(text: str, lang: str, cliches: list[str]) -> dict:
    sents = split_sentences(text, lang)
    if not sents:
        return {"avg_sentence_length": 0, "short_ratio": 0, "long_ratio": 0,
                "passive_ratio": 0, "first_person_ratio": 0, "cliche_hits": {}}
    if lang == "en":
        lens = [count_words_en(s) for s in sents]
    else:
        lens = [count_words_zh(s) for s in sents]
    avg_len = sum(lens) / len(lens)
    short = sum(1 for l in lens if l <= 15) / len(lens)
    long_ = sum(1 for l in lens if l >= 50) / len(lens)
    if lang == "en":
        passive = len(_PASSIVE_EN.findall(text)) / len(sents)
        first_p = len(_FIRST_PERSON.findall(text)) / len(sents)
    else:
        passive = 0.0
        first_p = len(_ZH_FIRST_PERSON.findall(text)) / len(sents)
    text_lower = text.lower()
    cliche_hits = {p: text_lower.count(p.lower()) for p in cliches if text_lower.count(p.lower()) > 0}
    punct_n = len(text) or 1
    punct = {
        "em_dash_per_1000": text.count("—") * 1000 / punct_n,
        "colon_per_1000": (text.count(":") + text.count("：")) * 1000 / punct_n,
        "semicolon_per_1000": (text.count(";") + text.count("；")) * 1000 / punct_n,
    }
    return {
        "avg_sentence_length": round(avg_len, 2),
        "short_sentence_ratio": round(short, 3),
        "long_sentence_ratio": round(long_, 3),
        "passive_ratio": round(passive, 3),
        "first_person_ratio": round(first_p, 3),
        "cliche_hits": cliche_hits,
        "punctuation_density_per_1000": {k: round(v, 2) for k, v in punct.items()},
    }


def analyze_citations(text: str) -> dict:
    """返回: intext_citation_count, citations_per_1000_words, ref_count, venue_distribution"""
    intext_brackets = sum(len(re.findall(r"\d+", m)) for m in _INTEXT_BRACKETED.findall(text))
    intext_named = len(_INTEXT_NAMED.findall(text))
    intext_count = intext_brackets + intext_named
    m = _REF_HEADING.search(text)
    refs_text = text[m.end():] if m else ""
    if not refs_text:
        return {"intext_citation_count": intext_count, "citations_per_1000_words": 0,
                "ref_count": 0, "venue_distribution": {}}
    ref_count = len(re.findall(r"^\s*(?:\[\d+\]|\d+\.)\s+", refs_text, re.MULTILINE))
    venues = {}
    for v in _KNOWN_VENUES:
        n = len(re.findall(rf"\b{re.escape(v)}\b", refs_text))
        if n:
            venues[v] = n
    lang = detect_lang(text)
    if lang == "en":
        wc = count_words_en(text)
    else:
        wc = count_words_zh(text)
    rate = round(intext_count * 1000 / max(wc, 1), 2)
    return {
        "intext_citation_count": intext_count,
        "citations_per_1000_words": rate,
        "ref_count": ref_count,
        "venue_distribution": dict(sorted(venues.items(), key=lambda x: -x[1])),
    }


def analyze_figures(text: str) -> dict:
    figures = _IMG_MD.findall(text)
    table_rows = _TABLE_ROW.findall(text)
    return {
        "figure_count": len(figures),
        "table_row_count": len(table_rows),
    }


def analyze_meta(text: str) -> dict:
    headings = re.findall(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
    return {
        "section_count": len(headings),
        "headings": [h[1].strip() for h in headings[:20]],
    }


# === 主流程 ===

def load_cliche_blacklist(repo_root: Path) -> list[str]:
    """从 docs/cliche-blacklist.md 加载套话清单"""
    p = repo_root / "docs" / "cliche-blacklist.md"
    if not p.exists():
        return []
    phrases = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^[-*]\s+(.+)$", line.strip())
        if m:
            phrases.append(m.group(1).strip())
    return phrases


def analyze_paper(path: Path, cliches: list[str], use_jieba: bool) -> dict:
    text = load_text(path)
    lang = detect_lang(text)
    if lang == "en":
        wc = count_words_en(text)
    else:
        wc = count_words_zh(text)
    return {
        "filename": path.name,
        "language": lang,
        "word_count": wc,
        "meta": analyze_meta(text),
        "language_stats": analyze_language(text, lang, cliches),
        "citation_stats": analyze_citations(text),
        "figure_stats": analyze_figures(text),
    }


def aggregate(per_paper: list[dict]) -> dict:
    """对所有论文的数值字段取平均"""
    if not per_paper:
        return {}
    keys_num = [
        ("language_stats", "avg_sentence_length"),
        ("language_stats", "short_sentence_ratio"),
        ("language_stats", "long_sentence_ratio"),
        ("language_stats", "passive_ratio"),
        ("language_stats", "first_person_ratio"),
        ("citation_stats", "citations_per_1000_words"),
        ("citation_stats", "ref_count"),
        ("figure_stats", "figure_count"),
        ("figure_stats", "table_row_count"),
        ("meta", "section_count"),
    ]
    agg = {}
    for section, key in keys_num:
        vals = [p[section][key] for p in per_paper if section in p and key in p[section]]
        if vals:
            agg[f"avg_{section}_{key}"] = round(sum(vals) / len(vals), 2)
    # 套话合并
    all_cliche = Counter()
    for p in per_paper:
        for phrase, n in p.get("language_stats", {}).get("cliche_hits", {}).items():
            all_cliche[phrase] += n
    agg["cliche_hits_top10"] = dict(all_cliche.most_common(10))
    # 期刊合并
    all_venues = Counter()
    for p in per_paper:
        for v, n in p.get("citation_stats", {}).get("venue_distribution", {}).items():
            all_venues[v] += n
    agg["venue_distribution_top10"] = dict(all_venues.most_common(10))
    return agg


def main():
    ap = argparse.ArgumentParser(description="Quantify academic paper corpus")
    ap.add_argument("folder", help="Folder containing .md/.txt papers")
    ap.add_argument("--output", help="Output JSON path (default: <folder>/quantify_report.json)")
    ap.add_argument("--no-jieba", action="store_true", help="Skip Chinese tokenization (no extra deps)")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"ERROR: {folder} is not a directory", file=sys.stderr)
        sys.exit(1)

    files = sorted(list(folder.glob("*.md")) + list(folder.glob("*.txt")))
    if not files:
        print(f"ERROR: no .md/.txt files in {folder}", file=sys.stderr)
        sys.exit(1)

    # jieba 是可选的（不强制安装）
    if not args.no_jieba:
        try:
            import jieba  # noqa: F401
            jieba.setLogLevel("ERROR")
        except ImportError:
            print("INFO: jieba not installed, Chinese tokenization disabled. Use --no-jieba to silence this.")

    repo_root = Path(__file__).parent.parent
    cliches = load_cliche_blacklist(repo_root)

    per_paper = [analyze_paper(f, cliches, use_jieba=not args.no_jieba) for f in files]
    report = {
        "folder": str(folder.resolve()),
        "paper_count": len(files),
        "per_paper": per_paper,
        "aggregate": aggregate(per_paper),
    }

    out_path = Path(args.output) if args.output else folder / "quantify_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: analyzed {len(files)} papers → {out_path}")
    # 打印 aggregate 摘要
    for k, v in report["aggregate"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
