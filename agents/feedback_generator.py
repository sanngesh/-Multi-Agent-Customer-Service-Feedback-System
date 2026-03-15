"""
Agent 2: Feedback Generator
Takes identified problematic statements and generates detailed explanations
and professional alternative statements using GPT-4o.
"""

import json
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert customer service coach providing constructive feedback to a 
colleague at a bank. Your tone should be helpful and professional — never insulting, sarcastic, 
or demeaning about the colleague.

For each problematic statement identified in a customer service chat transcript, you must produce:

1. **Explanation** (1–3 sentences):
   - Clearly state WHY the original statement is problematic.
   - You MUST use category language to characterize the issue. Use one or more of these exact 
     category terms: tone, empathy, clarity, ownership, proactivity, accuracy, compliance, 
     grammar, spelling, professionalism.
   - Be specific about what makes the statement problematic (e.g., "the word 'hmmm' creates an 
     overly informal tone inappropriate for banking support").
   - Do NOT merely restate the original — explain the actual problem.

2. **Alternative** (a replacement statement):
   - Must be substantively different from the original (not just minor word swaps).
   - Must maintain professional banking support tone.
   - Must NOT introduce any new personally identifiable information (PII) not present in the 
     original transcript.
   - Must NOT overpromise outcomes or timelines outside the representative's control (don't 
     guarantee immediate resolution or exact delivery times unless the original case supports it).
   - Should naturally fit the conversation flow given the context.
   - If the original had a grammar/spelling error, the alternative must be grammatically correct.

Return your output as a JSON object with this exact structure:
{
  "case_name": "Case One/Two/Three",
  "feedback_items": [
    {
      "original": "exact quote from transcript",
      "explanation": "1-3 sentence explanation using category language",
      "alternative": "professional replacement statement"
    }
  ]
}
"""


class FeedbackGenerator:
    """LLM-powered agent that generates explanations and alternatives."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model

    def generate(
        self,
        analysis: dict,
        transcript_text: str,
        case_name: str,
        corrections: list | None = None,
    ) -> dict:
        """
        Generate feedback for problematic statements.

        Args:
            analysis: Output from CaseAnalyzer with problematic_statements.
            transcript_text: Full transcript for context.
            case_name: Name of the case.
            corrections: Optional list of corrections from QualityVerifier for a second pass.

        Returns:
            dict with case_name and feedback_items.
        """
        statements_json = json.dumps(analysis.get("problematic_statements", []), indent=2)

        correction_section = ""
        if corrections:
            correction_section = f"""

IMPORTANT — CORRECTIONS FROM QUALITY REVIEW:
The following issues were found in your previous output. Please fix them:
{json.dumps(corrections, indent=2)}
"""

        user_prompt = f"""Generate feedback for the following problematic statements found in 
"{case_name}".

FULL TRANSCRIPT (for context):
---
{transcript_text}
---

PROBLEMATIC STATEMENTS IDENTIFIED:
{statements_json}
{correction_section}
For each statement, provide an explanation (1–3 sentences using category language) and a 
professional alternative. Return as the specified JSON structure."""

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        result = json.loads(response.choices[0].message.content)
        return result
