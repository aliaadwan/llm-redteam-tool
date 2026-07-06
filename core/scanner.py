"""
-----------------
The main orchestrator: loads the attack prompts dataset, sends each prompt
to the target model one by one, analyzes every response, and collects
everything into a single list of results.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

from providers.base import BaseLLMProvider
from core.analyzer import analyze, AnalysisResult


@dataclass
class ScanResult:
    category_id: str
    category_name: str
    prompt: str
    response_text: str
    verdict: str
    confidence: str
    method: str
    reasoning: str
    model: str


def load_attack_prompts(path: str = None) -> dict:
    """Load the attack prompts file. If path is None, resolve data/attack_prompts.json
    relative to the project root, independent of where the script is run from."""
    if path is None:
        project_root = Path(__file__).resolve().parent.parent
        path = project_root / "data" / "attack_prompts.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_scan(
    target_provider: BaseLLMProvider,
    judge_provider: Optional[BaseLLMProvider] = None,
    system_prompt: str = "",
    dataset_path: str = None,
    limit_per_category: Optional[int] = None,
) -> List[ScanResult]:
    """
    Runs every attack prompt against the target model and returns a list of results.

    Args:
        target_provider: the model being tested (the target)
        judge_provider: optional model used as a judge for ambiguous cases
                        (None = judge disabled, relies on the heuristic only)
        system_prompt: optional system instructions sent with every attempt (useful
                       for testing whether the model keeps its custom rules under pressure)
        dataset_path: custom path to the dataset file (defaults to data/attack_prompts.json)
        limit_per_category: cap the number of prompts per category, for quick test runs
    """
    data = load_attack_prompts(dataset_path)
    categories = data["categories"]

    all_jobs = []
    for cat in categories:
        prompts = cat["prompts"]
        if limit_per_category:
            prompts = prompts[:limit_per_category]
        for prompt in prompts:
            all_jobs.append((cat, prompt))

    results: List[ScanResult] = []

    for cat, prompt in tqdm(all_jobs, desc="Scanning attack prompts"):
        response = target_provider.send_prompt(prompt, system_prompt=system_prompt)
        analysis: AnalysisResult = analyze(prompt, response, judge_provider=judge_provider)

        results.append(ScanResult(
            category_id=cat["id"],
            category_name=cat.get("name", cat["id"]),
            prompt=prompt,
            response_text=response.text,
            verdict=analysis.verdict.value,
            confidence=analysis.confidence,
            method=analysis.method,
            reasoning=analysis.reasoning,
            model=target_provider.model_name,
        ))

    return results


def results_to_dicts(results: List[ScanResult]) -> List[dict]:
    """Convert results to plain dicts - useful for saving as JSON or feeding the report engine."""
    return [asdict(r) for r in results]