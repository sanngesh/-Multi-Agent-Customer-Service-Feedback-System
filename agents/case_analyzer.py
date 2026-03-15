"""
Agent 1: Case Analyzer
Performs deep multi-dimensional analysis of customer service chat transcripts
using GPT-4o to identify problematic representative statements.
"""

import json
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert customer service quality analyst. Your job is to analyze 
live chat transcripts between a bank's customer service representative ("Support") and a customer.

You must identify ONLY the representative's (Support's) statements that are problematic based on 
these live chat etiquette best practices:

1. **Tone** — Messages should be friendly, polite, and positive but NOT overly informal, cutesy, or 
   unprofessional (no GIFs, emoticons, excessive exclamation marks, or slang in banking context).
2. **Clarity** — Questions and statements should be unambiguous. Avoid vague or confusing wording.
3. **Empathy** — Show genuine empathy but avoid being performative, overly dramatic, or patronizing. 
   Don't express personal relief or emotions about the customer's situation.
4. **Grammar & Spelling** — All messages must be grammatically correct with proper spelling. 
   Typos reflect poorly on the business.
5. **Professionalism** — Maintain professional standards for banking support. No text emoticons, 
   gender assumptions, or overly casual language.
6. **Problem Resolution** — Don't close conversations prematurely. Focus on solving the customer's 
   issue. Don't deflect or shut down without offering solutions.
7. **Accuracy** — Don't misidentify customer intent. Don't misapply policies. Don't make incorrect 
   assumptions about what the customer is saying.

IMPORTANT RULES:
- Only flag statements made by "Support" (the representative), NEVER customer statements.
- Quote each problematic statement EXACTLY as it appears in the transcript (preserve typos, casing, 
  punctuation, emoticons).
- For each statement, identify ALL applicable categories from the list above.
- Include the surrounding conversation context (the customer message before and after, if available).

Return your analysis as a JSON object with this exact structure:
{
  "case_name": "Case One/Two/Three",
  "problematic_statements": [
    {
      "statement": "exact quote from transcript",
      "categories": ["tone", "clarity"],
      "context_before": "customer message before this statement",
      "context_after": "customer message after this statement",
      "severity": "high/medium/low"
    }
  ]
}
"""


class CaseAnalyzer:
    """LLM-powered agent that performs deep analysis of chat transcripts."""

    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model

    def analyze(self, transcript_text: str, case_name: str) -> dict:
        """
        Analyze a single transcript and return identified problematic statements.

        Args:
            transcript_text: Raw text of the chat transcript.
            case_name: Name of the case (e.g., "Case One").

        Returns:
            dict with case_name and list of problematic_statements.
        """
        user_prompt = f"""Analyze the following customer service chat transcript for "{case_name}".
Identify ALL problematic statements made by the representative (Support lines only).

TRANSCRIPT:
---
{transcript_text}
---

Return your analysis as the specified JSON structure. Be thorough — check every single Support 
line for issues across all 7 categories (tone, clarity, empathy, grammar & spelling, 
professionalism, problem resolution, accuracy). Even seemingly minor issues like a slightly 
informal "hmmm" or an ambiguous question should be flagged."""

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        result = json.loads(response.choices[0].message.content)
        return result
