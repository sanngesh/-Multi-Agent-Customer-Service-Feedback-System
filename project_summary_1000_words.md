# Multi-Agent Customer Service Feedback System — Project Summary

## 1. Introduction and Problem Statement

This project addresses a challenge faced by customer service managers in the banking sector: reviewing live chat transcripts and providing structured, constructive feedback to representatives. Manually reading through transcripts, identifying problematic statements, writing explanations, and suggesting improvements are all time-consuming and prone to inconsistency. The objective was to build a multi-agent AI system that automates this entire workflow, from transcript analysis to the production of a professionally formatted Word document. All while maintaining the quality and nuance that a human reviewer would provide.

The system processes three customer service chat transcripts (Case One, Case Two, and Case Three), each containing an exchange between a bank’s support representative and a customer. The final deliverable is a Word document titled “Case Feedback,” formatted with bolded section headings, 1.5-line spacing, and a length under five pages, suitable for a peer audience within a banking organisation.


## 2. System Architecture and Data Pipeline

The solution employs a four-agent pipeline orchestrated by a central controller (main.py). Each agent is a specialised Python class with a well-defined responsibility. 

The pipeline flows as follows: Raw Transcript → Agent 1 (Case Analyzer) → Agent 2 (Feedback Generator) → Agent 3 (Evaluation Agent, with retry loop back to Agent 2 if verification fails) → Agent 4 (Document Compiler) → Case Feedback.docx.

Agent 1 — Case Analyzer reads raw chat transcripts and identifies problematic statements made by the customer service representative.

Agent 2 — Feedback Generator takes the flagged statements and generates constructive, professional feedback.

Agent 3 — Evaluation Agent verifies Agent 2’s output against an evaluation rubric.

Agent 4 — Document Compiler uses python-docx to compile the approved JSON feedback into Case Feedback.docx.

Refer to the README.md file for the full explanation on each agent.

## 3. Prompt Engineering and Chain-of-Thought Strategy

The prompts employ several deliberate engineering techniques. First, each system prompt assigns the model a specific expert persona (quality analyst, coach, QA reviewer) to anchor its behaviour. Second, all prompts use structured JSON output mode (`response_format: json_object`) with explicit schema definitions, eliminating parsing ambiguity. Third, the Case Analyzer prompt uses chain-of-thought reasoning by requiring the model to assess every Support line against all seven categories, ensuring thoroughness rather than surface-level analysis. Fourth, the negative constraints in the Feedback Generator prompt: “must NOT introduce PII” and “must NOT overpromise”, serve as guardrails against common LLM failure modes. Finally, temperature tuning across agents (0.2 for analysis, 0.3 for generation, 0.1 for verification) reflects the different cognitive demands of each task.

## 4. Notes Log and Data Pipeline Documentation

The system generates a `notes_log.md` file documenting every pipeline step with timestamps, data summaries, and agent interactions. The run log from the executed pipeline reveals the self-correcting loop in action: Despite reaching the maximum retry limit for all three cases, the verification loop demonstrated an improved output quality at each iteration through reducing issue counts and eliminating missing statements.

Refer to the notes_log.md for the full data pipeline, prompts, edits, and human review.


## 5. Evaluation Plan

An evaluation plan was made that includes a structured rubric and methodology for assessing the quality of the Case Feedback.docx deliverable. 

The rubric is structured as follows:
1. Correctness (25points)
2. Completeness (20 points)
3. Clarity (15 points)
4. Format (20 points)
5. Usefulness (20 points)

Refer to the README.md file for the complete rubric explanations.  


## 6. Reflection: What Worked and What Struggled

The multi-agent architecture isolated specific tasks, so each component could be tested independently. By using Pydantic to enforce structured JSON, the system avoided parsing failures. The Document Compiler, which does not rely on an LLM, kept formatting consistent across every run. The verification loop also caught concrete errors, including misquoted statements and false attributions, that a single-pass approach would likely miss. Despite this, performance plateaued; none of the three cases surpassed 85 points, scoring 80, 77, and 80. This suggests the loop can fix surface-level inaccuracies but cannot bypass deeper generation constraints.

A bottleneck emerged when Agent 3 kept requesting more empathetic wording that Agent 2 could not produce. This cycle continued until the retry limit, highlighting a limitation in LLM self-correction, where the evaluator’s expectations outpace what the generator can deliver. The system also lacked company-specific knowledge a human reviewer would bring, such as checking quotes against transcripts and judging alternatives against internal standards.


## 7. Ethical, Legal, and Data-Quality Risks

Four risks were addressed. First, LLMs can fabricate statements not in the transcript, so Agent 3 checks every quote word-for-word against the source. Second, tone is difficult for an LLM to judge, so human review checklists serve as a backup. Third, if this feedback were used in HR decisions, it could raise fairness concerns; the system is therefore positioned as an assistive tool where outputs need human approval. Finally, because transcripts are sent to the OpenAI API, a PII redaction layer filters sensitive information before data leaves the local environment.

## 8. Potential Next Steps

Several practical improvements came out of the problems observed during development. The most impactful would be RAG knowledge base built from a bank’s internal policy documents, escalation protocols, and tone guidelines, so feedback reflects how that specific organisation actually operates rather than relying on generic LLM knowledge. Separately, a dedicated PII redaction or anonymisation step before any data reaches the OpenAI API would strengthen the current privacy safeguards for production use. The verification loop’s score plateau (77–80 across all cases) also points to a clear fix: providing Agent 2 with few-shot examples of high-scoring feedback so it has something concrete to work from, rather than regenerating blindly from correction notes alone. On the operational side, logging token usage, latency, and retry costs per agent per case would make optimisation decisions evidence-based rather than guesswork. Finally, the Quality Verifier’s prompts need better handling of edge cases, particularly recognising when a representative’s apology is contextually appropriate rather than flagging it as overly deferential.

Collectively, these improvements would strengthen the system’s readiness for real-world deployment while maintaining alignment with organisational requirements.

