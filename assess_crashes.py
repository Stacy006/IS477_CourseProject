
import pandas as pd

df = pd.read_csv("data/raw/crashes_2024.csv", low_memory=False)

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

missing = df.isnull().sum()
missing_percent = df.isnull().mean() * 100

missing_summary = pd.DataFrame({
    "Missing Count": missing,
    "Missing Percentage": missing_percent
})

missing_summary = missing_summary.sort_values(
    by="Missing Percentage",
    ascending=False
)

print(missing_summary.to_string())


columns_to_check = [
    "weather_condition",
    "lighting_condition",
    "roadway_surface_cond",
    "traffic_control_device",
    "prim_contributory_cause",
    "crash_type"
]

for col in columns_to_check:
    print(f"\n{col}")
    print(df[col].value_counts(dropna=False).head(15))


numeric_columns = [
    "posted_speed_limit",
    "num_units",
    "injuries_total",
    "injuries_fatal",
    "injuries_incapacitating",
    "crash_hour",
    "crash_month",
    "crash_day_of_week"
]

print("\nNUMERIC SUMMARY")
print(df[numeric_columns].describe().to_string())

print("\nPOSTED SPEED LIMIT VALUES")
print(df["posted_speed_limit"].value_counts().sort_index())

print("\nNUMBER OF UNITS")
print(df["num_units"].value_counts().sort_index())


injury_columns = [
    "injuries_fatal",
    "injuries_incapacitating",
    "injuries_non_incapacitating",
    "injuries_reported_not_evident",
    "injuries_no_indication",
    "injuries_unknown"
]

complete = df.dropna(
    subset=["injuries_total"] + injury_columns
).copy()

print("Records with complete injury data:", len(complete))

print(
    "Fatal injuries greater than total:",
    (complete["injuries_fatal"] > complete["injuries_total"]).sum()
)

injury_sum = complete[
    [
        "injuries_fatal",
        "injuries_incapacitating",
        "injuries_non_incapacitating",
        "injuries_reported_not_evident"
    ]
].sum(axis=1)

print(
    "Injury category sum differs from total:",
    (injury_sum != complete["injuries_total"]).sum()
)

print("\nCrash type vs injury count:")
print(
    pd.crosstab(
        df["crash_type"],
        df["injuries_total"] > 0
    )
)


inconsistent = df[
    (df["crash_type"] == "NO INJURY / DRIVE AWAY") &
    (df["injuries_total"] > 0)
]

print("\nPotentially inconsistent records:")
print(
    inconsistent[
        [
            "crash_record_id",
            "crash_date",
            "crash_type",
            "injuries_total",
            "injuries_fatal",
            "injuries_incapacitating",
            "injuries_non_incapacitating",
            "injuries_reported_not_evident"
        ]
    ].to_string(index=False)
)

print("Fatal > Total:",
      (complete["injuries_fatal"] > complete["injuries_total"]).sum())

print("Injury sum mismatch:",
      (injury_sum != complete["injuries_total"]).sum())


dates = pd.to_datetime(df["crash_date"])

print("Month mismatch:",
      (dates.dt.month != df["crash_month"]).sum())

print("Hour mismatch:",
      (dates.dt.hour != df["crash_hour"]).sum())

print("Day of week mismatch:",
      ((dates.dt.dayofweek + 1) % 7 + 1 != df["crash_day_of_week"]).sum())


crash_time = pd.to_datetime(df["crash_date"])
police_time = pd.to_datetime(df["date_police_notified"])

delay_hours = (police_time - crash_time).dt.total_seconds() / 3600

print("Police notified before crash:",
      (delay_hours < 0).sum())

print("Notification delay over 24 hours:",
      (delay_hours > 24).sum())

print("Missing notification times:",
      police_time.isna().sum())

print("Median notification delay (hours):",
      delay_hours.median())
