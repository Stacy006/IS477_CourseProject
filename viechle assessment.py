
from pathlib import Path
import pandas as pd
import requests

# 1. Get 2024 records from the Chicago API, 10,000 at a time.
year = 2024
out = Path(__file__).resolve().parent / "data" / "processed"
out.mkdir(parents=True, exist_ok=True)


def download(dataset, columns, sort_by):
    url = f"https://data.cityofchicago.org/resource/{dataset}.json"
    rows = []
    offset = 0
    while True:
        params = {
            "$select": ",".join(columns),
            "$where": f"crash_date >= '{year}-01-01' AND crash_date < '{year + 1}-01-01'",
            "$order": sort_by,
            "$limit": 10000,
            "$offset": offset,
        }
        response = requests.get(url, params=params, timeout=90)
        response.raise_for_status()
        batch = response.json()
        rows.extend(batch)
        print(f"{dataset}: {len(rows):,} records")
        if len(batch) < 10000:
            break
        offset += len(batch)
    return pd.DataFrame(rows, columns=columns).fillna("").astype(str)


cols = ["crash_unit_id", "crash_record_id", "unit_no", "crash_date", "unit_type", "vehicle_type", "vehicle_id"]
v = download("68nd-jvt3", cols, "crash_unit_id")
c = download("85ca-t3if", ["crash_record_id", "crash_date"], "crash_record_id")
if v.empty or c.empty:
    raise ValueError("API returned no records. Check the API connection and selected year.")

# 2. Clean formatting (keep missing and unknown values unchanged).
for col in cols:
    v[col] = v[col].str.strip()
for col in ["crash_record_id", "unit_type", "vehicle_type"]:
    v[col] = v[col].str.upper()
c["crash_record_id"] = c["crash_record_id"].str.strip().str.upper()

# 3. Completeness: blank, UNKNOWN and N/A are counted separately.
unknown = {"UNKNOWN", "UNK", "UNABLE TO DETERMINE", "UNKNOWN/NA"}
not_applicable = {"NA", "N/A", "NOT APPLICABLE"}
results = {"Vehicle records": len(v), "Crash records": len(c)}
for col in cols:
    results[f"{col} blank"] = int(v[col].eq("").sum())
    results[f"{col} unknown"] = int(v[col].isin(unknown).sum())
    results[f"{col} N/A"] = int(v[col].isin(not_applicable).sum())

# 4. Accuracy: identifier formats and category frequencies.
unit_ok = v["crash_unit_id"].str.fullmatch(r"\d+")
crash_ok = v["crash_record_id"].str.fullmatch(r"[A-F0-9]{128}")
results["Invalid nonblank unit IDs"] = int((v["crash_unit_id"].ne("") & ~unit_ok).sum())
results["Unusual nonblank crash IDs"] = int((v["crash_record_id"].ne("") & ~crash_ok).sum())
for col in ["unit_type", "vehicle_type"]:
    v[col].value_counts().rename_axis(col).reset_index(name="count").to_csv(
        out / f"{col}_counts.csv", index=False
    )

# 5. Timeliness and consistency.
v["date_parsed"] = pd.to_datetime(v["crash_date"], errors="coerce")
results["Invalid dates in selected records"] = int(v["date_parsed"].isna().sum())
results["Dates outside selected year"] = int((v["date_parsed"].notna() & v["date_parsed"].dt.year.ne(year)).sum())
v["date_parsed"].dt.to_period("M").value_counts().sort_index().to_csv(out / "monthly_counts.csv")
v["duplicate_unit"] = v["crash_unit_id"].ne("") & v["crash_unit_id"].duplicated(keep=False)
v["duplicate_pair"] = v["crash_unit_id"].ne("") & v.duplicated(["crash_record_id", "crash_unit_id"], keep=False)
results["Rows with duplicate unit IDs"] = int(v["duplicate_unit"].sum())
results["Rows with duplicate crash-unit pairs"] = int(v["duplicate_pair"].sum())
results["Duplicate IDs in Crashes"] = int(c["crash_record_id"].duplicated().sum())
crash_dates = c.drop_duplicates("crash_record_id").set_index("crash_record_id")["crash_date"]
v["crash_link"] = v["crash_record_id"].map(crash_dates)
results["Unmatched nonblank crash IDs"] = int((v["crash_record_id"].ne("") & v["crash_link"].isna()).sum())
results["Different linked crash dates"] = int((v["crash_link"].notna() & (v["crash_date"].str[:10] != v["crash_link"].str[:10])).sum())
v["crash_link"] = v["crash_link"].notna()  # True means a matching crash record exists.

# 6. Do not guess missing vehicle types; separate cars and SUVs.
v["type_status"] = "REPORTED"
v.loc[v["vehicle_type"].eq(""), "type_status"] = "MISSING"
v.loc[v["vehicle_type"].isin(unknown), "type_status"] = "UNKNOWN"
v.loc[v["vehicle_type"].isin(not_applicable), "type_status"] = "NOT_APPLICABLE"
nonvehicle = v["unit_type"].isin({"PEDESTRIAN", "BICYCLE", "NON-MOTOR VEHICLE"})
v.loc[nonvehicle & v["vehicle_type"].isin({""} | not_applicable), "type_status"] = "NOT_APPLICABLE"
v["vehicle_group"] = "OTHER_OR_UNRESOLVED"
v.loc[v["vehicle_type"].eq("PASSENGER"), "vehicle_group"] = "PASSENGER_CAR"
v.loc[v["vehicle_type"].isin({"SUV", "SPORT UTILITY VEHICLE (SUV)"}), "vehicle_group"] = "SUV"
results.update({f"Vehicle group: {x}": int(n) for x, n in v["vehicle_group"].value_counts().items()})
results.update({f"Type status: {x}": int(n) for x, n in v["type_status"].value_counts().items()})

# 7. Save all rows and a separate analysis-ready comparison file.
v.to_csv(out / "vehicles_2024_cleaned.csv", index=False)
valid = (v["vehicle_group"].isin(["PASSENGER_CAR", "SUV"]) & unit_ok & crash_ok
         & ~v["duplicate_unit"] & v["crash_link"] & v["date_parsed"].dt.year.eq(year))
v.loc[valid].to_csv(out / "cars_vs_suvs_2024.csv", index=False)
pd.DataFrame(results.items(), columns=["Check", "Count"]).to_csv(out / "quality_summary.csv", index=False)
print("\n", pd.DataFrame(results.items(), columns=["Check", "Count"]).to_string(index=False))
print("\nResults saved to:", out)
print("Note: Filtering by crash_date excludes undated source records from this extract.")
