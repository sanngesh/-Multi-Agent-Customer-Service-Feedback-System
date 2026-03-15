"""
Agent 3: Quality Verifier
Cross-checks the Feedback Generator's output against the original transcripts
and quality standards using GPT-4o. Implements a feedback loop.
"""

import json
from openai import OpenAI

SYSTEM_PROMPT = """You are a strict quality assurance reviewer for customer service feedback 
documents at a bank. Your job is to verify that feedback about a representative's chat 
performance meets all quality standards.

For each feedback item, verify ALL of the following:

1. **Transcript Accuracy**: The "original" statement must appear EXACTLY in the transcript as a 
   "Support:" line. Check character-by-character including typos, punctuation, and casing.

2. **Explanation Quality**:
   - Must be 1–3 sentences (count them).
   - Must use at least one category term: tone, empathy, clarity, ownership, proactivity, 
     accuracy, compliance, grammar, spelling, professionalism.
   - Must explain WHY the statement is problematic, not merely restate it.
   - Must identify at least one concrete reason (e.g., "overly informal", "gender-assumptive").

3. **Alternative Quality**:
   - Must be substantively different from the original (not just minor rewording).
   - Must NOT introduce new PII not in the original transcript.
   - Must NOT overpromise outcomes or timelines outside the representative's control.
   - Must be grammatically correct.
   - Must maintain professional banking support tone.

4. **Completeness**: Check if any obviously problematic Support statements were missed.

5. **Tone of Feedback**: Must not contain insulting, sarcastic, or demeaning language about 
   the colleague.

Return your verification as a JSON object:
{
  "approved": true/false,
  "overall_quality": "excellent/good/needs_revision",
  "items_reviewed": 5,
  "issues_found": [
    {
      "item_index": 0,
      "issue_type": "transcript_accuracy/explanation_quality/alternative_quality/completeness/tone",
      "description": "what's wrong",
      "suggested_fix": "how to fix it"
    }
  ],
  "missing_statements": [
    {
      "statement": "Support statement that should have been flagged",
      "reason": "why it should be flagged"
    }
  ]
}

If everything is correct, set "approved" to true and leave issues_found and missing_statements 
as empty arrays.
"""


class QualityVerifier:
    """LLM-powered agent that validates feedback quality."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model

    def verify(self, feedback: dict, transcript_text: str, case_name: str) -> dict:
        """
        Verify the quality of generated feedback against the transcript.

        Args:
            feedback: Output from FeedbackGenerator with feedback_items.
            transcript_text: Original transcript for cross-reference.
            case_name: Name of the case.

        Returns:
            dict with approved status, issues found, and missing statements.
        """
        feedback_json = json.dumps(feedback.get("feedback_items", []), indent=2)

        user_prompt = f"""Verify the following feedback for "{case_name}" against the original 
transcript.

ORIGINAL TRANSCRIPT:
---
{transcript_text}
---

FEEDBACK TO VERIFY:
{feedback_json}

Check every item against all 5 verification criteria. Be thorough but fair. 
Return your verification as the specified JSON structure."""

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        result = json.loads(response.choices[0].message.content)
        return result
