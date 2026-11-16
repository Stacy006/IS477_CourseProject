import os
import hashlib
import requests
import pandas as pd

integrated_file = "data/integrated/people_crashes_vehicles_2024.csv"
crashes_file = "data/processed/crashes_2024_clean.csv"
vehicles_file = "data/processed/vehicles_2024_cleaned.csv"
raw_files = {"crashes": "data/raw/crashes_2024.csv",
             "vehicles": "data/raw/vehicles_2024.csv",
             "people": "data/raw/people_2024.csv"}
dataset_ids = {"crashes": "85ca-t3if", "vehicles": "68nd-jvt3", "people": "u6pd-qa9d"}
results_dir = "results/integration"
year = 2024


def percent(part, whole):
    if whole == 0:
        return None
    return round(part / whole * 100, 4)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


df = pd.read_csv(integrated_file, dtype=str, keep_default_na=False)
crashes = pd.read_csv(crashes_file, low_memory=False)
crashes["crash_record_id"] = crashes["crash_record_id"].str.strip().str.upper()
vehicles = pd.read_csv(vehicles_file, dtype=str, keep_default_na=False)
raw_vehicles = pd.read_csv(raw_files["vehicles"], dtype=str, keep_default_na=False,
                           usecols=["crash_unit_id", "crash_record_id", "vehicle_id"])
vehicles["crash_record_id"] = vehicles["crash_record_id"].str.strip().str.upper()
vehicles["vehicle_id"] = vehicles["vehicle_id"].str.strip()
vehicles["crash_unit_id"] = vehicles["crash_unit_id"].str.strip()
os.makedirs(results_dir, exist_ok=True)

print("Integrated rows:", len(df))

totals = df.groupby("person_type").size().reset_index()
totals.columns = ["person_type", "type_total"]
link_tables = []
for link in ["crash", "vehicle"]:
    counts = df.groupby(["person_type", link + "_link_status"]).size().reset_index()
    counts.columns = ["person_type", "link_status", "count"]
    counts = counts.merge(totals, on="person_type", how="left")
    counts["percent_of_person_type"] = (counts["count"] / counts["type_total"] * 100).round(4)
    counts["link"] = link
    link_tables.append(counts[["link", "person_type", "link_status", "count", "percent_of_person_type"]])
links = pd.concat(link_tables)
links.to_csv(results_dir + "/link_status_by_person_type.csv", index=False)
print(links.to_string(index=False))

date_rows = []
people_dates = pd.to_datetime(df["crash_date"])
for link, col in [("crash", "crashes_crash_date"), ("vehicle", "vehicles_crash_date")]:
    matched = df[link + "_link_status"] == "MATCHED"
    left = people_dates[matched]
    right = pd.to_datetime(df.loc[matched, col])
    agree = (left == right).sum()
    date_rows.append([link, matched.sum(), len(left), agree, len(left) - agree, percent(agree, len(left))])
dates = pd.DataFrame(date_rows, columns=["link", "matched_people", "comparable", "agree", "different", "agreement_percent"])
dates.to_csv(results_dir + "/date_agreement.csv", index=False)
print(dates.to_string(index=False))

injury_fields = {
    "injuries_fatal": ["FATAL"],
    "injuries_incapacitating": ["INCAPACITATING"],
    "injuries_non_incapacitating": ["NONINCAPACITATING"],
    "injuries_reported_not_evident": ["REPORTED_NOT_EVIDENT"],
    "injuries_total": ["FATAL", "INCAPACITATING", "NONINCAPACITATING", "REPORTED_NOT_EVIDENT"],
    "injuries_no_indication": ["NO_INJURY"],
}
severity_counts = pd.crosstab(df["crash_record_id"], df["injury_severity"]).reset_index()
per_crash = crashes[["crash_record_id"] + list(injury_fields.keys())].merge(
    severity_counts, on="crash_record_id", how="left", indicator=True)
has_people = per_crash["_merge"] == "both"
injury_rows = []
discrepancy_tables = []
for field, categories in injury_fields.items():
    counted = per_crash[categories].fillna(0).sum(axis=1)
    reported = per_crash[field]
    comparable = reported.notna() & has_people
    diff = counted[comparable] - reported[comparable]
    agree = (diff == 0).sum()
    injury_rows.append([field, "+".join(categories), comparable.sum(), agree, (diff > 0).sum(), (diff < 0).sum(),
                        reported.isna().sum(), (~has_people).sum(), percent(agree, comparable.sum())])
    check = per_crash[comparable][["crash_record_id", field]].copy()
    check.columns = ["crash_record_id", "crashes_value"]
    check["crashes_field"] = field
    check["people_count"] = counted[comparable]
    check["difference"] = check["people_count"] - check["crashes_value"]
    discrepancy_tables.append(check[check["difference"] != 0])
injuries = pd.DataFrame(injury_rows, columns=["crashes_field", "people_categories", "crashes_compared", "agree",
                                              "people_higher", "people_lower", "crashes_value_missing",
                                              "crashes_without_people", "agreement_percent"])
discrepancies = pd.concat(discrepancy_tables)
discrepancies = discrepancies[["crash_record_id", "crashes_field", "crashes_value", "people_count", "difference"]]
injuries.to_csv(results_dir + "/injury_agreement.csv", index=False)
discrepancies.to_csv(results_dir + "/injury_discrepancies.csv", index=False)
print(injuries.to_string(index=False))
crashes_without_people = (~has_people).sum()
missing_total = per_crash["injuries_total"].isna()
print("Crashes without People:", crashes_without_people)
print("Crashes without People and missing injuries_total:", (~has_people & missing_total).sum())

missing_rows = []
linked = df["vehicle_link_status"] == "MATCHED"
unknown_types = ["UNKNOWN", "UNK", "UNABLE TO DETERMINE", "UNKNOWN/NA"]
for col in ["person_id", "crash_record_id", "person_type", "crash_date", "injury_classification",
            "vehicle_id", "crashes_injuries_total"]:
    blank = (df[col] == "").sum()
    missing_rows.append([col, len(df), blank, df[col].isin(unknown_types).sum(), percent(blank, len(df))])
for col in ["vehicles_vehicle_type", "vehicles_unit_type"]:
    values = df.loc[linked, col]
    blank = (values == "").sum()
    missing_rows.append([col + " (linked rows)", len(values), blank, values.isin(unknown_types).sum(),
                         percent(blank, len(values))])
missing = pd.DataFrame(missing_rows, columns=["field", "rows_checked", "blank", "unknown", "blank_percent"])
missing.to_csv(results_dir + "/missing_key_fields.csv", index=False)
print(missing.to_string(index=False))

vehicle_keys = vehicles[vehicles["vehicle_id"] != ""]
id_rows = [
    ["integrated", "person", "person_id", len(df), (df["person_id"] == "").sum(), df["person_id"].duplicated(keep=False).sum()],
    ["crashes", "crash", "crash_record_id", len(crashes), crashes["crash_record_id"].isna().sum(),
     crashes["crash_record_id"].duplicated(keep=False).sum()],
    ["vehicles", "unit", "crash_unit_id", len(vehicles), (vehicles["crash_unit_id"] == "").sum(),
     vehicles["crash_unit_id"].duplicated(keep=False).sum()],
    ["vehicles", "vehicle within crash", "crash_record_id+vehicle_id", len(vehicles), len(vehicles) - len(vehicle_keys),
     vehicle_keys.duplicated(subset=["crash_record_id", "vehicle_id"], keep=False).sum()],
]
uniqueness = pd.DataFrame(id_rows, columns=["dataset", "record_level", "key", "rows", "rows_with_blank_key", "duplicate_key_rows"])
uniqueness.to_csv(results_dir + "/id_uniqueness.csv", index=False)
print(uniqueness.to_string(index=False))

patterns = {"person_id": r"^[OP][0-9]+$", "crash_record_id": r"^[A-F0-9]{128}$",
            "vehicle_id": r"^[0-9]+$", "crash_unit_id": r"^[0-9]+$"}
format_checks = [("integrated", df, "person_id"), ("integrated", df, "crash_record_id"),
                 ("integrated", df, "vehicle_id"), ("crashes", crashes, "crash_record_id"),
                 ("vehicles", vehicles, "crash_record_id"), ("vehicles", vehicles, "vehicle_id"),
                 ("vehicles", vehicles, "crash_unit_id")]
format_rows = []
for name, table, col in format_checks:
    values = table[col].fillna("")
    nonblank = values[values != ""]
    unusual = (~nonblank.str.match(patterns[col])).sum()
    format_rows.append([name, col, patterns[col], len(nonblank), unusual])
formats = pd.DataFrame(format_rows, columns=["dataset", "column", "pattern", "nonblank", "unusual_format"])
formats.to_csv(results_dir + "/id_formats.csv", index=False)
print(formats.to_string(index=False))

people_keys = df[["crash_record_id", "vehicle_id"]].drop_duplicates()
vehicle_links = vehicle_keys.merge(people_keys, on=["crash_record_id", "vehicle_id"], how="left", indicator=True)
no_people = vehicle_links[vehicle_links["_merge"] == "left_only"]
unlinked_units = no_people["unit_type"].str.strip().str.upper().value_counts().reset_index()
unlinked_units.columns = ["unit_type", "vehicle_rows"]
unlinked_units.to_csv(results_dir + "/vehicles_without_people_by_unit_type.csv", index=False)
print(unlinked_units.to_string(index=False))

occupants = df[df["person_type"].isin(["DRIVER", "PASSENGER"])].copy()
occupants["known"] = occupants["injury_known"] == "True"
rq2 = occupants.groupby(["rq2_vehicle_group", "person_type"]).agg({"person_id": "count", "known": "sum"}).reset_index()
rq2.columns = ["rq2_vehicle_group", "person_type", "records", "known_injury_classification"]
rq2.to_csv(results_dir + "/rq2_vehicle_group_counts.csv", index=False)
other = occupants[occupants["rq2_vehicle_group"] == "EXCLUDED_OTHER_OR_UNRESOLVED_TYPE"]
other_status = other["vehicles_type_status"].value_counts().reset_index()
other_status.columns = ["type_status", "records"]
other_status.to_csv(results_dir + "/rq2_other_type_status.csv", index=False)
print(rq2.to_string(index=False))
print(other_status.to_string(index=False))

time_rows = []
for name, values in [("people", df["crash_date"]), ("crashes", crashes["crash_date"]), ("vehicles", vehicles["crash_date"])]:
    d = pd.to_datetime(values)
    time_rows.append([name, "earliest_crash_date", str(d.min())])
    time_rows.append([name, "latest_crash_date", str(d.max())])
    time_rows.append([name, "dates_outside_" + str(year), (d.dt.year != year).sum()])
for name, path in raw_files.items():
    acquired = pd.to_datetime(os.path.getmtime(path), unit="s")
    time_rows.append([name, "raw_file_saved_utc", str(acquired)[:19]])
for name, dataset_id in dataset_ids.items():
    response = requests.get("https://data.cityofchicago.org/api/views/" + dataset_id + ".json", timeout=60)
    updated = pd.to_datetime(response.json()["rowsUpdatedAt"], unit="s")
    time_rows.append([name, "source_rows_updated_utc", str(updated)])
timeliness = pd.DataFrame(time_rows, columns=["dataset", "check", "value"])
timeliness.to_csv(results_dir + "/timeliness.csv", index=False)
print(timeliness.to_string(index=False))

months = pd.to_datetime(df["crash_date"]).dt.to_period("M").astype(str)
monthly = months.value_counts().sort_index().reset_index()
monthly.columns = ["month", "people_records"]
monthly.to_csv(results_dir + "/monthly_counts.csv", index=False)

row_counts = pd.read_csv(results_dir + "/join_row_counts.csv")
id_compare = vehicles[["crash_unit_id", "vehicle_id"]].merge(
    raw_vehicles[["crash_unit_id", "vehicle_id"]], on="crash_unit_id", how="outer", suffixes=("", "_raw"), indicator=True)
vehicle_id_differences = ((id_compare["_merge"] != "both") | (id_compare["vehicle_id"] != id_compare["vehicle_id_raw"])).sum()
print("Vehicle IDs that differ between cleaned and raw Vehicles:", vehicle_id_differences)
checks = [
    ["people_rows_preserved", len(df) == row_counts["rows"].iloc[0]],
    ["no_row_multiplication", row_counts["rows"].nunique() == 1],
    ["person_id_unique_in_output", df["person_id"].duplicated().sum() == 0],
    ["all_people_matched_crashes", (df["crash_link_status"] == "MATCHED").all()],
    ["no_people_with_vehicle_id_unmatched", (df["vehicle_link_status"] == "UNMATCHED").sum() == 0],
    ["linked_dates_agree", dates["different"].sum() == 0],
    ["injury_counts_agree", len(discrepancies) == 0],
    ["vehicle_ids_match_raw_vehicles", vehicle_id_differences == 0],
]
validation = pd.DataFrame(checks, columns=["check", "passed"])
validation.to_csv(results_dir + "/validation.csv", index=False)
print(validation.to_string(index=False))

summary = [
    ["integrated_rows", len(df)],
    ["integrated_columns", len(df.columns)],
    ["people_linked_to_crashes", (df["crash_link_status"] == "MATCHED").sum()],
    ["people_linked_to_vehicles", linked.sum()],
    ["no_vehicle_id_expected", (df["vehicle_link_status"] == "NO_VEHICLE_ID_EXPECTED").sum()],
    ["no_vehicle_id_unexpected", (df["vehicle_link_status"] == "NO_VEHICLE_ID_UNEXPECTED").sum()],
    ["people_with_vehicle_id_unmatched", (df["vehicle_link_status"] == "UNMATCHED").sum()],
    ["crashes_without_people", crashes_without_people],
    ["vehicle_units_without_people", len(no_people)],
    ["crashes_ids_changed_by_uppercase", (pd.read_csv(raw_files["crashes"], usecols=["crash_record_id"])["crash_record_id"]
                                          != crashes["crash_record_id"]).sum()],
    ["vehicles_ids_changed_by_uppercase", (raw_vehicles["crash_record_id"] != raw_vehicles["crash_record_id"].str.upper()).sum()],
    ["vehicles_rows_with_vehicle_id", (vehicles["vehicle_id"] != "").sum()],
    ["rq2_passenger_car", (occupants["rq2_vehicle_group"] == "PASSENGER_CAR").sum()],
    ["rq2_suv", (occupants["rq2_vehicle_group"] == "SUV").sum()],
    ["rq2_excluded_other_or_unresolved", (occupants["rq2_vehicle_group"] == "EXCLUDED_OTHER_OR_UNRESOLVED_TYPE").sum()],
    ["rq2_excluded_no_vehicle_link", (occupants["rq2_vehicle_group"] == "EXCLUDED_NO_VEHICLE_LINK").sum()],
    ["sha256_integrated", sha256(integrated_file)],
    ["sha256_people_clean", sha256("data/processed/people_2024_clean.csv")],
    ["sha256_crashes_clean", sha256(crashes_file)],
    ["sha256_vehicles_clean", sha256(vehicles_file)],
    ["pandas_version", pd.__version__],
]
pd.DataFrame(summary, columns=["item", "value"]).to_csv(results_dir + "/summary.csv", index=False)
print(pd.DataFrame(summary, columns=["item", "value"]).to_string(index=False))
print("Results saved to", results_dir)
