import os
import pandas as pd

people_file = "data/processed/people_2024_clean.csv"
crashes_file = "data/processed/crashes_2024_clean.csv"
vehicles_file = "data/processed/vehicles_2024_cleaned.csv"
output_file = "data/integrated/people_crashes_vehicles_2024.csv"
results_dir = "results/integration"

crash_columns = ["crash_record_id", "crash_date", "crash_type", "most_severe_injury", "num_units",
                 "injuries_total", "injuries_fatal", "injuries_incapacitating",
                 "injuries_non_incapacitating", "injuries_reported_not_evident",
                 "injuries_no_indication", "injuries_unknown", "injury_type_conflict",
                 "late_notification"]
vehicle_columns = ["crash_unit_id", "unit_no", "unit_type", "vehicle_type", "crash_date",
                   "type_status", "vehicle_group"]
no_vehicle_types = ["PEDESTRIAN", "BICYCLE", "NON-MOTOR VEHICLE"]


def clean_ids(df):
    for col in ["person_id", "crash_record_id", "vehicle_id", "crash_unit_id"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.upper()
    return df


people = pd.read_csv(people_file, dtype=str, keep_default_na=False)
crashes = pd.read_csv(crashes_file, dtype=str, keep_default_na=False)
vehicles = pd.read_csv(vehicles_file, dtype=str, keep_default_na=False)

people = clean_ids(people)
crashes = clean_ids(crashes)
vehicles = clean_ids(vehicles)

for col in ["crash_record_id", "vehicle_id"] + vehicle_columns:
    if col not in vehicles.columns:
        raise ValueError("Vehicles file is missing " + col + ". Run vehicle_assessment.py first.")

print("People rows:", len(people))
print("Crashes rows:", len(crashes))
print("Vehicles rows:", len(vehicles))

crash_part = crashes[crash_columns].copy()
new_names = {}
for col in crash_columns:
    if col != "crash_record_id":
        new_names[col] = "crashes_" + col
crash_part = crash_part.rename(columns=new_names)

vehicle_part = vehicles[vehicles["vehicle_id"] != ""]
vehicle_part = vehicle_part[["crash_record_id", "vehicle_id"] + vehicle_columns].copy()
new_names = {}
for col in vehicle_columns:
    new_names[col] = "vehicles_" + col
vehicle_part = vehicle_part.rename(columns=new_names)

if crash_part["crash_record_id"].duplicated().sum() > 0:
    raise ValueError("Crashes has duplicate crash_record_id values.")
if vehicle_part.duplicated(subset=["crash_record_id", "vehicle_id"]).sum() > 0:
    raise ValueError("Vehicles has duplicate crash_record_id + vehicle_id values.")

rows_before = len(people)
merged = people.merge(crash_part, on="crash_record_id", how="left", indicator=True)
merged = merged.rename(columns={"_merge": "crash_merge"})
rows_after_crashes = len(merged)
merged = merged.merge(vehicle_part, on=["crash_record_id", "vehicle_id"], how="left", indicator=True)
merged = merged.rename(columns={"_merge": "vehicle_merge"})
rows_after_vehicles = len(merged)

if rows_after_crashes != rows_before or rows_after_vehicles != rows_before:
    raise ValueError("A join changed the number of People rows.")

merged["crash_link_status"] = "UNMATCHED"
merged.loc[merged["crash_merge"] == "both", "crash_link_status"] = "MATCHED"

missing_vehicle_id = merged["vehicle_id"] == ""
expected = merged["person_type"].isin(no_vehicle_types)
merged["vehicle_link_status"] = "UNMATCHED"
merged.loc[merged["vehicle_merge"] == "both", "vehicle_link_status"] = "MATCHED"
merged.loc[missing_vehicle_id & expected, "vehicle_link_status"] = "NO_VEHICLE_ID_EXPECTED"
merged.loc[missing_vehicle_id & ~expected, "vehicle_link_status"] = "NO_VEHICLE_ID_UNEXPECTED"

occupant = merged["person_type"].isin(["DRIVER", "PASSENGER"])
linked = merged["vehicle_link_status"] == "MATCHED"
merged["rq2_vehicle_group"] = "NOT_OCCUPANT"
merged.loc[occupant & ~linked, "rq2_vehicle_group"] = "EXCLUDED_NO_VEHICLE_LINK"
merged.loc[occupant & linked, "rq2_vehicle_group"] = "EXCLUDED_OTHER_OR_UNRESOLVED_TYPE"
merged.loc[occupant & linked & (merged["vehicles_vehicle_group"] == "PASSENGER_CAR"), "rq2_vehicle_group"] = "PASSENGER_CAR"
merged.loc[occupant & linked & (merged["vehicles_vehicle_group"] == "SUV"), "rq2_vehicle_group"] = "SUV"

merged = merged.drop(columns=["crash_merge", "vehicle_merge"])

os.makedirs("data/integrated", exist_ok=True)
os.makedirs(results_dir, exist_ok=True)
merged.to_csv(output_file, index=False)

row_counts = pd.DataFrame([
    ["people_input", rows_before],
    ["after_crashes_join", rows_after_crashes],
    ["after_vehicles_join", rows_after_vehicles],
], columns=["step", "rows"])
row_counts.to_csv(results_dir + "/join_row_counts.csv", index=False)

print(row_counts.to_string(index=False))
print(merged["crash_link_status"].value_counts())
print(merged["vehicle_link_status"].value_counts())
print("Saved", len(merged), "rows and", len(merged.columns), "columns to", output_file)
