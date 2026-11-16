
# Interim Status Report
## Chicago Traffic Crashes in 2024

**Course:** IS477 – Fall 2026  
**Team Members:** Stacy, Allen, Zijian, Netsh  
**Milestone:** Interim Status Report

---

## 1. Project Overview


This project examines injury patterns in Chicago traffic crashes during 2024 using three datasets from the Chicago Data Portal: Crashes, Vehicles, and People. We aim to compare injury proportions and severity distributions among pedestrians, cyclists, drivers, and passengers. We also compare injury proportions between passenger-car and SUV occupants.

Our workflow includes data acquisition, quality assessment, cleaning, integration, and analysis. We aim to develop a reproducible process with documented data sources, processing steps, and results.

---

## 2. Progress and Deliverables

### 2.1 Data Acquisition and Verification — Stacy

We used `acquire_data.py` to retrieve three datasets from the Chicago Data Portal, filtered to crashes occurring in 2024: Crashes (112,056 records), Vehicles (228,316 records), and People (246,702 records).

We ran `check_crashes.py` to confirm record counts, column counts, date coverage, and SHA-256 checksums for all three files. We also confirmed that Crashes contained no duplicate `crash_record_id` values. The original files were preserved separately from processed data.

**Artifacts:** [acquire_data.py](acquire_data.py), [check_crashes.py](check_crashes.py)

### 2.2 Crashes Assessment and Cleaning — Stacy

We assessed the Crashes dataset across four quality dimensions:

- **Completeness:** Several work-zone-related fields had over 99% missing values, while `injuries_total` was missing in 249 records (0.22%).
- **Accuracy:** We found 194 records with `posted_speed_limit` equal to zero and two crashes involving 16 or 18 traffic units.
- **Consistency:** Three crashes were classified as `NO INJURY / DRIVE AWAY` despite recording one injury. Checks of injury totals and date components found no mismatches.
- **Timeliness:** Police notification occurred more than 24 hours after the crash in 10,528 records (9.40%).

Because these findings did not establish which original values were incorrect, we preserved all records and added three fields using `clean_crashes.py`: `injury_type_conflict`, `notification_delay_hours`, and `late_notification`. The processed dataset contains 112,056 records and 52 columns. Validation confirmed three injury-conflict flags and 10,528 late-notification flags.

**Artifacts:** [assess_crashes.py](assess_crashes.py), [clean_crashes.py](clean_crashes.py), [Crashes Quality Report](docs/crashes_quality_report.md)

### 2.3 Vehicles Assessment and Cleaning — Allen

We assessed 228,316 Vehicles records across four data quality dimensions:

- **Completeness:** Some `UNIT_TYPE`, `VEHICLE_TYPE`, and `VEHICLE_ID` values were missing; 17,186 records had `VEHICLE_TYPE` marked as `UNKNOWN`.
- **Accuracy:** Vehicle types were standardized, and crash and unit identifiers passed format validation.
- **Consistency:** No duplicate crash-unit IDs, unmatched crash IDs, or conflicting crash dates were found.
- **Timeliness:** All retrieved records had valid dates within 2024, although the API date filter excluded records with missing or invalid dates.

We preserved all records and kept unresolved vehicle types separate rather than inferring missing values. The cleaned dataset contains 136,486 passenger cars, 35,781 SUVs, and 56,049 other or unresolved units.

**Artifacts:** [Vehicles Assessment Python Script](vehicle_assessment.py), [Vehicles Quality Report](vehicles_data_quality_report.md)

### 2.4 People Assessment and Cleaning — Zijian

We assessed all 246,702 People records. Completeness checks identified 39 missing injury classifications (0.016%) and 5,986 missing `vehicle_id` values (2.43%), including 37 drivers. Accuracy and consistency checks found no invalid identifier formats, duplicate person IDs, or unmatched crash records. All 240,716 records with `vehicle_id` matched Vehicles using `crash_record_id + vehicle_id`. Timeliness checks confirmed valid dates within 2024.

Cleaning standardized identifiers and dates, preserved all records, and added injury variables and quality flags. Missing injury classifications remained distinct from no injury. The cleaned output contains 49 columns and passed CSV validation.

**Artifacts:** [Assessment](assess_people.py), [Cleaning](clean_people.py), [Quality Report](docs/people_quality_report.md), [Validation](results/people/validation.csv).

### 2.5 Data Integration and Quality Assessment — Netsh

We used `integrate_data.py` to left-join cleaned People records with Crashes on `crash_record_id` and Vehicles on `crash_record_id + vehicle_id`. We standardized identifier capitalization and used Allen's updated cleaned Vehicles file, which retains `vehicle_id`.

The integrated dataset contains 246,702 records and 72 columns, with no records lost or duplicated. All People records matched Crashes, and 240,716 matched Vehicles. The remaining 5,986 records lacked `vehicle_id`, including 37 drivers who cannot be linked to a vehicle type.

Using `assess_integration.py`, we checked completeness, accuracy, consistency, and timeliness. All eight validation checks passed, including injury-count consistency, date agreement, and identifier uniqueness. For the passenger-car/SUV comparison, 147,010 linked drivers and passengers were in passenger cars and 40,093 were in SUVs.

**Artifacts:** [Integration Script](integrate_data.py), [Assessment Script](assess_integration.py), [Quality Report](docs/integration_quality_report.md), [Validation Results](results/integration/validation.csv).

### 2.6 Initial Analysis and Visualizations — Zijian

Injury mappings and denominator rules are implemented: 246,663 records have known classifications, including 25,706 injured people. These are preparation counts across the full People dataset, not completed research-question comparisons. Group comparisons, severity charts, and passenger-car/SUV analysis remain pending. Next, we will use the validated integrated dataset to compare injury proportions across groups and create the planned visualizations.

**Artifact:** [Classification counts](results/people/injury_classification_counts.csv).

### 2.7 Workflow Automation and Reproducibility — Allen

We automated Vehicles data retrieval, quality assessment, and cleaning using Python and the Chicago Open Data API. The workflow uses `requests` for API pagination and `pandas` for data processing, validation, and export. It successfully processed 228,316 Vehicles records and 112,056 Crashes records.

Remaining work includes integrating the workflow with other team members' scripts, documenting execution instructions, and testing reproducibility across multiple runs.

### 2.8 Metadata and Data Documentation — Stacy

We completed `docs/crashes_quality_report.md`, which documents the assessment results, processing decisions, and validation checks.

The data dictionary and Schema.org Dataset JSON-LD metadata are scheduled for November 24–December 1. The dictionary will define fields, identifiers, and missing-value conventions, while the JSON-LD file will describe dataset sources, coverage, and reuse information.

**Artifact:** [Crashes Quality Report](docs/crashes_quality_report.md)

---

## 3. Updated Project Timeline

| Task | Responsible Member(s) | Current Status | Expected Completion |
|---|---|---|---|
| Project Plan and initial release | All | Completed | Oct. 12 |
| Acquisition and SHA-256 verification | Stacy | Completed | Nov. 3 |
| Crashes assessment and cleaning | Stacy | Completed | Nov. 3 |
| Vehicles assessment and cleaning | Allen | Completed | Nov. 15 |
| People assessment and cleaning | Zijian | Completed; linkage issue resolved | Nov. 15 |
| Data integration | Netsh | Completed | Nov. 15 |
| Post-integration assessment | Netsh | Completed; all checks passed | Nov. 15 |
| Initial analysis and visualizations | Zijian | Injury variables ready; comparisons/charts pending | Nov. 18 target|
| Workflow automation and reproducibility | Allen | Vehicles automation completed; full workflow verification pending | Nov. 30 |
| Data dictionary and metadata | Stacy | Planned | Dec. 1 |
| Final README and documentation | Zijian; all contribute | Planned | Dec. 3 |
| Final workflow verification | All | Planned | Dec. 6 |
| Final release and submission | Stacy; all review | Planned | Dec. 7 |

---

## 4. Changes to the Project Plan

### 4.1 Changes Based on Instructor Feedback

In response to the instructor's feedback, we made our progress descriptions more specific by identifying the methods used, the results obtained, and the remaining tasks. We also distinguished completed work from planned activities to communicate the project's current status more clearly.

### 4.2 Changes to Methods, Scope, or Timeline

The research questions and overall approach remain unchanged. Compared with the initial extracts in the Project Plan, the current Crashes and Vehicles datasets contain one and two fewer records, respectively, while the People record count is unchanged. We recorded the current counts and SHA-256 checksums. The reason for these differences has not been determined.
The interim report deadline was also updated from November 19 to November 16 to match the date listed in Canvas.

---

## 5. Challenges, Solutions, and Next Steps

### 5.1 Challenges and Next Steps — Stacy

The main challenge was deciding how to handle incomplete or potentially inconsistent records without changing valid information. For example, work-zone fields may be blank because they do not apply to a crash, while unusual speed limits and conflicting injury classifications cannot be resolved from the available data.

We therefore retained uncertain values and flagged identifiable conflicts instead of making unsupported corrections. My next tasks are to compile the data dictionary and prepare the JSON-LD metadata. The Crashes assessment results also support the team's completed integration checks and may inform further validation during the final project stage.

### 5.2 Vehicles and Automation — Allen
The main challenges were retrieving large datasets through the API, correcting crash ID validation errors, and handling missing or unknown vehicle types. We addressed these issues through API pagination, revised ID validation logic, and standardized vehicle classifications while preserving unresolved values. Next, we will integrate the automated workflow with the team's other scripts, improve documentation, and test reproducibility.

### 5.3 People and Analysis — Zijian

Missing injury classifications were preserved rather than treated as no injury. The vehicle linkage issue was resolved after Allen updated the cleaned Vehicles file to retain `vehicle_id`. Next, we will complete the injury comparisons and visualizations, contribute field definitions, and prepare the final README.

### 5.4 Integration — Netsh

The main challenge was linking Vehicles because the initial cleaned file lacked `vehicle_id` and identifier capitalization differed across datasets. We standardized ID capitalization and switched to Allen's updated cleaned Vehicles file. All integration checks passed without dropping or duplicating People records. We retained and documented the 46 records without `vehicle_id` that were identified as drivers or non-contact-vehicle records. Next, I will share the integrated dataset through Box, support the vehicle comparison, and add `integrate_data.py` and `assess_integration.py` to the run-all workflow.

### 5.5 Outstanding Issues

- **People deliverables:** Zijian's comparisons and charts remain pending. Input and cleaned data snapshots exceed 50 MB; their course-required shared access still needs coordination with Stacy and Allen.
- **Integrated data:** The integrated file (165 MB) exceeds 50 MB and needs the shared Box link.
- **Unlinked drivers:** 37 drivers lack `vehicle_id` in the source data and will be excluded from the passenger-car/SUV comparison.
  
---

## 6. Individual Contributions

### 6.1 Stacy

I developed the data acquisition and verification scripts, assessed and cleaned the Crashes dataset, and validated the processed output. I documented the findings and committed the scripts and quality report to GitHub. My remaining tasks are preparing the data dictionary and JSON-LD metadata and coordinating the final release.

### 6.2 Allen

I assessed and cleaned the Vehicles dataset and developed a Python workflow for automated data retrieval, quality checks, and processing. I corrected identifier validation issues, standardized vehicle classifications, and produced cleaned data and a quality report to support the team's analysis.

### 6.3 Zijian

I developed the People assessment and cleaning scripts, documented injury classifications, and completed data quality checks, CSV validation, and three regression tests. I also verified vehicle linkage and prepared the quality report. My remaining tasks include comparative analysis, visualizations, field documentation, and the final README.

### 6.4 Netsh

I developed `integrate_data.py` and `assess_integration.py` to combine the cleaned datasets and validate the results without losing or duplicating People records. I documented the integration checks and updated the workflow to use Allen's cleaned Vehicles file. My remaining tasks are sharing the integrated dataset, adding both scripts to the run-all workflow, and documenting integration fields for the data dictionary.

---

## References to Repository Artifacts

- [Project Plan](ProjectPlan.md)
- [Data Acquisition Script](acquire_data.py)
- [Data Verification Script](check_crashes.py)
- [Crashes Assessment Script](assess_crashes.py)
- [Crashes Cleaning Script](clean_crashes.py)
- [Crashes Quality Report](docs/crashes_quality_report.md)

- [People Assessment Script](assess_people.py)
- [People Cleaning Script](clean_people.py)
- [People Quality Report and Run Instructions](docs/people_quality_report.md)
- [People Assessment and Validation Results](results/people/verification_summary.json)
- [People Regression Tests](tests/test_people.py)

- [Integration Script](integrate_data.py)
- [Post-Integration Assessment Script](assess_integration.py)
- [Integration Quality Report and Run Instructions](docs/integration_quality_report.md)
- [Integration Assessment Summary](results/integration/summary.csv)
- [Integration Validation Results](results/integration/validation.csv)

- [Vehicles Assessment Python Script](vehicle_assessment.py)
- [Vehicles Quality Report](vehicles_data_quality_report.md)

