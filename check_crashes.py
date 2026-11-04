import pandas as pd

df = pd.read_csv("data/raw/crashes_2024.csv", low_memory=False)

print("Rows:", len(df))
print("Columns:", len(df.columns))

dates = pd.to_datetime(df["crash_date"])
print("Earliest date:", dates.min())
print("Latest date:", dates.max())

print("Duplicate crash IDs:", df["crash_record_id"].duplicated().sum())

import hashlib

with open("data/raw/crashes_2024.csv", "rb") as f:
    checksum = hashlib.file_digest(f, "sha256").hexdigest()

print("SHA-256:", checksum)

from pathlib import Path

for name in ["vehicles", "people"]:
    path = Path(f"data/raw/{name}_2024.csv")
    data = pd.read_csv(path, low_memory=False)

    dates = pd.to_datetime(data["crash_date"])

    with open(path, "rb") as f:
        checksum = hashlib.file_digest(f, "sha256").hexdigest()

    print(f"\n{name.upper()}")
    print("Rows:", len(data))
    print("Columns:", len(data.columns))
    print("Earliest date:", dates.min())
    print("Latest date:", dates.max())
    print("SHA-256:", checksum)