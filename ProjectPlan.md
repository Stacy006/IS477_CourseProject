# Project Plan: Chicago Traffic Crashes in 2024

## Overview

This project will examine injury outcomes among people involved in recorded Chicago traffic crashes  in 2024. We will compare injury proportions and injury severity among pedestrians, cyclists, drivers and passengers. We will also compare injury proportions among occupants of passenger cars and SUVs.

We will integrate three datasets from the Chicago Data Portal: Traffic Crashes - Crashes, Vehicles, and People. These datasets provide complementary information about crash circumstances, vehicle types, and individual injury outcomes.

Our main focus is building a documented and reproducible data curation workflow. We will acquire and preserve the raw CSV files, assess each dataset for accuracy, completeness, timeliness, and consistency, and clean the issues identified. We will then link the cleaned datasets using crash and vehicle identifiers and assess the integrated data for missing matches, duplicate records, and inconsistent values. Separate Python scripts connected by a run-all script will reproduce the workflow from acquisition through analysis.

The final analysis will use summary tables and bar charts. We will document data sources, cleaning decisions, limitations, and field definitions to support reuse. Our findings will describe injury outcomes within recorded crashes, rather than the overall risk of traveling by each mode.

## Team

Each member will write the report sections and field descriptions for their own work and dataset and commit their contributions through their own GitHub account. Stacy will compile the field descriptions into the data dictionary. All four members will review the final report and documentation together. Compiling the report means organizing everyone’s completed sections, rather than writing unfinished sections for others.

| Member | Planned responsibilities |
| --- | --- |
| Stacy | Write acquisition scripts to download all three datasets filtered to 2024 and record SHA-256 checksums; assess and clean the Crashes data; compile the data dictionary and prepare a machine-readable metadata file; create GitHub releases and submit the project. |
| Allen | Assess and clean the Vehicles data; review and document data-use terms and add a software license; build the run-all script, document dependencies and reproduction steps, and verify the workflow on a fresh clone. |
| Zijian | Assess and clean the People data; conduct the analysis and create charts; compile each member’s completed report sections into the final README.md. |
| Netsh | Merge the cleaned datasets; assess the quality of the integrated data; document the integration methods and quality-check results. |

## Research Questions

We will address two research questions:

1. How do injury proportions and the distribution of injury severity differ among pedestrians, cyclists, drivers, and passengers involved in recorded Chicago traffic crashes in 2024?
2. Among drivers and passengers, how do injury proportions differ between those in passenger cars and those in SUVs?

These groups correspond to the PEDESTIRAN, BICYCLE, DRIVER and PASSENGER values in the People dataset. Passenger cars and SUVs will be identified using the PASSENGER and SPORT UTILITY VEHICLE (SUV) values in the Vehicles dataset's VEHICLE_TYPE field.

For each group, the injury proportion will be calculated as the number of people with a recorded injury divided by the number with a known injury classification. Missing injury classifications will be reported separately. These comparisons describe outcomes among people involved in recorded crashes, rather than the overall risk of traveling by each mode.

### Planned Analysis Approach

(Zijian: Based on the agreed research questions, describe the planned analysis methods, relevant variables, and visualizations. Explain any definitions or calculations needed to answer the questions.)

## Datasets and Planned Workflow

### Sources and Preliminary Feasibility

We downloaded initial CSV extracts on October 7, 2026, filtered to crash dates on or after January 1, 2024, and before January 1, 2025.

The Crashes extract contains only 2024 dates, exceeds 100 records, and has unique, non-missing CRASH_RECORD_ID values. No Kaggle data will be used.

| Official dataset | Initial extract | Contribution and identifiers |
| --- | --- | --- |
| [Traffic Crashes – Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if) | 112,057 rows; 49 columns | Each row represents a recorded crash. CRASH_RECORD_ID identifies each crash and links it to the Vehicles and People datasets. Relevant fields include CRASH_DATE, WEATHER_CONDITION, LIGHTING_CONDITION, FIRST_CRASH_TYPE, and injury summary fields such as INJURIES_TOTAL. This dataset defines the 2024 crash scope and provides crash-level context. Its injury totals will also be compared with aggregated People records as a consistency check, with any discrepancies investigated and documented.  |
| [Traffic Crashes – Vehicles](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3) | 228,318 rows; 71 columns | (Allen: Describe crash-unit records, relevant vehicle fields, CRASH_UNIT_ID, VEHICLE_ID, and CRASH_RECORD_ID. Explain how this dataset contributes information beyond Crashes and People.) |
| [Traffic Crashes – People](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d) | 246,702 rows; 29 columns | (Zijian: Describe person records, PERSON_ID, occupant roles, injury classification, and vehicle/crash identifiers. Explain how this dataset supports the research questions.) |

### Cross-Dataset Feasibility

(Netsh: Explain how the datasets complement each other, their shared identifiers, and preliminary evidence that they can be integrated.)

### Lifecycle, Acquisition, and Organization

(Stacy: Describe the lifecycle model, data acquisition, SHA-256 checks, and file organization.)

### Overall Assessment and Cleaning

(Stacy: Briefly introduce the assessment and cleaning workflow, covering accuracy, completeness, timeliness, and consistency.)

### Crashes Assessment and Cleaning

(Stacy: Outline quality checks across the four required dimensions and planned cleaning methods.)

### Vehicles Assessment and Cleaning

(Allen: Outline quality checks across the four required dimensions and planned cleaning methods.)

### People Assessment and Cleaning

(Zijian: Outline quality checks across the four required dimensions and planned cleaning methods based on the agreed research questions.)

### Integration and Post-Integration Assessment

(Netsh: Outline the integration approach, join keys, and post-integration checks across the four required quality dimensions.)

### Automation, Reproducibility, and Ethics

(Allen: Outline workflow automation, reproduction steps, data-use terms, and the software license.)

### Metadata and Data Documentation

(Stacy: Outline plans for the data dictionary and standard-based machine-readable metadata.)

## Timeline

(Netsh: Add a table with target date, task description/deliverable, and responsible member. Schedule acquisition, pre-integration assessment, cleaning, integration, post-integration assessment, analysis, run-all verification, metadata, and report review. Course milestones: Project Plan October 12, Status Report November 19, Final Project December 7, 2026. Check exact times in Canvas and allow time for feedback and corrections.)

## Constraints

(Zijian: Describe limitations and challenges based on the agreed research questions and datasets.)

## Gaps

(Netsh: Identify unresolved questions and needed instructor input, including whether three distinct datasets from one publisher satisfy the source requirement. Coordinate with Allen on reuse terms and automated acquisition, and with Zijian on category definitions and structural missingness. Explain that full quality checks and end-to-end reproduction remain future work and that the plan will be updated after feedback.)
