"""Assess Chicago People data; run from the repository root or any directory.

    python assess_people.py
    python assess_people.py --people data/processed/people_2024_clean.csv \
        --report-dir data/processed/people_quality_after

Requires Python >=3.10 and pandas >=2.0. Inputs come from acquire_data.py.
This script never modifies input files. clean_people.py imports its shared rules.
Use (crash_record_id, vehicle_id) on both sides, as specified in ProjectPlan.md.
The current source metadata describes crash_unit_id, but the 2024 snapshot's
vehicle_id values do not match it. Never substitute that different identifier.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
REQUIRED = ["person_id", "person_type", "crash_record_id", "vehicle_id",
            "crash_date", "injury_classification"]
ID_COLUMNS = ["person_id", "crash_record_id", "vehicle_id", "crash_unit_id"]
PERSON_TYPES = {"DRIVER", "PASSENGER", "PEDESTRIAN", "BICYCLE",
                "NON-MOTOR VEHICLE", "NON-CONTACT VEHICLE"}
ROAD_USERS = {"DRIVER", "PASSENGER", "PEDESTRIAN", "BICYCLE"}
UNKNOWN = {"UNKNOWN", "UNK", "UNKNOWN/NA", "UNABLE TO DETERMINE"}
NOT_APPLICABLE = {"NA", "N/A", "NOT APPLICABLE"}
# Exact published injury categories; unfamiliar labels are NOT guessed.
INJURIES = {
    "FATAL": "FATAL",
    "INCAPACITATING INJURY": "INCAPACITATING",
    "NONINCAPACITATING INJURY": "NONINCAPACITATING",
    "REPORTED, NOT EVIDENT": "REPORTED_NOT_EVIDENT",
}
NO_INJURY = "NO INDICATION OF INJURY"
KNOWN_INJURIES = set(INJURIES) | {NO_INJURY}


def resolve_path(value):
    """Relative CLI paths are always relative to the scripts' directory."""
    path = Path(value)
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def read_csv(path, required, only_required=False):
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run acquire_data.py first, or pass an input path.")
    # Preserve leading zeros and literal NA/UNKNOWN tokens for auditing.
    options = {"usecols": lambda column: column in required} if only_required else {}
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig", **options)
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing required columns {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"{path.name}: contains no records")
    return frame


def canonicalize(frame):
    """Only identifiers and analysis categories are standardized here."""
    result = frame.copy()
    for col in ID_COLUMNS:
        if col in result:
            result[col] = result[col].str.strip().str.upper()
    for col in ("person_type", "injury_classification"):
        if col in result:
            result[col] = result[col].str.strip().str.upper().str.replace(r"\s+", " ", regex=True)
    if "crash_date" in result:
        result["crash_date"] = result["crash_date"].str.strip()
    return result


def parse_dates(series):
    # Socrata's crash_date is an ISO local timestamp, with no timezone conversion.
    return pd.to_datetime(series, format="ISO8601", errors="coerce")


def injury_status(series):
    status = pd.Series("UNRECOGNIZED", index=series.index, dtype="string")
    status.loc[series.eq("")] = "MISSING"
    status.loc[series.isin(UNKNOWN)] = "UNKNOWN"
    status.loc[series.isin(NOT_APPLICABLE)] = "NOT_APPLICABLE"
    status.loc[series.isin(KNOWN_INJURIES)] = "KNOWN"
    return status


def quality_flags(frame, year):
    """Flags identify concerns; they do not prove the source values are wrong."""
    flags = pd.DataFrame(index=frame.index)
    for col in REQUIRED:
        flags[f"missing_{col}"] = frame[col].eq("")
    for col, pattern in {"person_id": r"[OP][0-9]+", "crash_record_id": r"[A-F0-9]{128}",
                         "vehicle_id": r"[0-9]+"}.items():
        flags[f"unusual_{col}"] = frame[col].ne("") & ~frame[col].str.fullmatch(pattern)
    flags["duplicate_person_id"] = frame.person_id.ne("") & frame.person_id.duplicated(keep=False)
    flags["unrecognized_person_type"] = ~frame.person_type.isin(PERSON_TYPES | UNKNOWN | NOT_APPLICABLE | {""})
    flags["unrecognized_injury_classification"] = injury_status(frame.injury_classification).eq("UNRECOGNIZED")
    dates = parse_dates(frame.crash_date)
    flags["invalid_crash_date"] = frame.crash_date.ne("") & dates.isna()
    flags["outside_selected_year"] = dates.notna() & dates.dt.year.ne(year)
    flags["occupant_missing_vehicle_id"] = frame.person_type.isin({"DRIVER", "PASSENGER"}) & frame.vehicle_id.eq("")
    return flags


def input_info(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    try:
        label = path.relative_to(ROOT).as_posix()
    except ValueError:
        label = str(path)
    return {"path": label, "sha256": digest.hexdigest(), "bytes": path.stat().st_size}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_links(people, reference, vehicle=False):
    """Count reference matches without multiplying People rows or matching blanks."""
    keys = ["crash_record_id", "vehicle_id"] if vehicle else ["crash_record_id"]
    ref = canonicalize(reference)
    valid_ref = ref[keys].ne("").all(axis=1)
    counts = (ref.loc[valid_ref].groupby(keys, as_index=False)
              .agg(reference_matches=("crash_date", "size"), reference_date=("crash_date", "first")))
    merged = people[keys].merge(counts, on=keys, how="left", sort=False, validate="many_to_one")
    status = pd.Series("UNMATCHED", index=people.index, dtype="string")
    status.loc[merged.reference_matches.eq(1)] = "MATCHED"
    status.loc[merged.reference_matches.gt(1)] = "AMBIGUOUS"
    status.loc[~people[keys].ne("").all(axis=1)] = "MISSING_KEY"
    left_dates = parse_dates(people.crash_date)
    right_dates = parse_dates(merged.reference_date)
    comparable = status.eq("MATCHED") & left_dates.notna() & right_dates.notna()
    comparison = pd.Series("NOT_COMPARABLE", index=people.index, dtype="string")
    comparison.loc[comparable & left_dates.eq(right_dates)] = "AGREE"
    comparison.loc[comparable & left_dates.ne(right_dates)] = "DIFFERENT"
    details = pd.DataFrame({"person_type": people.person_type, "link_status": status,
                            "date_comparison": comparison})
    summary = details.groupby(list(details.columns), dropna=False).size().reset_index(name="count")
    reference_stats = {
        "reference_rows": len(ref), "reference_rows_missing_key": int((~valid_ref).sum()),
        "reference_duplicate_key_rows": int(ref.loc[valid_ref].duplicated(keys, keep=False).sum()),
        "people_link_status_counts": {str(k): int(v) for k, v in status.value_counts().items()},
    }
    return status, comparison, summary, reference_stats


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--people", default="data/raw/people_2024.csv")
    parser.add_argument("--crashes", default="data/raw/crashes_2024.csv")
    parser.add_argument("--vehicles", default="data/raw/vehicles_2024.csv")
    parser.add_argument("--report-dir", default="data/processed/people_quality")
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    paths = {name: resolve_path(getattr(args, name)) for name in ("people", "crashes", "vehicles")}
    raw = read_csv(paths["people"], REQUIRED)
    people = canonicalize(raw)
    crashes = read_csv(paths["crashes"], ["crash_record_id", "crash_date"], only_required=True)
    vehicles = read_csv(paths["vehicles"], ["crash_record_id", "vehicle_id", "crash_date"], only_required=True)
    report_dir = resolve_path(args.report_dir)
    if report_dir in {p.parent for p in paths.values()}:
        raise ValueError("Use a separate directory for assessment outputs, not an input directory.")
    report_dir.mkdir(parents=True, exist_ok=True)

    missing_rows = []
    for col in raw:
        values = raw[col].str.strip().str.upper()
        missing_rows.append({"column": col, "blank_count": int(values.eq("").sum()),
                             "blank_percent": float(values.eq("").mean() * 100),
                             "unknown_count": int(values.isin(UNKNOWN).sum()),
                             "not_applicable_count": int(values.isin(NOT_APPLICABLE).sum())})
    pd.DataFrame(missing_rows).to_csv(report_dir / "missing_values.csv", index=False)
    for col in ("person_type", "injury_classification"):
        people[col].value_counts(dropna=False).rename_axis(col).reset_index(name="count").to_csv(
            report_dir / f"{col}_counts.csv", index=False)

    flags = quality_flags(people, args.year)
    audit = people[["person_id", "crash_record_id", "vehicle_id", "person_type"]].copy()
    audit.insert(0, "source_record", range(1, len(audit) + 1))
    audit = pd.concat([audit, flags], axis=1)
    link_metadata = {}
    for name, reference in (("crash", crashes), ("vehicle", vehicles)):
        status, comparison, summary, stats = check_links(people, reference, vehicle=name == "vehicle")
        audit[f"{name}_link_status"] = status
        audit[f"{name}_date_comparison"] = comparison
        flags[f"{name}_link_unmatched"] = status.eq("UNMATCHED")
        flags[f"{name}_link_ambiguous"] = status.eq("AMBIGUOUS")
        flags[f"{name}_linked_date_different"] = comparison.eq("DIFFERENT")
        summary.to_csv(report_dir / f"{name}_links_by_person_type.csv", index=False)
        link_metadata[name] = stats
        print(f"{name.capitalize()} links: {stats['people_link_status_counts']}")
    # All rows are included so structural absent links remain auditable.
    audit.to_csv(report_dir / "record_checks.csv", index=False)
    flag_counts = flags.sum().astype(int).rename_axis("check").reset_index(name="count")
    flag_counts["percent"] = flag_counts["count"] / len(people) * 100
    flag_counts.to_csv(report_dir / "quality_summary.csv", index=False)
    dates = parse_dates(people.crash_date)
    dates.dropna().dt.to_period("M").astype(str).value_counts().sort_index().rename_axis("month").reset_index(
        name="count").to_csv(report_dir / "monthly_counts.csv", index=False)
    write_json(report_dir / "assessment.json", {
        "assessed_at_utc": datetime.now(timezone.utc).isoformat(), "pandas_version": pd.__version__,
        "year": args.year, "people_rows": len(people), "people_columns": len(raw.columns),
        "earliest_valid_date": str(dates.min()), "latest_valid_date": str(dates.max()),
        "inputs": {name: input_info(path) for name, path in paths.items()},
        "injury_status_counts": {str(k): int(v) for k, v in injury_status(people.injury_classification).value_counts().items()},
        "links": link_metadata,
        "notes": ["No rows are removed; counts of duplicate IDs include every affected row.",
                  "IDs are compared after trimming and uppercasing; blank keys never match.",
                  "Vehicle join: People(crash_record_id, vehicle_id) -> Vehicles(crash_record_id, vehicle_id), as in ProjectPlan.md.",
                  "Vehicles.crash_unit_id is a different identifier in this snapshot; do not substitute it for vehicle_id.",
                  "AMBIGUOUS means multiple reference records; their dates are not compared.",
                  "Timeliness measures 2024 coverage, not publication delay or historical revision lag.",
                  "Source date filtering excludes undated source records before this assessment.",
                  "Quality flags and format checks identify potential issues, not verified real-world errors."]})
    print(f"People: {len(people):,} records, {len(raw.columns)} columns")
    print(flag_counts.to_string(index=False))
    print(f"Reports saved to {report_dir}")


if __name__ == "__main__":
    main()
