
import pandas as pd

df = pd.read_csv("data/raw/crashes_2024.csv", low_memory=False)

# Flag inconsistent injury information
df["injury_type_conflict"] = (
    (df["crash_type"] == "NO INJURY / DRIVE AWAY") &
    (df["injuries_total"] > 0)
)

# Calculate police notification delay
crash_time = pd.to_datetime(df["crash_date"])
police_time = pd.to_datetime(df["date_police_notified"])

df["notification_delay_hours"] = (
    (police_time - crash_time).dt.total_seconds() / 3600
)

# Flag delayed notifications
df["late_notification"] = df["notification_delay_hours"] > 24

print("Original rows:", len(df))
print("Injury type conflicts:", df["injury_type_conflict"].sum())
print("Late notifications:", df["late_notification"].sum())


import os

os.makedirs("data/processed", exist_ok=True)

df.to_csv("data/processed/crashes_2024_clean.csv", index=False)

print("Cleaned crashes data saved successfully!")

clean_df = pd.read_csv(
    "data/processed/crashes_2024_clean.csv",
    low_memory=False
)

print("\nVALIDATION RESULTS")
print("Rows:", len(clean_df))
print("Columns:", len(clean_df.columns))
print("Duplicate IDs:", clean_df["crash_record_id"].duplicated().sum())
print("Injury conflicts:", clean_df["injury_type_conflict"].sum())
print("Late notifications:", clean_df["late_notification"].sum())
