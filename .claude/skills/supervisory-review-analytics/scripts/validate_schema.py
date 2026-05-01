from __future__ import annotations
"""Schema validation for supervisory review Excel files.

Validates each sheet against its declared schema in expected_schema.json:
- All role-mapped columns (id, work_date, analyst, reviewer, review_date) must exist
- All declared review_parameters must exist
- Parameter columns must contain only values from parameter_values (Error/Errors, No Error/No Errors)

Usage:
    python validate_schema.py --file path/to/reviews.xlsx
    python validate_schema.py --file path/to/reviews.xlsx --schema path/to/schema.json

Exit codes:
    0 = all sheets valid
    1 = file or schema not readable
    2 = one or more sheets failed validation
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent / "assets" / "expected_schema.json"


def load_schema(schema_path: Path) -> dict:
    with schema_path.open() as f:
        return json.load(f)


def required_columns(sheet_schema: dict) -> list[str]:
    """All columns this sheet must carry."""
    cols = [
        sheet_schema["id_column"],
        sheet_schema["work_date_column"],
        sheet_schema["analyst_column"],
        sheet_schema["reviewer_column"],
        sheet_schema["review_date_column"],
    ]
    cols.extend(sheet_schema["review_parameters"])
    extras = sheet_schema.get("extras", {})
    cols.extend(v for v in extras.values())
    return cols


def validate_sheet(df: pd.DataFrame, sheet_schema: dict, allowed_values: set) -> dict:
    result = {"valid": True, "row_count": len(df), "issues": []}

    actual_cols = set(df.columns)
    required = required_columns(sheet_schema)
    missing = [c for c in required if c not in actual_cols]
    if missing:
        result["valid"] = False
        result["issues"].append(f"Missing columns: {missing}")
        return result

    # Check parameter columns hold only allowed values (or NaN)
    bad_params = {}
    for p in sheet_schema["review_parameters"]:
        non_null = df[p].dropna().astype(str)
        bad = sorted(set(non_null.unique()) - allowed_values)
        if bad:
            bad_params[p] = bad
    if bad_params:
        result["valid"] = False
        result["issues"].append(f"Unexpected values in parameter columns: {bad_params}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate supervisory review Excel schema")
    parser.add_argument("--file", required=True)
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH))
    args = parser.parse_args()

    file_path = Path(args.file)
    schema_path = Path(args.schema)

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    if not schema_path.exists():
        print(f"ERROR: Schema not found: {schema_path}", file=sys.stderr)
        sys.exit(1)

    schema = load_schema(schema_path)
    pv = schema["parameter_values"]
    allowed_values = set(pv["error"]) | set(pv["no_error"])

    try:
        xl = pd.ExcelFile(file_path)
    except Exception as e:
        print(f"ERROR: Could not read Excel file: {e}", file=sys.stderr)
        sys.exit(1)

    expected_sheets = set(schema["sheets"].keys())
    actual_sheets = set(xl.sheet_names)
    missing_sheets = expected_sheets - actual_sheets
    if missing_sheets:
        print(f"WARNING: Schema declares sheets not in file: {sorted(missing_sheets)}")

    extra_sheets = actual_sheets - expected_sheets
    if extra_sheets:
        print(f"NOTE: File has sheets not in schema (will be ignored): {sorted(extra_sheets)}")

    all_valid = True
    for sheet_name in sorted(expected_sheets & actual_sheets):
        sheet_schema = schema["sheets"][sheet_name]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        result = validate_sheet(df, sheet_schema, allowed_values)

        status = "OK" if result["valid"] else "FAIL"
        print(f"[{status}] {sheet_name!r}: {result['row_count']} rows, "
              f"{len(sheet_schema['review_parameters'])} parameters")
        for issue in result["issues"]:
            print(f"    {issue}")

        if not result["valid"]:
            all_valid = False

    if not all_valid:
        sys.exit(2)
    print("\nAll sheets valid.")
    sys.exit(0)


if __name__ == "__main__":
    main()
