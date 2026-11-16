# Vehicles Data Quality Assessment and Cleaning Report

## 1. Dataset Overview

This report documents the data quality assessment, cleaning decisions, and validation results for the **2024 Chicago Traffic Crashes – Vehicles** dataset. The Vehicles data was cross-checked against the corresponding **Traffic Crashes – Crashes** dataset.

| Item | Details |
|---|---|
| Source | [City of Chicago Data Portal](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3/about_data) |
| Primary dataset | Traffic Crashes – Vehicles (`68nd-jvt3`) |
| Cross-reference dataset | Traffic Crashes – Crashes (`85ca-t3if`) |
| Time period | January 1 – December 31, 2024 |
| Vehicle/unit records retrieved | 228,316 |
| Crash records retrieved | 112,056 |
| Vehicle columns selected from API | 7: `crash_unit_id`, `vehicle_id`, `crash_record_id`, `unit_no`, `crash_date`, `unit_type`, `vehicle_type` |
| Main unit identifier | `crash_unit_id` |
| Link to Crashes | `crash_record_id` |

The assessment covered four data quality dimensions: **completeness, accuracy, consistency, and timeliness**. Records were retrieved automatically using Python, the Chicago Open Data API, and pagination in batches of 10,000.

## 2. Data Quality Assessment

### 2.1 Completeness

Blank values and explicit `UNKNOWN` or `N/A` categories were counted separately for the selected fields.

| Field / condition | Records | Percentage of 228,316 |
|---|---:|---:|
| Missing `crash_unit_id` | 0 | 0.00% |
| Missing `crash_record_id` | 0 | 0.00% |
| Missing `unit_no` | 0 | 0.00% |
| Missing `crash_date` in the extracted records | 0 | 0.00% |
| Missing `unit_type` | 162 | 0.07% |
| Blank `vehicle_type` | 6,155 | 2.70% |
| `vehicle_type` reported as `UNKNOWN` | 17,186 | 7.53% |
| Blank `vehicle_id` | 6,155 | 2.70% |

The missing `vehicle_id` values were distinguished from `crash_unit_id`: every retrieved record had a `crash_unit_id`, but **6,155 records had a blank `vehicle_id`**. Blank and unknown vehicle types were not automatically filled because their correct values could not be reliably inferred.

The cleaning classifications further distinguished **5,940 not-applicable** vehicle-type records (primarily non-vehicle unit categories) from **215 remaining missing** vehicle-type records. The API's date-based extraction means the zero missing-date count does **not** measure date completeness across the entire source portal.

### 2.2 Accuracy

Identifier formats were examined using checks for numeric `crash_unit_id` values and the expected hexadecimal format of `crash_record_id`. Category frequency distributions were also generated for `unit_type` and `vehicle_type`.

| Check | Result |
|---|---:|
| Invalid nonblank `crash_unit_id` formats | 0 |
| Invalid nonblank `crash_record_id` formats | 0 |
| Invalid parsed dates within the extract | 0 |

These checks found no format violations in the selected fields. They do not independently verify whether a reported vehicle type is factually correct. `vehicle_id` was assessed for missingness but was not separately tested for format or uniqueness in the reported results.

### 2.3 Consistency

Consistency checks tested uniqueness of unit identifiers and relationships between the Vehicles and Crashes datasets.

| Check | Result |
|---|---:|
| Rows with duplicate `crash_unit_id` values | 0 |
| Rows with duplicate crash–unit ID pairs | 0 |
| Duplicate `crash_record_id` values in the Crashes extract | 0 |
| Vehicle records with unmatched `crash_record_id` values | 0 |
| Vehicle records with conflicting linked crash dates | 0 |

All **228,316** vehicle/unit records matched a crash record in the 2024 Crashes extract. Repeated `crash_record_id` values in the Vehicles dataset were treated as expected because multiple units can be involved in the same crash.

### 2.4 Timeliness

The script checked whether the retrieved crash dates could be parsed and belonged to 2024.

| Check | Result |
|---|---:|
| Invalid dates in selected records | 0 |
| Dates outside 2024 | 0 |

The API query was restricted to crash dates from **January 1 through December 31, 2024**. As a result, the assessment confirms date validity for the retrieved records only; records without usable dates were excluded by the query rather than measured. A monthly record-count file was created to support review of the distribution across 2024. This was a coverage check, not a measurement of reporting or publication delay.

## 3. Data Cleaning

The cleaning process aimed to standardize selected fields without inventing missing information. Whitespace was removed from selected text fields, and `crash_record_id`, `unit_type`, and `vehicle_type` were standardized to uppercase. Blank, `UNKNOWN`, and not-applicable classifications were kept distinct.

The script added quality and analysis fields including `date_parsed`, `duplicate_unit`, `duplicate_pair`, `crash_link`, `type_status`, and `vehicle_group`.

**Vehicle-type status after classification:**

| Status | Records |
|---|---:|
| `REPORTED` | 204,975 |
| `UNKNOWN` | 17,186 |
| `NOT_APPLICABLE` | 5,940 |
| `MISSING` | 215 |
| **Total** | **228,316** |

**Groups for subsequent analysis:**

| Vehicle group | Records | Percentage |
|---|---:|---:|
| `PASSENGER_CAR` | 136,486 | 59.78% |
| `SUV` | 35,781 | 15.67% |
| `OTHER_OR_UNRESOLVED` | 56,049 | 24.55% |
| **Total** | **228,316** | **100.00%** |

The `OTHER_OR_UNRESOLVED` group includes legitimate vehicle types outside the passenger-car/SUV comparison as well as unresolved classifications. All **228,316 retrieved rows** were retained in the cleaned file. A separate passenger-car/SUV dataset was exported for focused analysis. Its expected size is **172,267** records based on the reported category counts and successful quality checks; its saved row count should be confirmed directly.

## 4. Post-Cleaning Validation

The script's execution summary confirmed the following checks before export:

| Validation check | Result |
|---|---:|
| Vehicle/unit rows assessed | 228,316 |
| Invalid nonblank unit and crash ID formats | 0 |
| Duplicate unit IDs | 0 |
| Unmatched crash IDs | 0 |
| Conflicting linked crash dates | 0 |
| Total of all vehicle groups | 228,316 |
| Total of all type-status categories | 228,316 |

The script wrote the cleaned data and summary files to `data/processed/`. **A separate reload-and-recount validation of the saved CSV files was not shown in the supplied execution output** and remains a recommended final check.

## 5. Output Files

| Artifact | Purpose |
|---|---|
| Python assessment script (use actual repository filename) | API retrieval, assessment, cleaning, and export |
| `data/processed/vehicles_2024_cleaned.csv` | All 228,316 retrieved records with standardized values and added indicators |
| `data/processed/cars_vs_suvs_2024.csv` | Passenger-car/SUV comparison subset |
| `data/processed/quality_summary.csv` | Counts produced by the quality checks |
| `data/processed/vehicle_type_counts.csv` | Reported vehicle-type frequencies |
| `data/processed/unit_type_counts.csv` | Reported unit-type frequencies |
| `data/processed/monthly_counts.csv` | 2024 monthly record-count distribution |

The workflow used **Python**, `pandas`, and `requests`. It retrieved records directly from the API; it did not require a separate manually downloaded raw CSV file.

## 6. Limitations and Next Steps

The assessment was limited to **seven selected vehicle fields**, not every field available in the Chicago Vehicles dataset. The extraction filter also prevented evaluation of source records with missing or unusable crash dates. Identifier-format checks establish structural validity rather than independent factual accuracy.

Missing or unknown vehicle types and blank `vehicle_id` values were retained because there was insufficient evidence to infer replacements. The vehicle-group rules should be reviewed against the frequency reports before drawing conclusions from the car/SUV comparison.

Next steps include **reloading exported CSVs to verify their row counts and columns**, confirming the car/SUV subset size, integrating the cleaned Vehicles dataset with the team's Crashes and People work, and improving run instructions and error handling for reproducibility. Since the public dataset can change, reproducible snapshots should also record the extraction date or preserve the downloaded source extract.
