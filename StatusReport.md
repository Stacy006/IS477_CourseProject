
# Interim Status Report
## Chicago Traffic Crashes in 2024

**Course:** IS477 – Fall 2026  
**Team Members:** Stacy, Allen, Zijian, Netsh  
**Milestone:** Interim Status Report

---

## 1. Project Overview

Briefly summarize the project objectives, research questions, datasets, and overall progress.

Focus on:
- Injury outcomes across pedestrians, cyclists, drivers, and passengers
- Injury proportions among passenger-car and SUV occupants
- Progress toward a reproducible data processing and analysis workflow

[All members: Review and complete.]

---

## 2. Progress and Deliverables

Describe completed and ongoing tasks from the Project Plan. Include specific results and links to GitHub artifacts.


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

[Allen: Describe completed quality checks, cleaning methods, results, and relevant artifacts.]

### 2.4 People Assessment and Cleaning — Zijian

[Zijian: Describe completed quality checks, cleaning methods, results, and relevant artifacts.]

### 2.5 Data Integration and Quality Assessment — Netsh

[Netsh: Describe integration progress, join keys, validation results, unresolved matching issues, and relevant artifacts.]

### 2.6 Initial Analysis and Visualizations — Zijian

[Zijian: Describe analysis progress, preliminary results, charts, and relevant artifacts.]

### 2.7 Workflow Automation and Reproducibility — Allen

[Allen: Describe automation progress, dependency management, documentation, and remaining work.]

### 2.8 Metadata and Data Documentation — Stacy

We completed `docs/crashes_quality_report.md`, which documents the assessment results, processing decisions, and validation checks.

The data dictionary and Schema.org Dataset JSON-LD metadata are scheduled for November 24–December 1. The dictionary will define fields, identifiers, and missing-value conventions, while the JSON-LD file will describe dataset sources, coverage, and reuse information.

**Artifact:** [Crashes Quality Report](docs/crashes_quality_report.md)

---

## 3. Updated Project Timeline

| Task | Responsible Member(s) | Current Status | Expected Completion |
|---|---|---|---|
| Project Plan and initial release | All | Completed | Oct. 12 |
| Acquisition and SHA-256 verification | Stacy | Completed | Completed |
| Crashes assessment and cleaning | Stacy | Completed | Completed |
| Vehicles assessment and cleaning | Allen | To be updated | TBD |
| People assessment and cleaning | Zijian | To be updated | TBD |
| Data integration | Netsh | To be updated | TBD |
| Post-integration assessment | Netsh | To be updated | TBD |
| Initial analysis and visualizations | Zijian | To be updated | TBD |
| Workflow automation and reproducibility | Allen | To be updated | Nov. 30 |
| Data dictionary and metadata | Stacy | Planned | Dec. 1 |
| Final README and documentation | Zijian; all contribute | Planned | Dec. 3 |
| Final workflow verification | All | Planned | Dec. 6 |
| Final release and submission | Stacy; all review | Planned | Dec. 7 |

[All members: Confirm task statuses and revise dates if needed.]

---

## 4. Changes to the Project Plan

### 4.1 Changes Based on Instructor Feedback

The instructor's feedback on Milestone 2 was generally positive but identified opportunities to improve clarity and relevance in the writing.

[All members: Explain how the current report uses more specific descriptions of methods, results, and deliverables.]

### 4.2 Changes to Methods, Scope, or Timeline

[All members: Document any actual changes to the original plan, explain why they were necessary, and identify their effects. If no major changes occurred, state that clearly.]

---

## 5. Challenges, Solutions, and Next Steps

### 5.1 Challenges and Next Steps — Stacy

The main challenge was deciding how to handle incomplete or potentially inconsistent records without changing valid information. For example, work-zone fields may be blank because they do not apply to a crash, while unusual speed limits and conflicting injury classifications cannot be resolved from the available data.

We therefore retained uncertain values and flagged identifiable conflicts instead of making unsupported corrections. Next, we will complete the data dictionary and metadata and check for additional issues during dataset integration.

### 5.2 Vehicles and Automation — Allen

[Allen: Add challenges, solutions, and next steps.]

### 5.3 People and Analysis — Zijian

[Zijian: Add challenges, solutions, and next steps.]

### 5.4 Integration — Netsh

[Netsh: Add challenges, solutions, and next steps.]

### 5.5 Outstanding Issues

[All members: Summarize unresolved issues, responsible members, and planned actions.]

---

## 6. Individual Contributions

Each member should write and commit their own contribution summary using their GitHub account.

### 6.1 Individual Contributions — Stacy

I developed the acquisition and verification scripts, assessed the Crashes dataset, created the quality flags, and validated the processed output. I also documented the findings and committed the scripts and report to GitHub. My remaining responsibilities are compiling the data dictionary, preparing JSON-LD metadata, and coordinating the final release.
### Allen

[Allen: Add personal contribution summary.]

### Zijian

[Zijian: Add personal contribution summary.]

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

[Add links to other completed artifacts.]
