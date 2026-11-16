"""Clean Chicago People data without dropping records or guessing missing values.

    python clean_people.py

Place beside assess_people.py and acquire_data.py in the repository root.
Requires Python >=3.10 and pandas >=2.0. No downloads or joins occur here.
"""

import argparse
from datetime import datetime, timezone

import pandas as pd

from assess_people import (
    REQUIRED, ROAD_USERS, INJURIES, NO_INJURY, canonicalize, injury_status,
    input_info, parse_dates, quality_flags, read_csv, resolve_path, write_json,
)


def clean_people(raw, year=2024):
    """Return cleaned data, per-field change counts, and row-level quality flags."""
    clean = canonicalize(raw)
    dates = parse_dates(clean.crash_date)
    valid = dates.notna()
    # ISO output preserves fractional seconds; malformed dates remain for review.
    clean.loc[valid, "crash_date"] = dates.loc[valid].map(lambda value: value.isoformat())
    changes = [{"column": col, "changed_records": int(raw[col].ne(clean[col]).sum())}
               for col in raw.columns]
    clean["road_user_group"] = clean.person_type.where(clean.person_type.isin(ROAD_USERS), "OTHER_OR_UNRESOLVED")
    clean["injury_classification_status"] = injury_status(clean.injury_classification)
    clean["injury_known"] = clean.injury_classification_status.eq("KNOWN")
    # Nullable boolean is essential: an unknown injury must never become False.
    clean["injured"] = pd.Series(pd.NA, index=clean.index, dtype="boolean")
    clean.loc[clean.injury_classification.isin(INJURIES), "injured"] = True
    clean.loc[clean.injury_classification.eq(NO_INJURY), "injured"] = False
    clean["injury_severity"] = clean.injury_classification.map(INJURIES).astype("string")
    clean.loc[clean.injury_classification.eq(NO_INJURY), "injury_severity"] = "NO_INJURY"
    flags = quality_flags(clean, year)
    for col in flags:
        clean[f"quality_{col}"] = flags[col]
    return clean, pd.DataFrame(changes), flags


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--people", default="data/raw/people_2024.csv")
    parser.add_argument("--output", default="data/processed/people_2024_clean.csv")
    parser.add_argument("--report-dir", default="data/processed/people_cleaning")
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    source, output, report_dir = map(resolve_path, (args.people, args.output, args.report_dir))
    if output == source or source.parent in output.parents or source.parent == report_dir:
        raise ValueError("Keep cleaned data and reports outside the raw input directory.")
    if report_dir == output or output.parent == report_dir:
        raise ValueError("Use a dedicated subdirectory for cleaning reports.")
    raw = read_csv(source, REQUIRED)
    generated = {"road_user_group", "injury_classification_status", "injury_known", "injured", "injury_severity"}
    if generated.intersection(raw.columns) or any(col.startswith("quality_") for col in raw.columns):
        raise ValueError("Input already contains derived columns. Rerun with the preserved raw CSV.")
    source_info = input_info(source)
    clean, changes, flags = clean_people(raw, args.year)
    output.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output, index=False, na_rep="")

    # Validate what was actually saved, including unknowns and leading-zero IDs.
    saved = read_csv(output, REQUIRED)
    expected = clean.astype("string").fillna("").astype(str)
    injury_unknown = ~clean.injury_known
    checks = {
        "row_count_preserved": len(saved) == len(raw),
        "all_columns_and_values_survive_csv_roundtrip": saved.equals(expected),
        "identifier_values_and_row_order_preserved": saved["person_id"].equals(canonicalize(raw)["person_id"]),
        "unknown_injuries_remain_blank": bool(saved.loc[injury_unknown, "injured"].eq("").all()),
        "unknown_severities_remain_blank": bool(saved.loc[injury_unknown, "injury_severity"].eq("").all()),
        "known_injuries_have_boolean_status": bool(saved.loc[clean.injury_known, "injured"].isin(["True", "False"]).all()),
        "source_file_unchanged": input_info(source)["sha256"] == source_info["sha256"],
    }
    validation = pd.DataFrame([{"check": key, "passed": bool(value)} for key, value in checks.items()])
    validation.to_csv(report_dir / "validation.csv", index=False)
    if not all(checks.values()):
        raise RuntimeError(f"Output validation failed. See {report_dir / 'validation.csv'}")
    changes.to_csv(report_dir / "changed_fields.csv", index=False)
    flag_counts = flags.sum().astype(int).rename_axis("check").reset_index(name="count")
    flag_counts.to_csv(report_dir / "quality_after_cleaning.csv", index=False)
    clean.groupby(["road_user_group", "injury_classification_status"], dropna=False).size().reset_index(
        name="count").to_csv(report_dir / "group_classification_counts.csv", index=False)
    write_json(report_dir / "cleaning.json", {
        "cleaned_at_utc": datetime.now(timezone.utc).isoformat(), "pandas_version": pd.__version__,
        "year": args.year, "input": source_info, "output": input_info(output),
        "input_rows": len(raw), "output_rows": len(saved), "output_columns": len(saved.columns),
        "known_injury_records": int(clean.injury_known.sum()),
        "injured_records": int(clean.injured.sum()),
        "unknown_or_unrecognized_injury_records": int(injury_unknown.sum()),
        "injury_mapping": INJURIES, "no_injury_label": NO_INJURY,
        "rules": ["Trim and uppercase identifier fields; retain leading zeros.",
                  "Trim, uppercase, and collapse whitespace in person_type and injury_classification.",
                  "Normalize valid ISO timestamps; retain malformed timestamps with a quality flag.",
                  "Retain every row, including duplicates, invalid dates, other person types and absent vehicle IDs.",
                  "Retain unknown and unfamiliar source categories; injured and severity remain empty for them.",
                  "quality_* columns are review flags, not automatic exclusion rules.",
                  "Normalize crash IDs on BOTH sides of downstream joins; the existing Crashes file may use lowercase.",
                  "Join People.vehicle_id to Vehicles.vehicle_id within crash_record_id, as in ProjectPlan.md.",
                  "Read downstream IDs as strings and injured as a nullable boolean; do not use bool('False')."],
        "validation": {key: bool(value) for key, value in checks.items()}})
    print(f"Saved {len(saved):,} records to {output}")
    print(f"Known injury classifications: {clean.injury_known.sum():,}")
    print(f"Injured: {clean.injured.sum():,}; unknown/unrecognized: {injury_unknown.sum():,}")
    print(validation.to_string(index=False))
    print(f"Cleaning reports saved to {report_dir}")


if __name__ == "__main__":
    main()
