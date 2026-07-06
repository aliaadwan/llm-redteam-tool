from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List

from jinja2 import Environment, FileSystemLoader

from core.scanner import ScanResult


def _status_class(pass_rate: int) -> str:
    if pass_rate >= 80:
        return "good"
    if pass_rate >= 50:
        return "warn"
    return "bad"


def _category_summary(results: List[ScanResult]) -> list:
    """Computes the resilience (pass rate) for each category - weakest shown first."""
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r.category_name].append(r)

    summary = []
    for name, items in by_cat.items():
        total = len(items)
        passed = sum(1 for i in items if i.verdict == "PASS")
        failed = sum(1 for i in items if i.verdict == "FAIL")
        review = sum(1 for i in items if i.verdict == "NEEDS_REVIEW")
        pass_rate = round((passed / total) * 100) if total else 0
        summary.append({
            "name": name,
            "total": total,
            "passed": passed,
            "failed": failed,
            "needs_review": review,
            "pass_rate": pass_rate,
            "status": _status_class(pass_rate),
        })

    return sorted(summary, key=lambda s: s["pass_rate"])


def generate_report(
    results: List[ScanResult],
    model_name: str,
    output_path: str = "reports/report.html",
) -> str:
    """Builds an HTML report from scan results and saves it. Returns the full file path."""
    total = len(results)
    pass_count = sum(1 for r in results if r.verdict == "PASS")
    fail_count = sum(1 for r in results if r.verdict == "FAIL")
    review_count = sum(1 for r in results if r.verdict == "NEEDS_REVIEW")
    error_count = sum(1 for r in results if r.verdict == "ERROR")

    # Sort by category so the groupby in the template works correctly
    results_by_category = sorted(results, key=lambda r: r.category_id)

    project_root = Path(__file__).resolve().parent.parent
    env = Environment(loader=FileSystemLoader(str(project_root / "templates")))
    template = env.get_template("report_template.html")

    html = template.render(
        model_name=model_name,
        scan_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total=total,
        pass_count=pass_count,
        fail_count=fail_count,
        review_count=review_count,
        error_count=error_count,
        category_summary=_category_summary(results),
        results_by_category=results_by_category,
    )

    out_path = project_root / output_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)