from __future__ import annotations
"""Core analytics for supervisory review Excel files.

For each sheet, uses the per-sheet schema (column role mappings + declared
review parameters) to compute error-rate analytics. Normalizes singular/plural
parameter values (Error/Errors, No Error/No Errors). Filters by work date.

Outputs:
    analysis.json  -- structured per-sheet results
    summary.xlsx   -- multi-tab workbook with per-sheet views

Usage:
    python analyze_reviews.py \\
        --file reviews.xlsx \\
        --start 2026-01-01 \\
        --end 2026-03-31 \\
        --out /tmp/q1_analysis

    # Period-over-period comparison:
    python analyze_reviews.py --file ... --start ... --end ... --out ... --compare-prior

    # Specific sheets only:
    python analyze_reviews.py --file ... --start ... --end ... --out ... --sheets "Alerts" "Phone Calls"
"""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent / "assets" / "expected_schema.json"


def load_schema(schema_path: Path) -> dict:
    with schema_path.open() as f:
        return json.load(f)


def normalize_parameters(df: pd.DataFrame, parameters: list[str], pv: dict) -> pd.DataFrame:
    """Map all parameter values to canonical 'Error' / 'No Error' / NaN."""
    error_vals = set(pv["error"])
    no_error_vals = set(pv["no_error"])

    df = df.copy()
    for p in parameters:
        def normalize(v):
            if pd.isna(v):
                return pd.NA
            s = str(v)
            if s in error_vals:
                return "Error"
            if s in no_error_vals:
                return "No Error"
            return pd.NA  # Unrecognized -> treat as not evaluated
        df[p] = df[p].apply(normalize)
    return df


def filter_by_date(df: pd.DataFrame, work_date_col: str, start: date, end: date) -> pd.DataFrame:
    df = df.copy()
    df[work_date_col] = pd.to_datetime(df[work_date_col], errors="coerce")
    df = df.dropna(subset=[work_date_col])
    mask = (df[work_date_col] >= pd.Timestamp(start)) & (df[work_date_col] <= pd.Timestamp(end))
    return df.loc[mask].copy()


def overall_stats(df: pd.DataFrame, parameters: list[str]) -> dict:
    total_cases = len(df)
    if not parameters or df.empty:
        return {
            "total_cases": total_cases,
            "total_parameter_evaluations": 0,
            "total_errors": 0,
            "overall_error_rate": 0.0,
        }
    evals = df[parameters].isin(["Error", "No Error"])
    n_evals = int(evals.sum().sum())
    n_errors = int((df[parameters] == "Error").sum().sum())
    rate = n_errors / n_evals if n_evals else 0.0
    return {
        "total_cases": total_cases,
        "total_parameter_evaluations": n_evals,
        "total_errors": n_errors,
        "overall_error_rate": round(rate, 4),
    }


def per_analyst(df: pd.DataFrame, parameters: list[str], analyst_col: str,
                min_sample: int) -> pd.DataFrame:
    rows = []
    if df.empty:
        return pd.DataFrame(columns=["Analyst", "Cases Reviewed", "Parameters Evaluated",
                                     "Errors", "Error Rate", "Sample Size OK"])
    for analyst, group in df.groupby(analyst_col, dropna=True):
        if not parameters:
            continue
        evals = group[parameters].isin(["Error", "No Error"])
        n_evals = int(evals.sum().sum())
        n_errors = int((group[parameters] == "Error").sum().sum())
        rate = n_errors / n_evals if n_evals else 0.0
        rows.append({
            "Analyst": analyst,
            "Cases Reviewed": len(group),
            "Parameters Evaluated": n_evals,
            "Errors": n_errors,
            "Error Rate": round(rate, 4),
            "Sample Size OK": n_evals >= min_sample,
        })
    if not rows:
        return pd.DataFrame(columns=["Analyst", "Cases Reviewed", "Parameters Evaluated",
                                     "Errors", "Error Rate", "Sample Size OK"])
    return pd.DataFrame(rows).sort_values("Error Rate", ascending=False, ignore_index=True)


def per_parameter(df: pd.DataFrame, parameters: list[str]) -> pd.DataFrame:
    rows = []
    for p in parameters:
        col = df[p]
        evals = col.isin(["Error", "No Error"]).sum()
        errors = (col == "Error").sum()
        rate = errors / evals if evals else 0.0
        rows.append({
            "Parameter": p,
            "Evaluations": int(evals),
            "Errors": int(errors),
            "Error Rate": round(rate, 4),
        })
    if not rows:
        return pd.DataFrame(columns=["Parameter", "Evaluations", "Errors", "Error Rate"])
    return pd.DataFrame(rows).sort_values("Error Rate", ascending=False, ignore_index=True)


def analyst_parameter_matrix(df: pd.DataFrame, parameters: list[str], analyst_col: str) -> pd.DataFrame:
    if df.empty or not parameters:
        return pd.DataFrame()
    analysts = sorted(df[analyst_col].dropna().unique())
    if not analysts:
        return pd.DataFrame()
    data = {p: [] for p in parameters}
    for analyst in analysts:
        group = df[df[analyst_col] == analyst]
        for p in parameters:
            col = group[p]
            evals = col.isin(["Error", "No Error"]).sum()
            errors = (col == "Error").sum()
            rate = errors / evals if evals else None
            data[p].append(round(rate, 4) if rate is not None else None)
    matrix = pd.DataFrame(data, index=analysts)
    matrix.index.name = "Analyst"
    return matrix.reset_index()


def reviewer_coverage(df: pd.DataFrame, reviewer_col: str, analyst_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[reviewer_col, analyst_col, "Reviews"])
    coverage = df.groupby([reviewer_col, analyst_col]).size().reset_index(name="Reviews")
    return coverage.sort_values([reviewer_col, "Reviews"], ascending=[True, False],
                                ignore_index=True)


def risk_level_breakdown(df: pd.DataFrame, parameters: list[str], risk_col: str) -> pd.DataFrame:
    """Error rate by Risk Level. Only meaningful for Alerts."""
    if df.empty or risk_col not in df.columns or not parameters:
        return pd.DataFrame()
    rows = []
    for risk, group in df.groupby(risk_col, dropna=True):
        evals = group[parameters].isin(["Error", "No Error"])
        n_evals = int(evals.sum().sum())
        n_errors = int((group[parameters] == "Error").sum().sum())
        rate = n_errors / n_evals if n_evals else 0.0
        rows.append({
            "Risk Level": int(risk) if pd.notna(risk) else None,
            "Cases": len(group),
            "Evaluations": n_evals,
            "Errors": n_errors,
            "Error Rate": round(rate, 4),
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("Risk Level", ignore_index=True)


def prior_period(start: date, end: date) -> tuple[date, date]:
    length = (end - start).days
    prior_end = start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=length)
    return prior_start, prior_end


def compare_analysts(current: pd.DataFrame, prior: pd.DataFrame) -> pd.DataFrame:
    if current.empty and prior.empty:
        return pd.DataFrame()
    if prior.empty:
        prior = pd.DataFrame(columns=["Analyst", "Error Rate", "Parameters Evaluated"])
    merged = current.merge(
        prior[["Analyst", "Error Rate", "Parameters Evaluated"]],
        on="Analyst", how="outer", suffixes=(" (current)", " (prior)"),
    )
    merged["Rate Change"] = (
        merged.get("Error Rate (current)", 0).fillna(0) -
        merged.get("Error Rate (prior)", 0).fillna(0)
    ).round(4)
    return merged.sort_values("Rate Change", ascending=False, ignore_index=True)


def analyze_sheet(df: pd.DataFrame, sheet_schema: dict, min_sample: int) -> dict:
    parameters = sheet_schema["review_parameters"]
    analyst_col = sheet_schema["analyst_column"]
    reviewer_col = sheet_schema["reviewer_column"]

    out = {
        "parameters": parameters,
        "overall": overall_stats(df, parameters),
        "by_analyst": per_analyst(df, parameters, analyst_col, min_sample).to_dict(orient="records"),
        "by_parameter": per_parameter(df, parameters).to_dict(orient="records"),
        "analyst_parameter_matrix": analyst_parameter_matrix(df, parameters, analyst_col).to_dict(orient="records"),
        "reviewer_coverage": reviewer_coverage(df, reviewer_col, analyst_col).to_dict(orient="records"),
    }

    extras = sheet_schema.get("extras", {})
    risk_col = extras.get("risk_level_column")
    if risk_col:
        out["risk_level_breakdown"] = risk_level_breakdown(df, parameters, risk_col).to_dict(orient="records")
    return out


def sanitize_sheet_name(name: str, suffix: str) -> str:
    safe = re.sub(r"[\\/*?:\[\]]", "-", name)
    max_base = 31 - len(suffix) - 1
    if len(safe) > max_base:
        safe = safe[:max_base]
    return f"{safe}-{suffix}"


def write_excel_summary(results_by_sheet: dict, out_path: Path,
                        comparison_by_sheet: dict | None = None):
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        # Overview tab
        overview = []
        for sheet_name, res in results_by_sheet.items():
            row = {"Work Type": sheet_name, **res["overall"],
                   "Parameters": ", ".join(res["parameters"])}
            overview.append(row)
        pd.DataFrame(overview).to_excel(writer, sheet_name="Overview", index=False)

        # Per-sheet views
        for sheet_name, res in results_by_sheet.items():
            pd.DataFrame(res["by_analyst"]).to_excel(
                writer, sheet_name=sanitize_sheet_name(sheet_name, "Analyst"), index=False)
            pd.DataFrame(res["by_parameter"]).to_excel(
                writer, sheet_name=sanitize_sheet_name(sheet_name, "Param"), index=False)
            matrix = pd.DataFrame(res["analyst_parameter_matrix"])
            if not matrix.empty:
                matrix.to_excel(writer, sheet_name=sanitize_sheet_name(sheet_name, "Matrix"), index=False)
            pd.DataFrame(res["reviewer_coverage"]).to_excel(
                writer, sheet_name=sanitize_sheet_name(sheet_name, "Coverage"), index=False)
            if "risk_level_breakdown" in res:
                pd.DataFrame(res["risk_level_breakdown"]).to_excel(
                    writer, sheet_name=sanitize_sheet_name(sheet_name, "RiskLvl"), index=False)

        if comparison_by_sheet:
            for sheet_name, cmp_df in comparison_by_sheet.items():
                if cmp_df is not None and not cmp_df.empty:
                    cmp_df.to_excel(writer,
                                    sheet_name=sanitize_sheet_name(sheet_name, "Trend"),
                                    index=False)


def main():
    parser = argparse.ArgumentParser(description="Analyze supervisory review Excel file")
    parser.add_argument("--file", required=True)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--out", required=True)
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH))
    parser.add_argument("--sheets", nargs="+", default=None)
    parser.add_argument("--compare-prior", action="store_true")
    parser.add_argument("--min-sample", type=int, default=20)
    args = parser.parse_args()

    file_path = Path(args.file)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(Path(args.schema))
    pv = schema["parameter_values"]

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    xl = pd.ExcelFile(file_path)
    declared = set(schema["sheets"].keys())
    available = set(xl.sheet_names)
    target = declared & available
    if args.sheets:
        target = target & set(args.sheets)
    target = sorted(target)

    if not target:
        print("No sheets to process (intersection of schema, file, and --sheets is empty)",
              file=sys.stderr)
        sys.exit(2)

    results_by_sheet = {}
    comparison_by_sheet = {} if args.compare_prior else None

    for sheet_name in target:
        sheet_schema = schema["sheets"][sheet_name]
        raw = pd.read_excel(file_path, sheet_name=sheet_name)
        normalized = normalize_parameters(raw, sheet_schema["review_parameters"], pv)
        df = filter_by_date(normalized, sheet_schema["work_date_column"], start, end)

        if df.empty:
            results_by_sheet[sheet_name] = {
                "note": f"No rows in range {start}..{end}",
                "parameters": sheet_schema["review_parameters"],
                "overall": overall_stats(df, sheet_schema["review_parameters"]),
                "by_analyst": [], "by_parameter": [],
                "analyst_parameter_matrix": [], "reviewer_coverage": [],
            }
            continue

        results_by_sheet[sheet_name] = analyze_sheet(df, sheet_schema, args.min_sample)

        if args.compare_prior:
            p_start, p_end = prior_period(start, end)
            prior_df = filter_by_date(normalized, sheet_schema["work_date_column"], p_start, p_end)
            if not prior_df.empty:
                prior_results = analyze_sheet(prior_df, sheet_schema, args.min_sample)
                results_by_sheet[sheet_name]["prior_period"] = {
                    "start": str(p_start), "end": str(p_end),
                    "rows": len(prior_df),
                    "overall": prior_results["overall"],
                }
                comparison_by_sheet[sheet_name] = compare_analysts(
                    pd.DataFrame(results_by_sheet[sheet_name]["by_analyst"]),
                    pd.DataFrame(prior_results["by_analyst"]),
                )

    output = {
        "period": {"start": str(start), "end": str(end)},
        "sheets_processed": target,
        "results_by_sheet": results_by_sheet,
    }

    (out_dir / "analysis.json").write_text(json.dumps(output, indent=2, default=str))
    write_excel_summary(results_by_sheet, out_dir / "summary.xlsx", comparison_by_sheet)

    print(f"Wrote {out_dir / 'analysis.json'}")
    print(f"Wrote {out_dir / 'summary.xlsx'}")
    print(f"Sheets processed: {target}")


if __name__ == "__main__":
    main()
