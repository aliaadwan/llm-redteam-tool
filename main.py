import argparse

from config import Config
from providers.llm_provider import LLMProvider
from core.scanner import run_scan
from core.report import generate_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="LLM Red-Teaming Tool - a security scanner for LLM-based applications"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only use this many prompts per category (for a quick test run). Default: all prompts"
    )
    parser.add_argument(
        "--judge", action="store_true",
        help="Enable LLM-as-judge for ambiguous cases (uses extra API calls)"
    )
    parser.add_argument(
        "--system-prompt-file", type=str, default=None,
        help="Path to a text file with custom system instructions "
             "(to test whether a custom system prompt survives under attack)"
    )
    parser.add_argument(
        "--output", type=str, default="reports/report.html",
        help="Where to save the report (default: reports/report.html)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    Config.validate()

    system_prompt = ""
    if args.system_prompt_file:
        with open(args.system_prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
        print(f"Loaded custom system prompt from: {args.system_prompt_file}")

    target_provider = LLMProvider(Config.TARGET_MODEL)
    judge_provider = LLMProvider(Config.JUDGE_MODEL) if args.judge else None

    if args.judge:
        print(f"Judge enabled (judge model): {Config.JUDGE_MODEL}")

    scope = "full scan" if not args.limit else f"limited run (limit={args.limit} per category)"
    print(f"Starting scan on {Config.TARGET_MODEL} — {scope}")

    results = run_scan(
        target_provider,
        judge_provider=judge_provider,
        system_prompt=system_prompt,
        limit_per_category=args.limit,
    )

    report_path = generate_report(
        results, model_name=target_provider.model_name, output_path=args.output
    )

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    fail_count = sum(1 for r in results if r.verdict == "FAIL")
    review_count = sum(1 for r in results if r.verdict == "NEEDS_REVIEW")
    error_count = sum(1 for r in results if r.verdict == "ERROR")

    print(f"\nReport ready: {report_path}")
    print(
        f"PASS: {pass_count} | FAIL: {fail_count} | "
        f"NEEDS_REVIEW: {review_count} | ERROR: {error_count} | Total: {len(results)}"
    )


if __name__ == "__main__":
    main()