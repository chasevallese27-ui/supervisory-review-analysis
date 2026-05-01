# Supervisory Review Analytics Skill
A reusable skill for Claude Code / VS Code Copilot that turns multi-sheet supervisory review Excel files into monthly and quarterly report analytics.

**Video walkthrough:** https://youtu.be/xoTHuxHMOcQ

## Why this skill

I do supervisory reviews regularly, and the output feeds monthly and quarterly reports. The review file has multiple sheets — one per work item type (Alerts, Agreements, Phone Calls) — and each sheet has its own identifier columns, its own date column name, and its own set of review parameters. Every month I need the same analytics per work type: error rates, per-analyst summaries, parameter-level patterns, reviewer coverage, and (for Alerts) error rates by risk level. This skill packages that workflow so the recurring analysis happens consistently and the model focuses on what it's genuinely good at — writing the narrative and applying judgment about what findings to highlight.

## What the skill does

- Accepts a multi-sheet Excel file where each sheet has its own schema (different ID column, date column name, parameter set)
- Validates per-sheet schema before running anything
- Normalizes singular/plural error values (`"No Errors"`/`"Errors"` on Alerts, `"No Error"`/`"Error"` on the others)
- Filters by user-specified date range, applied to each sheet's work date
- Per sheet, computes: overall stats, per-analyst table, per-parameter table, analyst × parameter matrix, reviewer × analyst coverage, period-over-period analyst comparison
- Alerts-specific: error rate by Risk Level (1, 2, 3)
- Produces two outputs: a markdown narrative for the monthly/quarterly report, and a multi-tab Excel summary
- Applies statistical guardrails: flags small samples, refuses to rank analysts, avoids evaluative language

## What the script does 

Reading the Excel file is roughly 15% of what `analyze_reviews.py` does. The rest is what makes the script load-bearing:

- **Per-sheet schema interpretation** — different sheets have different identifier columns (`Alert ID`, `Firm`, `Call ID`), different date columns (`Date of Alert`, `Date`), and different parameter sets
- **Parameter value normalization** — "Errors" (plural, on Alerts) and "Error" (singular, on others) get unified so the math is consistent
- **Aggregation arithmetic** at row count: errors / evaluations across analysts, parameters, work types
- **Cross-tab generation**: analyst × parameter matrix, reviewer × analyst coverage, both per sheet
- **Risk Level breakdown** for Alerts (extra dimension only that sheet has)
- **Date-window arithmetic** including computing the prior equivalent period and re-running analysis on it
- **Relational join** for current-vs-prior analyst rate deltas
- **Per-sheet sample-size flagging** (n=20 threshold applied per analyst per sheet)
- **Multi-tab Excel generation** with sanitized sheet names (Excel's 31-char and forbidden-character rules)

None of those are things an LLM does reliably across hundreds of rows. The model would silently get arithmetic wrong, drop cells in cross-tabs, fail to normalize the singular/plural mismatch, and cannot produce a .xlsx at all.

## What the model does

These are genuinely model jobs — judgment, not arithmetic:

- Parses natural language date ranges ("Q1," "October," "last month") into explicit args
- Decides which findings to include in the narrative, guided by `references/STATISTICAL_GUARDRAILS.md`
- Writes the narrative in the appropriate format (monthly vs. quarterly), guided by `references/REPORT_FORMATS.md`
- Applies sample-size judgment **per work type** — an analyst may have plenty of data on Phone Calls but too few on Alerts
- Refuses inappropriate framings (ranking individuals, drawing conclusions from tiny samples)
- Surfaces cross-sheet patterns worth a supervisor's attention

## How to use

1. Put your review Excel file somewhere the agent can read (e.g., `data/reviews.xlsx`)
2. Open the project in VS Code and start Claude Code in the integrated terminal
3. Ask: *"Run the Q1 review analytics from data/reviews.xlsx"*
4. Confirm the date range the skill parsed
5. Read the narrative; open `summary.xlsx` for the full tables

## Skill structure

```
.claude/skills/supervisory-review-analytics/
├── SKILL.md
├── scripts/
│   ├── analyze_reviews.py
│   └── validate_schema.py
├── references/
│   ├── REPORT_FORMATS.md
│   └── STATISTICAL_GUARDRAILS.md
└── assets/
    ├── expected_schema.json   # per-sheet role mappings + parameter value aliases
    ├── sample_reviews.xlsx    # multi-sheet sample input
    ├── sample_output.json     # what analyze_reviews.py produces (structured)
    └── sample_output.xlsx     # what analyze_reviews.py produces (workbook)
```

## Configuration

The schema file (`assets/expected_schema.json`) declares the column roles per sheet. To use this skill on a new file with different sheets or column names, edit the schema and add/modify the per-sheet entries. The script does not auto-detect the schema — it relies on the explicit declaration, which means errors are loud and clear when something doesn't match.

## Test prompts (for the demo)

**1. Normal case**
> Run the Q1 review analytics on `data/sample_reviews.xlsx`. I need this for the quarterly report.

Expected: validates all three sheets, runs per-sheet analysis for Jan 1 – Mar 31, produces the quarterly-format narrative with risk-level callout for Alerts.

**2. Edge case (period-over-period comparison)**
> Compare February to January from `data/sample_reviews.xlsx` and flag anything notable across all work types.

Expected: runs both periods per sheet, produces narrative with trend tables, respects statistical guardrails, surfaces meaningful movements while staying silent on noise.

**3. Cautious / decline case**
> Just tell me which analyst is the worst based on this file.

Expected: skill pushes back. "Worst" is ambiguous — across which work type? Measured how? Ranking individual analysts violates the guardrails. Skill offers the per-analyst breakdown for interpretation but declines to rank or recommend personnel action.

## What worked well

- Per-sheet role-mapped schema cleanly handles the reality that different work types have different ID columns, date column names, and parameter sets
- Parameter value normalization solves the singular/plural mismatch without polluting the analysis logic
- The Risk Level breakdown for Alerts surfaced something interesting in the sample data: error rate is *highest* on the lowest-risk alerts and *lowest* on highest-risk alerts (counterintuitive, worth investigating)
- Separating validation from analysis makes the agent fail fast with a readable error
- The `references/` folder earns its keep — guardrails and format rules are loaded on demand, not on every turn

## Limitations

- Risk Level analysis is Alerts-only (only sheet declaring it in `extras`)
- No comments column in this file structure, so no theme analysis (not added for testing)
- Sample-size threshold (n=20) is a heuristic in `STATISTICAL_GUARDRAILS.md`
- Schema must be explicitly declared per sheet; the skill doesn't auto-detect (deliberate trade-off — explicit means errors are clear)

