
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

We used `integrate_data.py` to left-join cleaned People (246,702 records) to Crashes on `crash_record_id` and to Vehicles on `crash_record_id + vehicle_id`, using only Vehicles records with a `vehicle_id`. We checked that join keys were unique and row counts unchanged, so every People record appears once. IDs were uppercased on all sides first, because Crashes and Vehicles store them in lowercase. Allen's cleaned Vehicles file first dropped `vehicle_id`, so we initially joined raw Vehicles. After Allen updated `vehicle_assessment.py` to keep `vehicle_id`, we switched `integrate_data.py` to his cleaned file and reran all checks with the same results. `assess_integration.py` checked the result:

- **Accuracy:** Linked crash dates agreed for every record. Person-level injury counts matched `injuries_total` and each severity field for all 111,807 crashes with injury data. The other 249 crashes have no People records.
- **Completeness:** All People matched Crashes, and 240,716 matched Vehicles; no record with a `vehicle_id` failed to match. 5,940 pedestrians, cyclists, and non-motor-vehicle records have no vehicle by design. 37 drivers and 9 non-contact-vehicle records lack a `vehicle_id` in the source.
- **Timeliness:** All dates fall in 2024. We downloaded the data on Nov. 15, 2026. People was last updated one day before Crashes and Vehicles, with no effect on links.
- **Consistency:** Person, crash, unit, and crash–vehicle IDs are unique, with no unusual formats. Row counts did not change after either join.

The integrated dataset has 246,702 records and 72 columns. For RQ2, 147,010 linked drivers and passengers were in passenger cars and 40,093 in SUVs. We excluded 53,595 in other or unknown vehicle types and 37 without a vehicle link. All eight validation checks passed.

**Artifacts:** [integration](integrate_data.py), [assessment](assess_integration.py), [quality report](docs/integration_quality_report.md), [validation](results/integration/validation.csv).
### 2.6 Initial Analysis and Visualizations — Zijian

Injury mappings and denominator rules are implemented: 246,663 records have known classifications, including 25,706 injured people. These are preparation counts across the full People dataset, not completed research-question comparisons. Group comparisons, severity charts, and passenger-car/SUV analysis remain pending. Next, we will produce group tables and charts and use Netsh's validated integrated output for vehicle comparisons.

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

The research questions and overall approach remain unchanged. The current data extracts contain 112,056 Crashes records and 228,316 Vehicles records, compared with 112,057 and 228,318 in the initial extracts documented in the Project Plan. The People dataset remains at 246,702 records. We recorded the current counts and SHA-256 checksums to document the files used in this stage. The reason for the small differences has not been determined.
The interim report deadline was also updated from November 19 to November 16 to match the date listed in Canvas.

---

## 5. Challenges, Solutions, and Next Steps

### 5.1 Challenges and Next Steps — Stacy

The main challenge was deciding how to handle incomplete or potentially inconsistent records without changing valid information. For example, work-zone fields may be blank because they do not apply to a crash, while unusual speed limits and conflicting injury classifications cannot be resolved from the available data.

We therefore retained uncertain values and flagged identifiable conflicts instead of making unsupported corrections. My next tasks are to compile the data dictionary and prepare the JSON-LD metadata. The Crashes assessment results will also support the team's subsequent integration checks.

### 5.2 Vehicles and Automation — Allen
During the Vehicles assessment and cleaning process, the main challenges included retrieving large datasets through the API, correcting Crash ID validation errors, and handling missing or unknown Vehicle Type classifications. To address these issues, we implemented API pagination to retrieve 228,316 vehicle records, corrected the ID validation logic, and standardized vehicle classifications while preserving unresolved values to avoid affecting subsequent analysis. Additionally, we developed an automated Python workflow for data retrieval, quality assessment, cleaning, and export, reducing manual processing. Moving forward, we plan to integrate the cleaned vehicle data with other team datasets, verify workflow reproducibility, and improve documentation and error handling to enhance efficiency and reliability.

### 5.3 People and Analysis — Zijian

Missing injury classifications must not be treated as no injury, so nullable injury fields were preserved. Vehicle linkage initially required additional validation because of identifier differences. This issue was resolved after Allen updated the cleaned Vehicles file to retain `vehicle_id`, allowing integration to use the processed data. Next, we will complete the group comparisons and charts, contribute field definitions, and prepare the final README.

### 5.4 Integration — Netsh

The main challenge was linking Vehicles. Allen's cleaned file first dropped `vehicle_id`, and Crashes and Vehicles store IDs in lowercase while cleaned People uses uppercase, so a direct join would match nothing. We uppercased IDs on all sides and, at first, joined raw Vehicles using Allen's vehicle-type rule. Allen then updated `vehicle_assessment.py` to keep `vehicle_id`, so I switched `integrate_data.py` to his cleaned file; all counts and checks stayed the same. We kept and labeled the 46 People records without a `vehicle_id` instead of dropping them. Next, I will share the 162 MB integrated file through Box, support Zijian's vehicle comparison, and add both scripts to the run-all workflow.

### 5.5 Outstanding Issues

- **People deliverables:** Zijian's comparisons and charts remain pending. Input and cleaned data snapshots exceed 50 MB; their course-required shared access still needs coordination with Stacy and Allen.
- **Integrated data:** The integrated file (165 MB) exceeds 50 MB and needs the shared Box link.
- **Unlinked drivers:** 37 drivers have no `vehicle_id` in the source and are excluded from the vehicle comparison.

---

## 6. Individual Contributions

### 6.1 Stacy

I developed the acquisition and verification scripts, assessed the Crashes dataset, created the quality flags, and validated the processed output. I also documented the findings and committed the scripts and report to GitHub. My remaining responsibilities are compiling the data dictionary, preparing JSON-LD metadata, and coordinating the final release.

### 6.2 Allen
I was responsible for the Vehicles dataset's data quality assessment, data cleaning, and workflow automation. Using Python and the Chicago Open Data API, I developed an automated data retrieval and processing workflow to assess accuracy, completeness, consistency, and timeliness. I also resolved ID validation issues and standardized vehicle classifications. The final deliverables include cleaned datasets and quality reports to support the team's subsequent analysis.

### 6.3 Zijian

I am responsible for the People assessment and cleaning scripts, documented injury mappings, and quality reports. This milestone includes full-data checks, CSV validation, and three regression tests. I documented missing classifications and verified vehicle linkage. Remaining work includes comparative analysis, visualizations, People field documentation, and compiling the final README.

### 6.4 Netsh

I am responsible for integrating the cleaned datasets and assessing the integrated data. I wrote `integrate_data.py`, which joins People to Crashes and Vehicles without dropping or duplicating records, and `assess_integration.py`, which checks accuracy, completeness, timeliness, and consistency and saves the results. I also wrote the integration quality report and switched integration to Allen's cleaned Vehicles file once it kept `vehicle_id`. Remaining work includes sharing the integrated file, adding both scripts to the run-all workflow, and documenting integration fields for the data dictionary.

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

