---
name: supervisory-review-analytics
description: Analyzes multi-sheet supervisory review Excel files (Alerts, Agreements, Phone Calls, etc.) to produce per-work-type error-rate analytics, per-analyst summaries, risk-level breakdowns, and period-over-period comparisons. Each sheet has its own schema with different identifier columns, date columns, and review parameters; the skill maps roles per sheet via a configurable schema. Normalizes singular/plural error values (Error/Errors, No Error/No Errors). Use when the user asks for review analytics, error rates, analyst performance, or monthly/quarterly review summaries over a specified time period. Does not make personnel recommendations or draw conclusions from small samples.
---

# Supervisory Review Analytics

## When to use this skill

Activate this skill when the user asks to:
- Run monthly or quarterly review analytics
- Compute error rates from a supervisory review file
- Summarize analyst performance for a given period
- Compare two time periods (e.g., Q1 vs prior period, January vs February)
- Produce narrative highlights or an Excel summary from review data
- Analyze a specific work item type ("just the Alerts sheet" or "just Phone Calls")
- Investigate whether errors correlate with risk level (Alerts only)

## When NOT to use this skill

- **Ranking or rating individual analysts.** Decline and offer the per-analyst breakdown instead. Supervisory data informs development conversations; it does not produce personnel rankings.
- **Drawing conclusions from tiny samples.** See `references/STATISTICAL_GUARDRAILS.md`. Apply the n=20 threshold per analyst per work type — an analyst may clear it on Phone Calls but not Alerts.
- **Files that don't match the declared schema.** Validate first; if validation fails, surface the issue and stop.
- **Free-form HR questions.** This skill computes and summarizes. It does not recommend actions.

## Required inputs

1. Path to the review Excel file (.xlsx)
2. Date range (natural language like "Q1," "October," or explicit "2026-01-01 to 2026-03-31"). The model converts to explicit YYYY-MM-DD before invoking the script.
3. Optional: specific sheet names to analyze (defaults to all declared sheets present in the file)

The date filter applies to each sheet's **work date** column (when the case was originally worked: `Date of Alert` for Alerts, `Date` for Agreements and Phone Calls), not the `1st Level Review Date`.

## Schema model

Each sheet has its own schema declared in `assets/expected_schema.json`. For each sheet, the schema specifies:

- `id_column` — what identifies a row (e.g., `Alert ID`, `Firm`, `Call ID`)
- `work_date_column` — when the case was worked (the date used for filtering)
- `analyst_column` — who did the original work
- `reviewer_column` — who reviewed (`1st Level Reviewer`)
- `review_date_column` — when the review was completed
- `review_parameters` — list of columns evaluated as Error / No Error
- `extras` — optional sheet-specific fields (e.g., `risk_level_column` on Alerts)

Parameter values are normalized internally: `"Error"` / `"Errors"` both become Error; `"No Error"` / `"No Errors"` both become No Error; anything else is treated as not evaluated.

## Workflow

1. **Parse the user's period request.** Convert natural language to explicit `(start_date, end_date)`. Confirm if ambiguous ("Q1" = Jan 1–Mar 31; "last month" depends on today). Q1 of 2026 is `2026-01-01` to `2026-03-31`.

2. **Validate the schema.** Run:
   ```
   scripts/validate_schema.py --file <path>
   ```
   Reports per-sheet status. Stop if any sheet fails on a sheet the user wanted to analyze.

3. **Run the analysis.**
   ```
   scripts/analyze_reviews.py --file <path> --start <YYYY-MM-DD> --end <YYYY-MM-DD> --out <output_dir>
   ```
   Add `--sheets "Alerts" "Phone Calls"` to scope. Add `--compare-prior` for period-over-period comparison.

   Outputs:
   - `analysis.json` — structured per-sheet results
   - `summary.xlsx` — multi-tab workbook

4. **Apply the statistical guardrails.** Load `references/STATISTICAL_GUARDRAILS.md` before writing the narrative. Apply rules **per work type**.

5. **Write the narrative.** Use `references/REPORT_FORMATS.md`. Two formats:
   - **Monthly:** brief, per-work-type highlights
   - **Quarterly:** substantive, with period-over-period and (for Alerts) risk-level analysis

   For every work type, the narrative MUST include three views (see REPORT_FORMATS.md):
   - **Average error rate by metric** (per-parameter table — overall team rate per metric)
   - **Per-analyst summary** (overall rate per analyst across all metrics)
   - **Per-analyst per-metric breakdown — error rate by metric** (matrix where each cell shows that analyst's error rate on that specific metric)

   The matrix is the most actionable view — it tells the supervisor whether an analyst's elevated rate is concentrated in one specific metric or spread across all of them.

6. **Present results.** Show the markdown narrative; report the path to `summary.xlsx`.

## Output format

**Markdown narrative** — organized by work type. Each section includes overall stats, per-analyst table with sample-size flags, parameter-level findings, and (for Alerts) a risk-level callout if the breakdown surfaces something unusual. Final cross-work-type observation if patterns repeat across sheets.

**Excel summary** (`summary.xlsx`) — tabs:
- `Overview` — one row per work type
- `<Sheet>-Analyst` — per-analyst table
- `<Sheet>-Param` — per-parameter table
- `<Sheet>-Matrix` — analyst × parameter error rate matrix
- `<Sheet>-Coverage` — reviewer × analyst review counts
- `Alerts-RiskLvl` — error rate by Risk Level (Alerts only)
- `<Sheet>-Trend` — period-over-period analyst comparison (only with `--compare-prior`)

Sheet names in `summary.xlsx` are sanitized to comply with Excel's 31-char and forbidden-character rules.

## Limitations

- Risk Level analysis is Alerts-only (only sheet declaring `extras.risk_level_column`).
- Error rates are descriptive, not diagnostic. A high rate may reflect difficult case mix, training timing, or genuine performance — the skill cannot distinguish.
- The sample-size threshold (n=20) is a heuristic. Adjust in `references/STATISTICAL_GUARDRAILS.md` if your context warrants.
- This file structure has no comments column, so theme analysis is not produced. If a future file adds one, the script can be extended.

## Why the script is load-bearing (not just parsing)

Reading the .xlsx is maybe 15% of what `analyze_reviews.py` does. The substantive work:

| Operation | Why it's not "just parsing" |
|---|---|
| Per-sheet schema interpretation | Each sheet has different identifier, date, and parameter columns. The script applies the right schema per sheet. |
| Parameter value normalization | Singular vs plural ("Error" vs "Errors") differs across sheets. Script unifies them so the math is consistent. |
| Aggregation arithmetic | Per-analyst error rates across hundreds of rows. LLMs silently produce wrong numbers at this scale. |
| Analyst × parameter cross-tab | Pivot computation per sheet. The model would drop cells. |
| Reviewer × analyst coverage matrix | Group-by aggregation for surfacing coverage imbalance. |
| Risk Level breakdown for Alerts | Conditional aggregation by an extra dimension. |
| Prior-period date arithmetic + re-analysis | Computing the equivalent prior window and running the full analysis on it. |
| Relational join for analyst rate deltas | Standard join + delta arithmetic. Unreliable in prose. |
| Excel sheet-name sanitization | Excel has a 31-char limit and forbids `\\ / * ? : [ ]`. Script handles it. |
| Multi-tab .xlsx generation with openpyxl | The model literally cannot produce binary file formats. |
| Per-work-type sample-size flagging at scale | Rule application across the data, not summary judgment. |

What the model does on top: parses vague date phrases, decides which findings warrant narrative highlight (guided by the guardrails), writes the prose, refuses inappropriate framings. Neither half could do this alone.
