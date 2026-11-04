import requests
import pandas as pd
import hashlib
from pathlib import Path
from io import StringIO

datasets = {
    "crashes": "85ca-t3if",
    "vehicles": "68nd-jvt3",
    "people": "u6pd-qa9d"
}

output_dir = Path(__file__).resolve().parent / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

where = (
    "crash_date >= '2024-01-01T00:00:00' "
    "AND crash_date < '2025-01-01T00:00:00'"
)

limit = 5000

for name, dataset_id in datasets.items():
    file_path = output_dir / f"{name}_2024.csv"

    if file_path.exists():
        print(f"{name}: File already exists, skipping download.")
        continue

    print(f"\nDownloading {name}...")

    url = f"https://data.cityofchicago.org/resource/{dataset_id}.csv"

    offset = 0
    all_data = []

    while True:
        params = {
            "$where": where,
            "$order": {
                "crashes": "crash_record_id",
                "vehicles": "crash_unit_id",
                "people": "person_id"
            }[name],
            "$limit": limit,
            "$offset": offset
        }

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()

        df = pd.read_csv(StringIO(response.text), dtype=str)

        if df.empty:
            break

        all_data.append(df)
        offset += len(df)

        print(f"{name}: {offset} rows downloaded")

        if len(df) < limit:
            break

    data = pd.concat(all_data, ignore_index=True)
    data.to_csv(file_path, index=False)

    with open(file_path, "rb") as f:
        checksum = hashlib.file_digest(f, "sha256").hexdigest()

    print(f"{name}: Download complete!")
    print(f"Total rows: {len(data)}")
    print(f"SHA-256: {checksum}")