# Evaluation Plan — Multi-Agent Customer Service Feedback System

## Overview

This evaluation plan provides a structured rubric and methodology for assessing the quality of the `Case Feedback.docx` deliverable produced by the multi-agent system.

---

## Evaluation Rubric

### 1. Correctness (25 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Quoted originals match transcript | 5 | Every "Original Statement" cited in the document must appear verbatim in the corresponding case transcript as a representative (Support) line |
| Explanations identify real issues | 5 | Each explanation must correctly identify why the statement is problematic — not merely restate the original |
| Alternatives are appropriate | 5 | Alternatives must fix the identified issue without introducing new PII, overpromising, or creating new problems |
| No false attributions | 5 | No customer statements should be flagged as representative statements |
| Key statements identified | 5 | All obviously problematic statements from each case are captured (no significant omissions) |

### 2. Completeness (20 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| All three cases covered | 6 | Document contains feedback sections for Case One, Case Two, and Case Three |
| Three components per item | 6 | Every feedback item includes all three parts: Original Statement, Explanation, and Alternative |
| Sufficient coverage per case | 4 | Each case has at least 3 problematic statements identified |
| Category language used | 4 | Explanations use category terms (tone, empathy, clarity, grammar, professionalism, etc.) |

### 3. Clarity (15 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Explanations are clear | 5 | Explanations are easy to understand and directly address the issue |
| Explanations are concise | 5 | Each explanation is 1–3 sentences (not overly verbose) |
| Alternatives read naturally | 5 | Alternative statements fit naturally in the conversation context |

### 4. Format (20 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Word .docx format | 3 | Deliverable is a single .docx file |
| Title is "Case Feedback" | 3 | Document title/heading is exactly "Case Feedback" |
| Bold section headings | 3 | "Case One", "Case Two", "Case Three" appear in bold |
| 1.5 line spacing | 3 | All body text uses 1.5 line spacing |
| Under 5 pages | 3 | Total document length is less than 5 pages |
| Bulleted/numbered lists | 3 | Feedback items are presented as lists, not plain paragraphs |
| Bold labels | 2 | Original/Explanation/Alternative labels are visually distinguished with bold formatting |

### 5. Usefulness (20 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Actionable feedback | 5 | Feedback gives the colleague specific, actionable guidance on how to improve |
| Professional tone | 5 | No insulting, sarcastic, or demeaning language about the colleague |
| Alternatives are substantively different | 5 | Each alternative is meaningfully different from its original (not just minor word swaps) |
| Suitable for intended audience | 5 | Content is written for a peer within a banking organization — appropriate level of detail and professionalism |

---

## Total: 100 Points

| Category | Max Points |
|----------|-----------|
| Correctness | 25 |
| Completeness | 20 |
| Clarity | 15 |
| Format | 20 |
| Usefulness | 20 |
| **Total** | **100** |

---

## Evaluation Methodology

### Automated Checks
The pipeline's Quality Verifier agent (Agent 3) performs automated checks during generation:
- Transcript accuracy (exact matching of quoted statements)
- Explanation quality (sentence count, category language usage)
- Alternative quality (PII check, overpromising check, substantive difference)
- Completeness (missing statements detection)

### Manual Review Checklist
After generation, the human reviewer should verify:
1. Open `Case Feedback.docx` in Microsoft Word
2. Check page count (must be < 5 pages)
3. Verify 1.5 line spacing visually
4. Confirm all three sections have bold headings
5. Read each feedback item for accuracy and helpfulness
6. Cross-reference 2–3 quoted originals against the transcripts
7. Assess overall tone — constructive and professional, not condescending
