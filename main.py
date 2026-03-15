"""
Multi-Agent Customer Service Feedback System — Orchestrator

Coordinates the 4-agent pipeline:
  1. Case Analyzer → identifies problematic statements via LLM
  2. Feedback Generator → produces explanations + alternatives via LLM
  3. Quality Verifier → cross-checks accuracy, triggers re-generation if needed
  4. Document Compiler → assembles final Word document

Usage:
    python main.py

Requires:
    - .env file with OPENAI_API_KEY
    - transcripts/ folder with case_one.txt, case_two.txt, case_three.txt
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from agents import CaseAnalyzer, FeedbackGenerator, QualityVerifier, DocumentCompiler

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
OUTPUT_PATH = BASE_DIR / "Case Feedback.docx"
NOTES_LOG_PATH = BASE_DIR / "notes_log.md"
MAX_VERIFICATION_RETRIES = 2
MODEL = "gpt-4o"

CASE_FILES = {
    "Case One": "case_one.txt",
    "Case Two": "case_two.txt",
    "Case Three": "case_three.txt",
}

# ─── Logging Helpers ──────────────────────────────────────────────────────────

log_entries = []


def log(stage: str, message: str, data: dict | None = None):
    """Append a timestamped entry to the notes log."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stage": stage,
        "message": message,
    }
    if data:
        entry["data_summary"] = data
    log_entries.append(entry)
    print(f"  [{stage}] {message}")


def save_notes_log():
    """Write the notes log to a markdown file documenting the full pipeline."""
    with open(NOTES_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("# Notes Log — Multi-Agent Customer Service Feedback System\n\n")
        f.write("This document records the data pipeline, LLM prompts, agent interactions, ")
        f.write("and quality verification steps used to generate `Case Feedback.docx`.\n\n")
        f.write("## System Configuration\n\n")
        f.write(f"- **Model**: `{MODEL}`\n")
        f.write(f"- **Max Verification Retries**: {MAX_VERIFICATION_RETRIES}\n")
        f.write(f"- **Output**: `{OUTPUT_PATH.name}`\n\n")
        f.write("## Pipeline Steps\n\n")

        for i, entry in enumerate(log_entries, 1):
            f.write(f"### Step {i}: {entry['stage']}\n\n")
            f.write(f"**Time**: {entry['timestamp']}\n\n")
            f.write(f"{entry['message']}\n\n")
            if "data_summary" in entry:
                f.write("**Data**:\n")
                f.write(f"```json\n{json.dumps(entry['data_summary'], indent=2, default=str)}\n```\n\n")

    print(f"\n📝 Notes log saved to: {NOTES_LOG_PATH}")


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  Multi-Agent Customer Service Feedback System")
    print("=" * 70)

    # Load environment
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY not found in .env file.")
        print("   Create a .env file with: OPENAI_API_KEY=sk-your-key-here")
        return

    client = OpenAI(api_key=api_key)
    log("Setup", "OpenAI client initialized.", {"model": MODEL})

    # Read transcripts
    transcripts = {}
    for case_name, filename in CASE_FILES.items():
        filepath = TRANSCRIPTS_DIR / filename
        transcripts[case_name] = filepath.read_text(encoding="utf-8")
        log("Data Sourcing", f"Loaded transcript: {filename}", {"chars": len(transcripts[case_name])})

    # Initialize agents
    analyzer = CaseAnalyzer(client, model=MODEL)
    generator = FeedbackGenerator(client, model=MODEL)
    verifier = QualityVerifier(client, model=MODEL)
    compiler = DocumentCompiler()

    log("Setup", "All 4 agents initialized: CaseAnalyzer, FeedbackGenerator, QualityVerifier, DocumentCompiler")

    all_feedback = {}

    for case_name, transcript_text in transcripts.items():
        print(f"\n{'─' * 50}")
        print(f"  Processing: {case_name}")
        print(f"{'─' * 50}")

        # ── Agent 1: Case Analyzer ────────────────────────────────────────
        print(f"\n🔍 Agent 1 (Case Analyzer) analyzing {case_name}...")
        analysis = analyzer.analyze(transcript_text, case_name)
        num_found = len(analysis.get("problematic_statements", []))
        log(
            "Agent 1 — Case Analyzer",
            f"Analyzed {case_name}: identified {num_found} problematic statement(s).",
            {
                "case": case_name,
                "statements_found": num_found,
                "statements": [s.get("statement", "")[:80] for s in analysis.get("problematic_statements", [])],
                "categories_flagged": [s.get("categories", []) for s in analysis.get("problematic_statements", [])],
            },
        )

        # ── Agent 2: Feedback Generator ───────────────────────────────────
        print(f"📝 Agent 2 (Feedback Generator) creating feedback for {case_name}...")
        feedback = generator.generate(analysis, transcript_text, case_name)
        num_items = len(feedback.get("feedback_items", []))
        log(
            "Agent 2 — Feedback Generator",
            f"Generated {num_items} feedback item(s) for {case_name}.",
            {
                "case": case_name,
                "items_generated": num_items,
                "prompt_strategy": "Structured JSON mode with category language requirements",
            },
        )

        # ── Agent 3: Quality Verifier (with retry loop) ──────────────────
        for attempt in range(1, MAX_VERIFICATION_RETRIES + 1):
            print(f"✅ Agent 3 (Quality Verifier) checking {case_name} (attempt {attempt}/{MAX_VERIFICATION_RETRIES})...")
            verification = verifier.verify(feedback, transcript_text, case_name)

            approved = verification.get("approved", False)
            issues = verification.get("issues_found", [])
            missing = verification.get("missing_statements", [])

            log(
                f"Agent 3 — Quality Verifier (Attempt {attempt})",
                f"{case_name}: {'✅ APPROVED' if approved else '❌ NEEDS REVISION'} — "
                f"{len(issues)} issue(s), {len(missing)} missing statement(s).",
                {
                    "case": case_name,
                    "approved": approved,
                    "quality": verification.get("overall_quality", "unknown"),
                    "issues_count": len(issues),
                    "missing_count": len(missing),
                    "issues_summary": [i.get("description", "")[:100] for i in issues],
                },
            )

            if approved or attempt == MAX_VERIFICATION_RETRIES:
                if not approved:
                    print(f"   ⚠️  Max retries reached for {case_name}. Using best available output.")
                    log(
                        "Agent 3 — Quality Verifier",
                        f"Max retries reached for {case_name}. Proceeding with current output.",
                    )
                break

            # Re-generate with corrections
            print(f"   🔄 Re-generating feedback for {case_name} with corrections...")
            corrections = issues + [{"issue_type": "missing", "description": m.get("reason", ""), "suggested_fix": f"Add feedback for: {m.get('statement', '')}"} for m in missing]

            feedback = generator.generate(
                analysis, transcript_text, case_name, corrections=corrections
            )
            log(
                "Agent 2 — Feedback Generator (Revision)",
                f"Re-generated feedback for {case_name} with {len(corrections)} correction(s).",
                {"corrections_applied": len(corrections)},
            )

        all_feedback[case_name] = feedback.get("feedback_items", [])

    # ── Agent 4: Document Compiler ────────────────────────────────────────
    print(f"\n{'─' * 50}")
    print("  📄 Agent 4 (Document Compiler) building Word document...")
    print(f"{'─' * 50}")

    output_file = compiler.compile(all_feedback, str(OUTPUT_PATH))
    total_items = sum(len(items) for items in all_feedback.values())
    log(
        "Agent 4 — Document Compiler",
        f"Compiled {total_items} feedback items into {OUTPUT_PATH.name}.",
        {"output_file": str(OUTPUT_PATH), "total_items": total_items},
    )

    # Save notes log
    save_notes_log()

    print(f"\n{'=' * 70}")
    print(f"  ✅ Done! Output saved to: {OUTPUT_PATH}")
    print(f"  📝 Notes log saved to: {NOTES_LOG_PATH}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
