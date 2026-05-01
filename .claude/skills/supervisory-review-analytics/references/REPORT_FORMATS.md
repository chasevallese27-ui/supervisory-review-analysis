# Report Formats

Two canonical narrative shapes. Pick based on the user's request: "monthly report" → monthly; "quarterly report" or 60+ day range → quarterly. Ad-hoc ranges default to monthly unless the user asks otherwise.

Both formats organize the narrative by **work item type** (one section per sheet processed), then finish with cross-work-type observations.

## Required content for every report

For each work type processed, the narrative MUST include all three of these views:

1. **Per-metric averages** — error rate for each parameter (from `by_parameter`)
2. **Per-analyst overall summary** — each analyst's overall error rate on this work type (from `by_analyst`)
3. **Per-analyst per-metric breakdown** — which specific metrics each analyst failed on (from `analyst_parameter_matrix`)

The third view is the most actionable. A supervisor needs to know not just "Analyst KA had a high error rate" but "Analyst KA's high rate is driven by Completeness of Entry (50%) — Matter Resolved and Matter Closed are normal." Always include the per-analyst per-metric matrix as a table.

## Monthly Report

Short and scannable. Meant to copy-paste into the monthly review document.

```
## Supervisory Review — [Month YYYY]

**Period:** [start_date] to [end_date]
**Work types analyzed:** [Alerts | Agreements | Phone Calls]

---

### [Work Type 1]

**Overall:** [N] cases, [N] parameter evaluations, **[X.X%] overall error rate**

**Average error rate by metric**
| Metric | Evaluations | Errors | Error Rate |
|---|---|---|---|
| [Parameter A] | ... | ... | X.X% |
| [Parameter B] | ... | ... | X.X% |
| [Parameter C] | ... | ... | X.X% |

**Per-analyst summary**
| Analyst | Cases | Evaluations | Errors | Error Rate | Note |
|---|---|---|---|---|---|
| ... | ... | ... | ... | X.X% | ⚠ if <20 evals |

**Per-analyst per-metric breakdown — error rate by metric**

*Each cell shows the percent of that analyst's evaluations on that metric marked as Error.*

| Analyst | [Param A] | [Param B] | [Param C] |
|---|---|---|---|
| ... | X.X% | X.X% | X.X% |

[1-2 bullet observations: which metric is the team-wide weak spot, whether any single analyst's elevated rate is concentrated in one specific metric vs. spread evenly. No personnel judgments.]

---

### [Work Type 2]
[Same three-table structure]

---

### Cross-work-type observations
- [2-3 bullets: patterns repeating across sheets]
- [Data-quality caveats: insufficient samples, etc.]
```

## Quarterly Report

More substantive. Includes period-over-period and (for Alerts) risk-level analysis.

```
## Supervisory Review — [Quarter YYYY]

**Period:** [start_date] to [end_date]
**Work types analyzed:** [list]

### Executive summary
[3-4 sentences: most important findings; one per work type plus the strongest cross-cutting pattern.]

---

### [Work Type 1]

**Overall:** [X.X%] error rate (prior period: [Y.Y%], change: [±Z.Z pp])

**Average error rate by metric**
[Table with metric, evaluations, errors, rate — sorted by rate descending]

**Per-analyst summary with prior-period comparison**
| Analyst | Cases | Evaluations | Rate | Prior Rate | Change | Note |
|---|---|---|---|---|---|---|

**Per-analyst per-metric breakdown — error rate by metric**

*Each cell shows the percent of that analyst's evaluations on that metric marked as Error.*

| Analyst | [Param A] | [Param B] | [Param C] |
|---|---|---|---|

[Bullet observations: which metrics drive the headline rate, where individual analyst patterns concentrate, period-over-period movement that clears the significance threshold.]

**Reviewer coverage**
[1-2 sentences noting any imbalances; no interpretation.]

---

### Alerts — Risk Level Analysis
[Only when Alerts is in scope. Always include the table. Flag in narrative only when there is a meaningful pattern.]

| Risk Level | Cases | Evaluations | Errors | Error Rate |
|---|---|---|---|---|

[Brief observation if pattern is meaningful.]

---

### [Other Work Types...]
[Same structure]

---

### Cross-work-type analysis
- **Analyst patterns across work types:** [e.g., does an analyst's weak metric on one sheet correlate with anything on another sheet]
- **Reviewer coverage patterns**
- **Overall team trajectory** (observation, not prediction)

### Data quality notes
```

## Style rules for both formats

- Use percentages, not proportions ("4.2%" not "0.042")
- One decimal place for rates; two only if precision matters
- Tables over prose when comparing numbers
- Short sentences — supervisors skim
- Organize by work type first, then the three required tables within each work type
- Apply per-work-type sample-size rules to the per-analyst tables
- Load `STATISTICAL_GUARDRAILS.md` before writing — do not paraphrase from memory

## When the per-analyst per-metric matrix is empty

If a sheet has only one parameter, the matrix collapses to a single column and is redundant with the per-analyst summary. In that case, omit the matrix and add a note: "Single parameter — see per-analyst summary above."

## Highlighting which metric an analyst "failed on"

When an analyst's overall error rate is notably above the team average for a work type, identify in prose which specific parameter is driving it. Read from the matrix:

- If one parameter accounts for the bulk of an analyst's errors → "Analyst [X]'s elevated rate on [Work Type] is concentrated in [Parameter]; their rates on other parameters are in line with the team."
- If errors are spread across multiple parameters → "Analyst [X]'s elevated rate on [Work Type] is spread across multiple parameters rather than concentrated in one."

Both framings are descriptive and actionable without ranking the analyst against peers.
