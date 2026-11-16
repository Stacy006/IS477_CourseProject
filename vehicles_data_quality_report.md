# Vehicles Data Quality Assessment and Cleaning Report

## 1. Dataset Overview

This report documents the data quality assessment, cleaning decisions, and validation results for the **2024 Chicago Traffic Crashes – Vehicles** dataset. The Vehicles records were cross-checked against the **Traffic Crashes – Crashes** dataset.

| Item | Details |
| --- | --- |
| Source | [City of Chicago Data Portal – Vehicles](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3/about_data) |
| Primary dataset | Traffic Crashes – Vehicles (`68nd-jvt3`) |
| Cross-reference dataset | Traffic Crashes – Crashes (`85ca-t3if`) |
| Time period | January 1 – December 31, 2024 |
| Vehicle/unit records retrieved | **228,316** |
| Crash records retrieved | **112,056** |
| Vehicle fields selected from API | 7: `crash_unit_id`, `vehicle_id`, `crash_record_id`, `unit_no`, `crash_date`, `unit_type`, `vehicle_type` |
| Main unit identifier | `crash_unit_id` |
| Vehicle identifier assessed for linkage | `vehicle_id` |
| Link to Crashes | `crash_record_id` |

Python and the Chicago Open Data API were used to retrieve records in batches of 10,000. The assessment covered **completeness, accuracy, consistency, and timeliness**.

## 2. Data Quality Assessment

### 2.1 Completeness

Blank values were assessed separately from explicit `UNKNOWN` and `N/A` categories.

| Field or condition | Records | Percentage of 228,316 |
| --- | ---: | ---: |
| Blank `crash_unit_id` | 0 | 0.00% |
| Blank `crash_record_id` | 0 | 0.00% |
| Blank `unit_no` | 0 | 0.00% |
| Blank `crash_date` in the extracted records | 0 | 0.00% |
| Blank `unit_type` | 162 | 0.07% |
| Blank `vehicle_type` | 6,155 | 2.70% |
| `vehicle_type` = `UNKNOWN` | 17,186 | 7.53% |
| Blank `vehicle_id` | **6,155** | **2.70%** |

All records contained a `crash_unit_id`, but **6,155 records lacked a `vehicle_id`**. A follow-up check grouped these missing IDs by `unit_type`:

| `unit_type` for records with blank `vehicle_id` | Records |
| --- | ---: |
| `PEDESTRIAN` | 3,345 |
| `BICYCLE` | 2,349 |
| `NON-MOTOR VEHICLE` | 246 |
| Blank `unit_type` | 161 |
| `DRIVER` | 37 |
| `NON-CONTACT VEHICLE` | 9 |
| `DRIVERLESS` | 3 |
| `PARKED` | 3 |
| `DISABLED VEHICLE` | 1 |
| `EQUESTRIAN` | 1 |
| **Total** | **6,155** |

Of the missing IDs, **5,940 (96.51%)** were associated with pedestrian, bicycle, or other non-motor-vehicle units, where a vehicle identifier may not apply. The remaining **215 (3.49%)** were flagged for further review; their missing IDs cannot be assumed to be errors without additional evidence.

Separately, the vehicle-type classification distinguished **5,940 `NOT_APPLICABLE`** cases from **215 `MISSING`** cases. Missing and unknown values were retained rather than filled with guesses.

### 2.2 Accuracy

Identifiers were checked for expected formats, and frequency distributions were produced for `unit_type` and `vehicle_type`.

| Check | Result |
| --- | ---: |
| Invalid nonblank `crash_unit_id` formats | 0 |
| Invalid nonblank `crash_record_id` formats | 0 |
| **Invalid nonblank `vehicle_id` formats** | **0** |
| Invalid parsed dates in the selected extract | 0 |

All **222,161 nonblank `vehicle_id` values** passed the numeric-format check. Format validation establishes structural validity; it cannot independently confirm that identifiers or vehicle classifications were recorded correctly at the scene.

### 2.3 Consistency

The assessment checked identifier uniqueness, crash–vehicle key uniqueness, and links between Vehicles and Crashes.

| Check | Result |
| --- | ---: |
| Duplicate `crash_unit_id` values | 0 |
| Duplicate crash–unit ID pairs | 0 |
| **Duplicate (`crash_record_id`, `vehicle_id`) pairs among nonblank `vehicle_id` records** | **0** |
| Duplicate crash IDs in the Crashes extract | 0 |
| Vehicle records with unmatched `crash_record_id` | 0 |
| Vehicle records with conflicting linked crash dates | 0 |

All **228,316** retrieved Vehicles records matched a crash in the Crashes extract. Repeated `crash_record_id` values across different units are expected because a crash can involve multiple units.

The **0 duplicate crash–vehicle pairs** result applies only to records with a nonblank `vehicle_id`, consistent with the project's planned vehicle-level join requirements.

### 2.4 Timeliness

| Check | Result |
| --- | ---: |
| Invalid dates among retrieved records | 0 |
| Dates outside 2024 | 0 |

All retrieved records had valid crash dates within 2024. However, the API request **filtered by 2024 `crash_date` before extraction**. Thus, this check does not measure how many undated records exist in the full source dataset. Monthly counts were exported for a distribution review; reporting and publication delays were not assessed.

## 3. Data Cleaning

The workflow standardized whitespace and selected categorical text, including capitalization, while avoiding unsupported replacements for missing or unknown data. The retrieved records were retained in the full cleaned output.

Additional processing fields included `date_parsed`, `duplicate_unit`, `duplicate_pair`, `crash_link`, `type_status`, and `vehicle_group`.

The **6,155 blank `vehicle_id` values were preserved**. The follow-up assessment identified their distribution by unit type but did not manufacture substitute IDs or delete those rows. Records missing `vehicle_id` should be omitted only from joins that require that key, while remaining in the full Vehicles dataset.

**Vehicle-type classification:**

| `type_status` | Records |
| --- | ---: |
| `REPORTED` | 204,975 |
| `UNKNOWN` | 17,186 |
| `NOT_APPLICABLE` | 5,940 |
| `MISSING` | 215 |
| **Total** | **228,316** |

**Vehicle groups for the planned comparison:**

| `vehicle_group` | Records | Percentage |
| --- | ---: | ---: |
| `PASSENGER_CAR` | 136,486 | 59.78% |
| `SUV` | 35,781 | 15.67% |
| `OTHER_OR_UNRESOLVED` | 56,049 | 24.55% |
| **Total** | **228,316** | **100.00%** |

The `OTHER_OR_UNRESOLVED` group includes both legitimate other vehicle categories and unresolved classifications. A separate passenger-car/SUV analysis file was exported. Its **expected** record count is **172,267** (136,486 passenger cars + 35,781 SUVs), pending a direct check of the saved file.

## 4. Post-Cleaning Validation

The latest script output confirmed these **in-memory checks before export**:

| Validation check | Result |
| --- | ---: |
| Vehicle/unit rows assessed | 228,316 |
| Nonblank `vehicle_id` values | 222,161 |
| Blank `vehicle_id` values | 6,155 |
| Invalid nonblank `vehicle_id` formats | 0 |
| Duplicate nonblank crash–vehicle ID pairs | 0 |
| Duplicate `crash_unit_id` values | 0 |
| Unmatched crash IDs | 0 |
| Conflicting linked crash dates | 0 |
| Sum of vehicle-group counts | 228,316 |
| Sum of vehicle-type-status counts | 228,316 |

The CSV outputs were saved to `data/processed/`. **A separate post-export reload-and-recount validation has not yet been demonstrated**, so the stored files and passenger-car/SUV row count should be confirmed before final submission.

The additional `vehicle_id` format and uniqueness checks appeared in the console output. **They should also be added to `quality_summary.csv`** if that file is intended to be a complete record of all quality checks.

## 5. Output Files

| Artifact | Purpose |
| --- | --- |
| Python assessment script (use the actual filename in your repository) | API retrieval, data assessment, cleaning, and exports |
| `data/processed/vehicles_2024_cleaned.csv` | All selected Vehicles records, including the `vehicle_id` field |
| `data/processed/cars_vs_suvs_2024.csv` | Passenger-car/SUV analysis subset |
| `data/processed/quality_summary.csv` | Automated assessment counts; add the new ID checks to keep it complete |
| `data/processed/vehicle_type_counts.csv` | Vehicle-type frequency distribution |
| `data/processed/unit_type_counts.csv` | Unit-type frequency distribution |
| `data/processed/monthly_counts.csv` | Monthly record distribution for 2024 |

The workflow uses **Python**, `pandas`, and `requests`. The data was retrieved directly from the API rather than a manually downloaded CSV file.

## 6. Limitations and Next Steps

The assessment covered **seven selected Vehicles fields**, not all fields offered by the source. The API date filter excludes undated records from the extract, and format checks cannot establish the factual accuracy of recorded identifiers or classifications.

Most missing `vehicle_id` values occurred among non-motor-vehicle units, but **215 cases still warrant review**. Missing identifiers and unknown vehicle types were preserved rather than inferred. The passenger-car/SUV mapping should be reviewed against the exported category frequency tables.

