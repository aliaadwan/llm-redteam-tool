import json
from pathlib import Path
from datasets import load_dataset


def slugify(text: str) -> str:
    return text.lower().replace("/", "_").replace(" ", "_")


def main():
    print("Downloading JBB-Behaviors from Hugging Face...")
    ds = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
    harmful = ds["harmful"]  # 100 rows

    grouped = {}
    for row in harmful:
        grouped.setdefault(row["Category"], []).append(row["Goal"])

    categories = [
        {
            "id": slugify(cat),
            "name": cat,
            "description": f"'{cat}' category from OpenAI's usage policy",
            "prompts": prompts,
        }
        for cat, prompts in grouped.items()
    ]

    output = {
        "_notes": (
            "Source: JBB-Behaviors dataset (JailbreakBench, NeurIPS 2024, MIT License). "
            "For educational/research use only, on systems you are authorized to test. "
            "Citation: Chao et al., 'JailbreakBench: An Open Robustness Benchmark "
            "for Jailbreaking LLMs', NeurIPS 2024."
        ),
        "categories": categories,
    }

    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "data" / "attack_prompts.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(c["prompts"]) for c in categories)
    print(f"Saved: {len(categories)} categories, {total} prompts, to {output_path}")


if __name__ == "__main__":
    main()