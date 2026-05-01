# Supervisory Review — Q1 2026

**Period:** 2026-01-01 to 2026-03-31  
**Work types analyzed:** Agreements, Alerts, Phone Calls

> *Example narrative output produced by the skill on `sample_reviews.xlsx`. The model writes the prose around these tables; the script computes every number.*

---

## Agreements

**Overall:** 80 cases, 160 evaluations, **11.2% overall error rate**

### Average error rate by metric

| Metric | Evaluations | Errors | Error Rate |
|---|---|---|---|
| Documentation Saved | 80 | 13 | 16.2% |
| Information Check | 80 | 5 | 6.2% |

### Per-analyst summary

| Analyst | Cases | Evaluations | Errors | Error Rate | Note |
|---|---|---|---|---|---|
| LP | 16 | 32 | 5 | 15.6% |  |
| MT | 16 | 32 | 4 | 12.5% |  |
| KA | 16 | 32 | 4 | 12.5% |  |
| JH | 16 | 32 | 3 | 9.4% |  |
| BS | 16 | 32 | 2 | 6.2% |  |

### Per-analyst per-metric breakdown — error rate by metric

*Each cell shows the percent of that analyst's evaluations on that metric marked as Error.*

| Analyst | Information Check | Documentation Saved |
|---|---|---|
| BS | 0.0% | 12.5% |
| JH | 0.0% | 18.8% |
| KA | 0.0% | 25.0% |
| LP | 12.5% | 18.8% |
| MT | 18.8% | 6.2% |

---

## Alerts

**Overall:** 100 cases, 300 evaluations, **9.3% overall error rate**

### Average error rate by metric

| Metric | Evaluations | Errors | Error Rate |
|---|---|---|---|
| Review Info | 100 | 17 | 17.0% |
| Review Notes | 100 | 11 | 11.0% |
| Review Status | 100 | 0 | 0.0% |

### Per-analyst summary

| Analyst | Cases | Evaluations | Errors | Error Rate | Note |
|---|---|---|---|---|---|
| KA | 20 | 60 | 8 | 13.3% |  |
| BS | 20 | 60 | 6 | 10.0% |  |
| JH | 20 | 60 | 5 | 8.3% |  |
| MT | 20 | 60 | 5 | 8.3% |  |
| LP | 20 | 60 | 4 | 6.7% |  |

### Per-analyst per-metric breakdown — error rate by metric

*Each cell shows the percent of that analyst's evaluations on that metric marked as Error.*

| Analyst | Review Info | Review Status | Review Notes |
|---|---|---|---|
| BS | 15.0% | 0.0% | 15.0% |
| JH | 15.0% | 0.0% | 10.0% |
| KA | 30.0% | 0.0% | 10.0% |
| LP | 10.0% | 0.0% | 10.0% |
| MT | 15.0% | 0.0% | 10.0% |

### Risk Level breakdown

| Risk Level | Cases | Evaluations | Errors | Error Rate |
|---|---|---|---|---|
| 1 | 24 | 72 | 10 | 13.9% |
| 2 | 31 | 93 | 9 | 9.7% |
| 3 | 45 | 135 | 9 | 6.7% |

---

## Phone Calls

**Overall:** 180 cases, 540 evaluations, **19.4% overall error rate**

### Average error rate by metric

| Metric | Evaluations | Errors | Error Rate |
|---|---|---|---|
| Completeness of Entry | 180 | 72 | 40.0% |
| Matter Resolved | 180 | 23 | 12.8% |
| Matter Closed | 180 | 10 | 5.6% |

### Per-analyst summary

| Analyst | Cases | Evaluations | Errors | Error Rate | Note |
|---|---|---|---|---|---|
| KA | 36 | 108 | 26 | 24.1% |  |
| MT | 36 | 108 | 22 | 20.4% |  |
| JH | 36 | 108 | 20 | 18.5% |  |
| LP | 35 | 105 | 18 | 17.1% |  |
| BS | 37 | 111 | 19 | 17.1% |  |

### Per-analyst per-metric breakdown — error rate by metric

*Each cell shows the percent of that analyst's evaluations on that metric marked as Error.*

| Analyst | Completeness of Entry | Matter Resolved | Matter Closed |
|---|---|---|---|
| BS | 43.2% | 5.4% | 2.7% |
| JH | 38.9% | 8.3% | 8.3% |
| KA | 50.0% | 13.9% | 8.3% |
| LP | 31.4% | 14.3% | 5.7% |
| MT | 36.1% | 22.2% | 2.8% |

