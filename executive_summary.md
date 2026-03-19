# Executive Summary

## Multi-Agent Customer Service Feedback System

This project delivers an AI-powered multi-agent system that automates the review of customer service live-chat transcripts in a banking context. Using three transcripts between a support representative and customers, the system identifies problematic representative statements, explains why they are problematic, and suggests professional alternatives—compiled into a Word document titled “Case Feedback”.

The solution uses a four-agent Python pipeline powered by OpenAI’s GPT-4o. Agent 1 (Case Analyzer) reviews each transcript across seven quality categories—tone, clarity, empathy, grammar, professionalism, problem resolution, and accuracy—quoting issues verbatim. Agent 2 (Feedback Generator) writes 1–3 sentence explanations using category language and proposes substantively different alternatives. Agent 3 (Evaluation Agent) cross-checks outputs against the transcript with structured validation, scores them on a 100-point rubric, and triggers re-generation if rules are broken or the score falls below 85. Agent 4 (Document Compiler) assembles the verified feedback with bold headings, 1.5 line spacing, and consistent formatting.

Key engineering choices include structured JSON outputs for reliable parsing, temperature tuning per agent role (0.1–0.3), guardrails against new PII and overpromising, and a self-correcting verification loop with up to five retries per case. The pipeline processes all three transcripts and improves output quality through iteration.

The system is evaluated on correctness, completeness, clarity, format, and usefulness. Risks such as hallucination, contextual misinterpretation, compliance issues, and privacy are reduced through automated checks, human review checklists, and prompt constraints. Human oversight remains essential for context, fairness, and final approvals. 

