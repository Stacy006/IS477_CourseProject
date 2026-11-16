
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
We assessed the Vehicles dataset across four data quality dimensions:
- **Completeness**: There are no missing vehicle IDs, crash IDs, or dates. 162 records which is roughly 0.07% had missing UNIT_TYPE, while 6155 had blank VEHICLE_TYPE and 17186(7.53%) were marked UNKNOWN
- **Accuracy:** Vehicle types are standardized and other variables passed format validation
-  **Consistency:** There are no duplicate vehicle IDS, unmatched crash IDs, or conflicting crash dates were identified
-  **Timeliness:** The records are within 2024 and all of the dates are valid. The API files had automatically excluded records without date that can be used.

The missing vehicle types can not be inferred accurately. Therefore, we have preserved all records, standardized categories, and separated unresolved values. The cleaned dataset contains 228,316 records, classified into 136,486 passenger cars, 35,781 SUV, and 56,049 other units.

**Artifacts:** vehicles_2024_cleaned.csv, cars_vs_suvs_2024.csv, quality_summary.csv, and vehicle/unit type frequency reports.

### 2.4 People Assessment and Cleaning — Zijian

We assessed all 246,702 People records. Accuracy checks found no unrecognized person/injury categories or unusual identifier formats. Completeness checks found 39 missing injury classifications (0.016%) and 5,986 missing vehicle IDs (2.43%), including 37 drivers. Timeliness checks confirmed valid dates throughout 2024. Consistency checks found no duplicate person IDs; all records matched Crashes, and all 240,716 records with vehicle IDs matched Vehicles using `crash_record_id + vehicle_id`, with no linked-date conflicts.

Cleaning standardized identifiers and dates, retained all records, and added injury variables and quality flags. Unknown injuries remain separate from no injury. The output has 49 columns; CSV round-trip validation passed.

**Artifacts:** [Assessment](assess_people.py), [cleaning](clean_people.py), [quality report](docs/people_quality_report.md), [validation](results/people/validation.csv).

### 2.5 Data Integration and Quality Assessment — Netsh

[Netsh: Describe integration progress, join keys, validation results, unresolved matching issues, and relevant artifacts.]

### 2.6 Initial Analysis and Visualizations — Zijian

Injury mappings and denominator rules are implemented: 246,663 records have known classifications, including 25,706 injured people. These are preparation counts across the full People dataset, not completed research-question comparisons. Group comparisons, severity charts, and passenger-car/SUV analysis remain pending. Next, we will produce group tables and charts and use Netsh's validated integrated output for vehicle comparisons.

**Artifact:** [Classification counts](results/people/injury_classification_counts.csv).

### 2.7 Workflow Automation and Reproducibility — Allen

We have automated the Vehicles data assessment and the cleaning process using Python and the Chicago Open Data. 
Automation: Python automatically retrievces 2024 Vehicles and Crashes records through API pagination, performs quality checks, standardizes data, and exports cleaned datasets and reports.
Dependency Management: The workflow uses libraries such as pandas for data processing and requests for API access. 
Documentation: The python script contains organized steps for data retrieval, validation, cleaning, and exporting results.
Remaining Work: Integrate the workflow with other team members datasets, documentation execution instructions, and verify reproducibility across runs

The automated process is successful. 228316 vehicle records and 112056 crash records are retrieved.

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
| People assessment and cleaning | Zijian | Completed; integration follow-up pending | Nov. 15 |
| Data integration | Netsh | To be updated | TBD |
| Post-integration assessment | Netsh | To be updated | TBD |
| Initial analysis and visualizations | Zijian | Injury variables ready; comparisons/charts pending | Nov. 18 target; depends on integration |
| Workflow automation and reproducibility | Allen | To be updated | Nov. 30 |
| Data dictionary and metadata | Stacy | Planned | Dec. 1 |
| Final README and documentation | Zijian; all contribute | Planned | Dec. 3 |
| Final workflow verification | All | Planned | Dec. 6 |
| Final release and submission | Stacy; all review | Planned | Dec. 7 |

[All members: Confirm task statuses and revise dates if needed.]

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
In the vehicles assessment and cleaning process, the major challenge that are met includes getting large API data, crash ID validation format error, and some vehicle type includes missing values and unknown classification problems. To solve this, we use API pagination and retrieved 228316 vehicle records, fix id validation decision. We have also use data standardization to unify vehicle type's format while we preserve data that classification are unable to be done to reduce effect on future analysis. Moreover, we uses python to build automated workflow, allowing data retrieval, quality assessment, data cleaning, and data export to be done automoatically, reducing manual processing. We will be organizing cleaned vehicle data and ensure workflow reproduciblity. We will also improve documentation and error handling, which can help improve effeciency and relaibility.

### 5.3 People and Analysis — Zijian

Missing injury classifications must not become no injury. Nullable injury fields preserve this distinction. Vehicle metadata also suggested a different identifier; actual matching confirmed the plan's `vehicle_id` linkage. Allen's current export omits this field, so assessment uses raw Vehicles. Next, coordinate its retention and consistent ID formatting with Allen and Netsh, complete comparisons and charts, and contribute field definitions and the final README.

### 5.4 Integration — Netsh

[Netsh: Add challenges, solutions, and next steps.]

### 5.5 Outstanding Issues

- **People/vehicle linkage:** Allen and Netsh need to retain `vehicle_id` and normalize IDs on both sides before integration.
- **People deliverables:** Zijian's comparisons and charts remain pending. Input and cleaned data snapshots exceed 50 MB; their course-required shared access still needs coordination with Stacy and Allen.

[Other members: Add remaining issues and planned actions.]

---

## 6. Individual Contributions

Each member should write and commit their own contribution summary using their GitHub account.

### 6.1 Individual Contributions — Stacy

I developed the acquisition and verification scripts, assessed the Crashes dataset, created the quality flags, and validated the processed output. I also documented the findings and committed the scripts and report to GitHub. My remaining responsibilities are compiling the data dictionary, preparing JSON-LD metadata, and coordinating the final release.
### Allen
I am responsible for vehicles dataset's data quality assessment, data cleaning and workflow automation. Through python and Chicago open data, I have built automatic data retrieval and organizing processes, which finished checking on accuracy, completeness, consistency, and timeliness. I have also solve ID validation and vehicle type classification problem. The final result are cleaned dataset and quality reports, which ensure data quality and support team analysis in the future. 
[Allen: Add personal contribution summary.]

### Zijian

I am responsible for the People assessment and cleaning scripts, documented injury mappings, and quality reports. This milestone includes full-data checks, CSV validation, and three regression tests. I documented missing classifications and verified vehicle linkage. Remaining work includes comparative analysis, visualizations, People field documentation, and compiling the final README.

### Netsh

[Netsh: Add personal contribution summary.]

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

[Add links to other completed artifacts.]

