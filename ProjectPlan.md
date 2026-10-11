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

We will follow the USGS Science Data Lifecycle introduced in Week 1. Planning will define our questions and responsibilities; acquisition will obtain the three datasets; processing will cover quality assessment, cleaning, and integration; analysis will produce tables and charts. We will preserve the data snapshots, scripts, and documentation and share the project through GitHub releases. Documentation, quality management, and backups will support all stages.

Acquisition scripts will retrieve records with crash dates from January 1, 2024, up to but excluding January 1, 2025. We will record source URLs, retrieval dates, filtering conditions, and row counts. SHA-256 checksums will identify the acquired files and allow later copies to be checked against the saved snapshots. As the source data may change, a new download may have a different checksum.

The datasets are tabular CSV files containing identifiers, categorical values, numeric values, and dates. We will preserve identifiers as strings and store unchanged source files in data/raw/, cleaned files in data/cleaned/, and integrated files in data/integrated/. Scripts will be stored in scripts/, tables and charts in results/, and metadata and the data dictionary in docs/. All scripts will use relative paths.

### Overall Assessment and Cleaning

Before integration, we will assess each dataset for accuracy, completeness, timeliness, and consistency. Checks will examine valid values and ranges, missing data, coverage of the 2024 study period, duplicate identifiers, and consistent formats and categories. These checks can identify potential errors but cannot independently confirm every recorded crash detail.

Cleaning will address the issues found through assessment. We will standardize formats where needed, investigate duplicates and invalid values, and distinguish missing information from fields that do not apply to a record. We will document each cleaning decision and the number of affected records, preserve the raw files, and reassess the cleaned data before integration.

### Crashes Assessment and Cleaning

For accuracy, we will check that injury counts are non-negative integers and that INJURIES_TOTAL agrees with the sum of the fatal, incapacitating, non-incapacitating, and reported-but-not-evident injury counts. For completeness, we will measure missingness in CRASH_RECORD_ID, CRASH_DATE, and injury summary fields. For timeliness, we will confirm that crash dates within fall 2024 and record the retrieval date, noting that historical records may be revised. For consistency, we will check identifier uniqueness, date formats, and agreement between CRASH_DATE and CRASH_MONTH.

Preliminary checks found no missing or duplicate CRASH_RECORD_ID values and confirmed that all crash dates fall within 2024. We will standardize date and numeric formats as needed and investigate any invalid counts or inconsistencies. Missing injury counts will not automatically be replaced with zero. Corrections or exclusions will be documented, and unresolved issues will be flagged before integration.

### Vehicles Assessment and Cleaning

We will examine the Traffic Crashes Vehicles data set to understand the data structure, including number of observations, data types, and important variables that is highly related to crashes such as VEHICLE_TYPE, MAKE, and MODEL. Then, four aspect of data value will be evaluated, which is completeness, uniqueness, consistency, and validity. These aspects includes checking the completeness of the data set, including the existence of missing values, especially important variables such as MODEL, MAKE, and vehicles types. We will also be checking whether there are repetitive observations using CRASH_RECORD_ID and VEHICLE_ID as references to prevents its affect on accuracy. Checking consistency of classification criteria and data format and ensuring that each variables actually presents data in a reasonable ranges such if unreasonable data or outlier exist are what we will be performing for the later two aspect. 

### People Assessment and Cleaning

(Zijian: Outline quality checks across the four required dimensions and planned cleaning methods based on the agreed research questions.)

### Integration and Post-Integration Assessment

(Netsh: Outline the integration approach, join keys, and post-integration checks across the four required quality dimensions.)

### Automation, Reproducibility, and Ethics

We plan to use python to automatically collect data, clean data, and integrate data to reduce manual error and improve efficiency. We will organize the code into reusable function, ensuring that processing to be consistant. To enure that the result will be reproducable, we will present data source, data cleaning process, and method of analysis. Meanwhile, we will also use GitHub to tract the modification of codes and files. Allowing other to trace back from result. In the aspect of ethics, we will use crash data from public and ensure that the usage comply with applicable requirements. Moreover, we will try to avoid identifying the identy of the individual in the observation and present our results in an agregated manner as much as we can.

### Metadata and Data Documentation

We will create a data dictionary in docs/ describing field names, meanings, data types, identifiers, category values, and missing-value conventions for the fields used in our project. Each member will document their own dataset, and Stacy will compile these descriptions and document derived fields, including road-user groups and injury indicators.

We will also create a machine-readable metadata file in JSON-LD using Schema.org Dataset. It will describe the project title, purpose, contributors, data sources, temporal and spatial coverage, file formats, access locations, and applicable data-use terms. The documentation will explain how the datasets are linked and how derived variables are calculated to support understanding and reuse.

## Timeline

(Netsh: Add a table with target date, task description/deliverable, and responsible member. Schedule acquisition, pre-integration assessment, cleaning, integration, post-integration assessment, analysis, run-all verification, metadata, and report review. Course milestones: Project Plan October 12, Status Report November 19, Final Project December 7, 2026. Check exact times in Canvas and allow time for feedback and corrections.)

## Constraints

(Zijian: Describe limitations and challenges based on the agreed research questions and datasets.)

## Gaps

(Netsh: Identify unresolved questions and needed instructor input, including whether three distinct datasets from one publisher satisfy the source requirement. Coordinate with Allen on reuse terms and automated acquisition, and with Zijian on category definitions and structural missingness. Explain that full quality checks and end-to-end reproduction remain future work and that the plan will be updated after feedback.)
