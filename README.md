#  LLM Red-Teaming Tool

A Python-based security scanner that automatically tests whether an LLM-powered chatbot can be manipulated into bypassing its own safety rules — and measures how much a custom system prompt actually helps.

##  The Problem This Solves
Most companies don't build AI models from scratch. They take an off-the-shelf model (GPT, Llama, etc.) and add a custom system prompt on top:

> "You are a banking assistant. Never share customer data. Decline any off-topic requests."

The question nobody answers systematically: **does that system prompt actually hold up under attack, or is it just words?**
This tool measures that — with empirical, real-world data.

---

##  Key Findings

Tested on `llama-3.1-8b-instant` using 100 attack prompts from the **JailbreakBench benchmark (NeurIPS 2024)**:

| Scenario | System Prompt | Pass Rate | FAIL Count |
| :--- | :--- | :--- | :--- |
| **A — Baseline** | None | **83%** | 6 |
| **B — Weak** | One generic sentence | **92%** | 3 |
| **C — Hardened** | Detailed, explicit rules | **92%** | 1 |

### 📊 Security Insights:
* **Immediate ROI:** Even a single-sentence system prompt raised resilience by **+9%**.
* **Behavioral Constraints Matter:** Detailed, explicit instructions cut the remaining FAIL count in half again.
* **The Vulnerable Link:** The **"Expert Advice"** category was consistently the weakest across all three scenarios. Framing a harmful request as a professional consultation bypasses safety rules far more reliably than direct malicious requests.

---

##  Architecture & Project Structure

```text
llm-redteam-tool/
├── main.py                        # CLI entry point
├── config.py                      # Centralized settings (reads from .env)
├── providers/
│   ├── base.py                    # Abstract interface — any provider must implement this
│   ├── llm_provider.py            # API-based provider (Groq, OpenAI, or compatible)
│   └── browser_provider.py        # Browser-based provider (Playwright for web widgets)
├── core/
│   ├── analyzer.py                # Verdict logic: PASS / FAIL / NEEDS_REVIEW / ERROR
│   ├── scanner.py                 # Orchestrator: runs all prompts, collects results
│   └── report.py                  # HTML report generator
├── templates/
│   └── report_template.html       # Report template (dark terminal aesthetic)
├── data/
│   └── attack_prompts.json        # 100 attack prompts across 10 categories (auto-generated)
├── scripts/
│   └── prepare_dataset.py         # Downloads JBB-Behaviors from Hugging Face
└── prompts/                       # Custom system prompt files for comparison testing
    ├── weak_assistant.txt
    └── hardened_assistant.txt
---

## 🚀 Quickstart

### 1. Clone & setup
```bash
git clone https://github.com/aliaadwan/llm-redteam-tool.git
cd llm-redteam-tool
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configure
```bash
copy .env.example .env
# Open .env and add your Groq API key (free at console.groq.com)
```

### 3. Download the dataset
```bash
python scripts/prepare_dataset.py
```

### 4. Run a scan
```bash
# Full scan → generates reports/report.html
python main.py

# Quick test (1 prompt per category)
python main.py --limit 1

# Test a custom system prompt
python main.py --system-prompt-file prompts/hardened_assistant.txt

# Enable LLM-as-Judge for ambiguous verdicts
python main.py --judge
```

---

##  Tech Stack

`Python` · `Groq API` · `OpenAI SDK` · `Playwright` · `Jinja2` · `Hugging Face Datasets` · `tqdm`

---

##  Dataset

Attack prompts sourced from **JBB-Behaviors** (JailbreakBench, NeurIPS 2024, MIT License):

> Chao et al., *"JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models"*, NeurIPS 2024.

---

##  Responsible Use

This tool is for **educational and authorized security testing only**.

|  Allowed |  Not Allowed |
|---|---|
| Testing your own LLM application | Testing any system without permission |
| Authorized client security audits | Automated attacks on public services |
| Academic research & learning | Violating a platform's Terms of Service |
