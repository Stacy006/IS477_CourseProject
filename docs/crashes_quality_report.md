# Crashes Data Quality Assessment and Cleaning Report

## 1. Dataset Overview

This report documents the data quality assessment, cleaning decisions, and validation results for the 2024 Chicago Traffic Crashes – Crashes dataset.

- **Source:** Chicago Data Portal
- **Dataset:** Traffic Crashes – Crashes
- **Dataset ID:** `85ca-t3if`
- **Time period:** January 1 – December 31, 2024
- **Original records:** 112,056
- **Original columns:** 49
- **Unique identifier:** `crash_record_id`

The assessment covered four data quality dimensions: completeness, accuracy, consistency, and timeliness.

## 2. Data Quality Assessment

### 2.1 Completeness

Missing values were examined for all 49 columns.

Several fields had high missing-value percentages, including:

| Column | Missing Percentage |
|---|---:|
| lane_cnt | 99.98% |
| workers_present_i | 99.89% |
| work_zone_type | 99.71% |
| dooring_i | 99.64% |
| work_zone_i | 99.60% |
| intersection_related_i | 76.59% |
| hit_and_run_i | 67.99% |
| report_type | 4.53% |
| latitude | 1.06% |
| longitude | 1.06% |
| injuries_total | 0.22% |

Some fields may only apply to particular crash circumstances. Therefore, high missingness does not necessarily indicate incorrect data.

In addition to null values, categorical fields contained values representing unknown or undetermined information.

| Column | Category | Records |
|---|---|---:|
| weather_condition | UNKNOWN | 8,826 |
| lighting_condition | UNKNOWN | 7,093 |
| roadway_surface_cond | UNKNOWN | 14,692 |
| traffic_control_device | UNKNOWN | 7,128 |
| prim_contributory_cause | UNABLE TO DETERMINE | 45,995 |

These categories were retained rather than automatically converted to missing values or replaced with estimated information.

### 2.2 Accuracy

Numeric ranges were examined to identify potentially invalid or unusual values.

| Variable | Minimum | Maximum |
|---|---:|---:|
| posted_speed_limit | 0 | 70 |
| num_units | 1 | 18 |
| injuries_total | 0 | 15 |
| injuries_fatal | 0 | 2 |
| crash_hour | 0 | 23 |
| crash_month | 1 | 12 |
| crash_day_of_week | 1 | 7 |

The date-related numeric fields fell within their expected ranges.

The `posted_speed_limit` field contained 194 records with a value of zero and several unusual values, such as 2, 3, and 7 mph.

The `num_units` field included extreme values of 16 and 18 traffic units.

These observations were treated as potential anomalies rather than confirmed errors. No values were automatically corrected or removed.

### 2.3 Consistency

Consistency checks examined relationships between injury counts, crash classifications, and date components.

**Injury consistency**

Among 111,807 records with complete injury data:

- No records had fatal injuries exceeding total injuries.
- No records had a mismatch between total injuries and the sum of the four reported injury categories.

**Crash classification consistency**

Three records were identified where:

- `crash_type` was `NO INJURY / DRIVE AWAY`.
- `injuries_total` was 1.
- `injuries_reported_not_evident` was 1.

These records represent potential inconsistencies between crash classification and reported injury information.

Because the correct values could not be determined from the available data, the records were retained and flagged.

**Date consistency**

The following comparisons produced zero mismatches:

- `crash_month` versus the month extracted from `crash_date`
- `crash_hour` versus the hour extracted from `crash_date`
- `crash_day_of_week` versus the weekday extracted from `crash_date`

No duplicate `crash_record_id` values were found.

### 2.4 Timeliness

Timeliness was evaluated by calculating the difference between `crash_date` and `date_police_notified`.

| Check | Result |
|---|---:|
| Police notified before crash | 0 |
| Notification delay exceeding 24 hours | 10,528 |
| Missing notification timestamps | 0 |
| Median notification delay | 0.52 hours |

Approximately 9.40% of crashes had notification delays exceeding 24 hours.

These delays may reflect legitimate late reporting rather than data errors. Therefore, the records were retained and flagged for further analysis.

This assessment measures police notification delay, not the time elapsed between the accident and publication of the record in the data portal.

## 3. Data Cleaning

The cleaning process prioritized preserving original information while identifying potential data quality concerns.

No original records were deleted, and no original values were overwritten.

Three additional columns were created:

| New Column | Description |
|---|---|
| injury_type_conflict | Flags crashes classified as `NO INJURY / DRIVE AWAY` with positive total injuries |
| notification_delay_hours | Calculates hours between crash occurrence and police notification |
| late_notification | Flags notification delays exceeding 24 hours |

Missing values, unknown categories, unusual speed limits, and extreme traffic-unit counts were retained because there was insufficient evidence to correct them reliably.

The original dataset was preserved separately from the processed dataset.

## 4. Post-Cleaning Validation

The processed CSV was reloaded and checked to confirm successful saving and preservation of records.

| Validation Check | Result |
|---|---:|
| Total records | 112,056 |
| Total columns | 52 |
| Duplicate crash IDs | 0 |
| Injury classification conflicts flagged | 3 |
| Notification delays over 24 hours flagged | 10,528 |

The processed dataset preserved all 112,056 original records and added three derived columns.

The validation results confirmed that the expected record count, column count, and quality-flag counts were maintained after saving.

## 5. Output Files

**Original dataset:** `data/raw/crashes_2024.csv`

**Processed dataset:** `data/processed/crashes_2024_clean.csv`

**Assessment script:** `assess_crashes.py`

**Cleaning and validation script:** `clean_crashes.py`

**Acquisition script:** `acquire_data.py`

**Initial data verification script:** `check_crashes.py`

## 6. Limitations and Next Steps

The assessment identified several potential quality concerns, but not all could be conclusively classified as errors.

In particular, unknown categories, unusual speed limits, and delayed police notifications require careful interpretation.

The current cleaning process focuses on quality flagging and derived-variable creation rather than correcting uncertain original values.

Further validation may be necessary during integration with the Vehicles and People datasets, particularly when checking relationships between crash records and related vehicle or person records.

