from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from engine.ocr_processor import extract_text


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[-1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def cer(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein(reference, hypothesis) / max(1, len(reference))


def keyword_recall(reference: str, hypothesis: str) -> float:
    ref_words = {w for w in reference.lower().split() if w}
    if not ref_words:
        return 1.0
    hyp_words = {w for w in hypothesis.lower().split() if w}
    return len(ref_words.intersection(hyp_words)) / len(ref_words)


def run_benchmark(dataset_csv: Path, report_md: Path | None = None) -> dict:
    rows = []
    with dataset_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    results = []
    for row in rows:
        image_path = Path(row["image_path"])
        reference = row.get("ground_truth", "")
        with image_path.open("rb") as f:
            hypothesis = extract_text(f.read())
        results.append(
            {
                "image_path": str(image_path),
                "cer": cer(reference, hypothesis),
                "keyword_recall": keyword_recall(reference, hypothesis),
            }
        )

    avg_cer = sum(r["cer"] for r in results) / max(1, len(results))
    avg_kw_recall = sum(r["keyword_recall"] for r in results) / max(1, len(results))
    summary = {
        "samples": len(results),
        "avg_cer": avg_cer,
        "avg_keyword_recall": avg_kw_recall,
        "results": results,
    }

    if report_md is not None:
        lines = [
            "# OCR Benchmark Report",
            "",
            f"- Samples: {summary['samples']}",
            f"- Average CER: {summary['avg_cer']:.4f}",
            f"- Average Keyword Recall: {summary['avg_keyword_recall']:.4f}",
            "",
            "## Per-file",
            "",
        ]
        for item in results:
            lines.append(
                f"- `{item['image_path']}` | CER: {item['cer']:.4f} | Keyword Recall: {item['keyword_recall']:.4f}"
            )
        report_md.write_text("\n".join(lines), encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OCR quality benchmark")
    parser.add_argument("--dataset", required=True, help="CSV with columns: image_path,ground_truth")
    parser.add_argument("--report", default=None, help="Optional markdown report output path")
    args = parser.parse_args()

    dataset_csv = Path(args.dataset)
    report_md = Path(args.report) if args.report else None
    summary = run_benchmark(dataset_csv, report_md=report_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
