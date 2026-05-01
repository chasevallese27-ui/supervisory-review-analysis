# Statistical Guardrails

Loaded by the skill before writing the narrative. These rules prevent overclaiming.

## Sample-size rules

Apply **per work item type (per sheet)**. An analyst may have plenty of data on one sheet and almost none on another — the narrative should respect the difference.

- **Fewer than 20 parameter evaluations for an analyst on a given work type:** report the numbers in the table, but do **not** characterize their performance in the narrative for that work type. Use the neutral phrase "insufficient sample for period."
- **Fewer than 5 evaluations:** exclude from the narrative entirely for that work type. Show in a separate "Low Volume" note.
- **A sheet has fewer than 50 total evaluations for the period:** do not produce narrative highlights for that sheet. Report the tables and recommend the user widen the period.

## Period-over-period rules

- Report rate changes only when both periods have n ≥ 20 for the analyst.
- Use the term "change" — not "improvement" or "decline" — unless the change is large (>5 percentage points) AND both periods have n ≥ 30. Small shifts in small samples are noise.
- Never attribute causation. "Error rate rose from 9.3% to 13.5%" is acceptable. "The new process caused errors to rise" is not.

## Risk Level (Alerts) rules

- Report the breakdown table whenever Alerts is included.
- Highlight in the narrative *only* when there is a meaningful inversion or pattern (e.g., higher error rate on low-risk than high-risk alerts, or vice versa).
- Frame as observation, not conclusion. "Error rate is highest on Risk Level 1 alerts (X%) and lowest on Risk Level 3 (Y%) — worth investigating" is appropriate. "Analysts are not paying attention to low-risk alerts" is not.
- If any Risk Level has n < 10 evaluations, note it as low confidence.

## Language guardrails

- Never use "worst," "best," or rank-order language for individual analysts in the narrative.
- Avoid "struggling," "underperforming," or evaluative adjectives. Stick to rates, counts, and comparisons to the team or sheet average.
- Reviewer-coverage imbalance is reported as an observation, not an allegation. "Reviewer X covered N% of Analyst Y's reviews on this work type" — no interpretation.

## What to include in the narrative

- Overall stats per work type for the period
- Top error-driving parameters per work type
- Per-analyst error rates as a **table**, with sample-size caveats in a footnote
- Risk Level callout for Alerts when meaningful
- Period-over-period movement (if requested) where samples are adequate
- Cross-work-type observations if a pattern repeats across sheets

## What to leave out

- Personnel recommendations ("consider retraining X")
- Rankings ("Top performer: Y")
- Predictions ("at this rate, Z will...")
- Causal claims without supporting evidence the file contains
