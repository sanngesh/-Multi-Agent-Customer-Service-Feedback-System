# Multi-Agent Customer Service Feedback System — Project Summary

## 1. Introduction and Problem Statement

This project addresses a practical challenge faced by customer service managers in the banking sector: reviewing live chat transcripts and providing structured, constructive feedback to representatives. Manually reading through transcripts, identifying problematic statements, writing explanations, and suggesting improvements is time-consuming and prone to inconsistency. The objective was to build a multi-agent AI system that automates this entire workflow — from transcript analysis to the production of a professionally formatted Word document — while maintaining the quality and nuance that a human reviewer would provide.

The system processes three customer service chat transcripts (Case One, Case Two, and Case Three), each containing an exchange between a bank's support representative and a customer. The final deliverable is a Word document titled "Case Feedback," formatted with bolded section headings, 1.5 line spacing, and a length under five pages, suitable for a peer audience within a banking organisation.

## 2. System Architecture and Data Pipeline

The solution employs a four-agent pipeline orchestrated by a central controller (`main.py`). Each agent is a specialised Python class with a well-defined responsibility:

**Agent 1 — Case Analyzer** ingests the raw transcript text and uses GPT-4o with a carefully engineered system prompt to identify problematic statements made exclusively by the representative. The prompt defines seven evaluation categories: tone, clarity, empathy, grammar and spelling, professionalism, problem resolution, and accuracy. The model is instructed to quote statements verbatim — preserving typos, emoticons, and casing — and to return structured JSON. A low temperature of 0.2 ensures deterministic, focused output.

**Agent 2 — Feedback Generator** receives the analysis output along with the full transcript for context. It generates, for each flagged statement, a one-to-three-sentence explanation using category language (e.g., "tone," "empathy," "professionalism") and a substantively different professional alternative. The prompt explicitly prohibits introducing new personally identifiable information (PII) or overpromising outcomes. Temperature is set to 0.3 to balance creativity with consistency. When corrections are supplied from the quality verification loop, they are injected into the prompt as an additional "CORRECTIONS FROM QUALITY REVIEW" section, enabling the model to address specific deficiencies.

**Agent 3 — Quality Verifier** acts as a strict quality assurance reviewer. It cross-checks every feedback item against the original transcript, verifying transcript accuracy (character-by-character match), explanation quality (sentence count, category terms, substantive reasoning), alternative quality (PII check, overpromise check, grammatical correctness), and completeness (whether any obviously problematic statements were missed). The temperature is set to 0.1 for maximum precision. If verification fails, the pipeline loops back to Agent 2 with the verifier's specific corrections — up to a maximum of two attempts per case — creating a self-correcting feedback mechanism.

**Agent 4 — Document Compiler** is a deterministic, non-LLM agent built with `python-docx`. It assembles verified feedback into a Word document with the exact formatting specifications: centred title, bold case headings, bulleted feedback items with bold labels ("Original Statement," "Explanation," "Alternative"), Calibri 11pt font, 1.5 line spacing throughout, and optimised margins to stay under five pages.

## 3. Prompt Engineering and Chain-of-Thought Strategy

The prompts employ several deliberate engineering techniques. First, each system prompt assigns the model a specific expert persona (quality analyst, coach, QA reviewer) to anchor its behaviour. Second, all prompts use structured JSON output mode (`response_format: json_object`) with explicit schema definitions, eliminating parsing ambiguity. Third, the Case Analyzer prompt uses chain-of-thought reasoning by requiring the model to assess every Support line against all seven categories, ensuring thoroughness rather than surface-level analysis. Fourth, the negative constraints in the Feedback Generator prompt — "must NOT introduce PII," "must NOT overpromise" — serve as guardrails against common LLM failure modes. Finally, temperature tuning across agents (0.2 for analysis, 0.3 for generation, 0.1 for verification) reflects the different cognitive demands of each task.

## 4. Notes Log and Data Pipeline Documentation

The system generates a comprehensive `notes_log.md` file documenting every pipeline step with timestamps, data summaries, and agent interactions. The run log from the executed pipeline reveals the self-correcting loop in action: Case One required revision twice (transcript accuracy issues and a false attribution of a customer statement), Case Two underwent two passes (an alternative that introduced an unsolicited apology and an extraneous statement), and Case Three was revised twice (missed spelling error "depsoit" and insufficient differentiation in alternatives). Despite reaching the maximum retry limit for all three cases, the verification loop demonstrably improved output quality at each iteration — reducing issue counts from 3 to 2 for Case Three, and eliminating missing statements for Case Two by the second pass.

## 5. Evaluation Plan

The evaluation framework uses a five-dimension rubric totalling 100 points: Correctness (25 points) covers verbatim transcript matching, accurate issue identification, and appropriate alternatives; Completeness (20 points) ensures all three cases are covered with sufficient depth and category language; Clarity (15 points) assesses whether explanations are concise and alternatives read naturally; Format (20 points) verifies the .docx format, title, bold headings, spacing, and page count; and Usefulness (20 points) evaluates actionability, professional tone, and audience appropriateness. The rubric is supported by both automated checks (performed by Agent 3 during generation) and a manual review checklist for human validation.

## 6. Reflection: What Worked and What Struggled

**What worked well.** The multi-agent architecture created clear separation of concerns, making each component independently testable and debuggable. The verification-and-retry loop caught genuine errors — misquoted statements, false attributions, and missing spelling corrections — that a single-pass system would have missed.  The structured JSON output mode eliminated parsing failures entirely. The Document Compiler, being deterministic, produced consistent formatting every time.

**Where the AI struggled.** The Quality Verifier was sometimes overly strict, flagging reasonable alternatives as "not substantively different" or objecting to apologies that were contextually appropriate. This perfectionism meant no case achieved full approval — all three hit the maximum retry limit. Additionally, the Case Analyzer occasionally flagged statements that were borderline rather than clearly problematic, and in one instance attributed a customer's statement to the representative. The system also lacks the ability to understand organisational-specific policies or cultural norms that a human reviewer would implicitly apply.

**How a real professional would validate.** A human quality manager would cross-reference quoted statements against the original transcripts, assess whether alternatives would realistically fit the conversation flow, and evaluate whether the feedback tone is genuinely constructive. They would also apply institutional knowledge — specific company policies, escalation protocols, and service-level expectations — that the AI cannot access.

## 7. Ethical, Legal, and Data-Quality Risks

**Hallucination risk.** LLMs may fabricate statements not present in the transcript or misattribute customer statements to the representative. The verbatim-matching requirement in the Quality Verifier mitigates but does not eliminate this risk.

**Misinterpretation of context.** The AI may misjudge tone or intent — for example, flagging a representative's genuine attempt at empathy as "patronising." Cultural and situational context that a human reviewer would naturally understand may be lost.

**Compliance risk.** If used in formal HR processes, AI-generated feedback could raise fairness and bias concerns. The system should never be used as the sole basis for disciplinary action without human review.

**Data provenance.** The transcripts are processed by OpenAI's API, raising data residency and privacy considerations. In a production environment, PII redaction should occur before any data is sent to external APIs.

**Mitigation strategies.** These risks are partially addressed by the verification loop, the mandatory human review checklist in the evaluation plan, and the explicit PII and overpromise guardrails in the prompts. For production deployment, additional safeguards would include PII redaction pipelines, audit logging, bias testing across demographic groups, and a mandatory human-in-the-loop approval step before any feedback reaches the intended recipient.
