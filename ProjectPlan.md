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

We will conduct a descriptive analysis at the person-record level. We will first use PERSON_TYPE to classify records into four road-user groups: pedestrians, cyclists, drivers, and passengers. For each group, we will report the total number of records, the number with a known injury classification, the number recorded as injured, and the number with a missing or unknown injury classification.

The injury proportion will be calculated as the number of people classified as having a fatal, incapacitating, non-incapacitating, or reported-but-not-evident injury divided by the number of people with a known injury classification. Records with missing or unknown injury classifications will not be treated as uninjured and will be reported separately. Among injured people, we will also calculate the distribution of injury severity to compare the relative frequency of fatal, incapacitating, non-incapacitating, and reported-but-not-evident injuries across the four road-user groups.

To address the second research question, we will restrict the analysis to drivers and passengers whose People records can be linked to Vehicles records. We will use CRASH_RECORD_ID together with People.VEHICLE_ID and Vehicles.CRASH_UNIT_ID to associate each person with a crash unit. We will then compare injury proportions for occupants of vehicles classified as PASSENGER and SPORT UTILITY VEHICLE (SUV).

Results will be presented in summary tables and bar charts. A grouped bar chart will compare injury proportions across pedestrians, cyclists, drivers, and passengers; a proportional stacked bar chart will show injury-severity distributions among injured people; and a separate grouped bar chart will compare passenger-car and SUV occupants. We will display record counts together with percentages and report missing classifications and unmatched vehicle records. The analysis will be descriptive and will not be interpreted as measuring travel risk or establishing causal effects.

## Datasets and Planned Workflow

### Sources and Preliminary Feasibility

We downloaded initial CSV extracts on October 7, 2026, filtered to crash dates on or after January 1, 2024, and before January 1, 2025.

The Crashes extract contains only 2024 dates, exceeds 100 records, and has unique, non-missing CRASH_RECORD_ID values. No Kaggle data will be used.

| Official dataset | Initial extract | Contribution and identifiers |
| --- | --- | --- |
| [Traffic Crashes – Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if) | 112,057 rows; 49 columns | Each row represents a recorded crash. CRASH_RECORD_ID identifies each crash and links it to the Vehicles and People datasets. Relevant fields include CRASH_DATE, WEATHER_CONDITION, LIGHTING_CONDITION, FIRST_CRASH_TYPE, and injury summary fields such as INJURIES_TOTAL. This dataset defines the 2024 crash scope and provides crash-level context. Its injury totals will also be compared with aggregated People records as a consistency check, with any discrepancies investigated and documented.  |
| [Traffic Crashes – Vehicles](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3) | 228,318 rows; 71 columns | (Allen: Describe crash-unit records, relevant vehicle fields, CRASH_UNIT_ID, VEHICLE_ID, and CRASH_RECORD_ID. Explain how this dataset contributes information beyond Crashes and People.) |
| [Traffic Crashes – People](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d) | 246,702 rows; 29 columns |Each row represents one person involved in a recorded crash, including drivers, passengers, pedestrians, and cyclists. PERSON_ID uniquely identifies the person record, CRASH_RECORD_ID links the person to the corresponding crash, and VEHICLE_ID corresponds to CRASH_UNIT_ID in the Vehicles dataset. Relevant fields include PERSON_TYPE, CRASH_DATE, VEHICLE_ID, SEAT_NO, AGE, SEX, SAFETY_EQUIPMENT, and INJURY_CLASSIFICATION. This dataset provides the person-level road-user roles and injury outcomes needed for both research questions. It allows us to compare injury outcomes across pedestrians, cyclists, drivers, and passengers and, after integration with Vehicles, to compare occupants of passenger cars and SUVs.|

### Cross-Dataset Feasibility

The three City of Chicago datasets complement each other because they provide different information about the same traffic crashes. The Crashes dataset contains crash dates, locations, road conditions, and injury totals. The Vehicles dataset provides details about the crash units involved, while the People dataset includes drivers, passengers, pedestrians, and injury classifications.

All three datasets share `CRASH_RECORD_ID`, which allows us to connect records belonging to the same crash. Vehicles also contains `CRASH_UNIT_ID` to identify individual units, while People contains `PERSON_ID` to identify individuals. We plan to use `People.VEHICLE_ID` and `Vehicles.CRASH_UNIT_ID` to connect people with specific crash units, after validating this relationship in the data.

Our initial extracts contain 112,057 crash records, 228,318 vehicle/unit records, and 246,702 person records. The Crashes dataset has unique, non-missing crash identifiers and contains records from 2024. These shared identifiers suggest that integration is feasible, although we still need to assess missing values, duplicate records, and matching rates across all three datasets.


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

For accuracy, we will verify that CRASH_DATE falls within 2024 and that PERSON_TYPE and INJURY_CLASSIFICATION contain documented or explainable values. We will review the ranges and formats of fields used in the analysis and investigate invalid ages, malformed identifiers, and unexpected injury or road-user categories. After integration, aggregated person-level injury counts will be compared with the injury-summary fields in the Crashes dataset. Differences will be investigated rather than automatically treated as errors because the datasets may be updated at different times.

For completeness, we will calculate missing-value counts and percentages for PERSON_ID, CRASH_RECORD_ID, VEHICLE_ID, PERSON_TYPE, CRASH_DATE, and INJURY_CLASSIFICATION. We will distinguish genuinely missing information from values that are not applicable to a particular type of person. Missing or unknown injury classifications will be reported separately and will not be recoded as no injury.

For timeliness, we will confirm that the extract covers crashes from January 1 through December 31, 2024 and record the acquisition date. Because the source is updated over time and fatalities may be added after the original crash report, we will treat the downloaded files as dated snapshots and document this limitation.

For consistency, we will test whether PERSON_ID is unique, identify exact duplicate records, standardize date and categorical formats, and examine spelling or capitalization differences in PERSON_TYPE and INJURY_CLASSIFICATION. We will also check that each CRASH_RECORD_ID matches a Crashes record and that People.VEHICLE_ID matches Vehicles.CRASH_UNIT_ID within the same crash where a vehicle linkage is expected.

Cleaning will preserve the raw data and create a separate cleaned file. We will parse dates into a consistent format, preserve identifiers as strings, trim unnecessary whitespace, standardize equivalent category labels, and convert documented missing-value codes to a consistent null representation. Duplicate records will be removed only after their identifiers and contents have been investigated. We will create documented derived fields for road-user group, known injury classification, injury status, and injury severity. The cleaning script will record the number of affected records and produce checks that can be rerun as part of the automated workflow.
### Integration and Post-Integration Assessment

After each team member cleans their assigned dataset, we will integrate the three datasets using Python and Pandas. The main join key will be `CRASH_RECORD_ID`, which connects records from the same crash. When linking people to specific crash units, we will also use `People.VEHICLE_ID` and `Vehicles.CRASH_UNIT_ID`, while checking that the crash identifiers match.

Since a single crash can involve multiple vehicles and people, we will use appropriate one-to-many relationships to avoid incorrectly duplicating records. We plan to create integrated tables at the crash, unit, and person levels so that our analysis can accurately count crashes, vehicles, and injuries.

After integration, we will evaluate the data using the four required quality dimensions:

- **Accuracy:** Check whether linked records contain reasonable values and whether information such as crash dates and injury counts is consistent across datasets.
- **Completeness:** Identify missing values, unmatched records, and missing identifiers. Calculate the percentage of records successfully matched across datasets.
- **Timeliness:** Confirm that the integrated data represents crashes occurring in 2024 and document when the data was acquired.
- **Consistency:** Check for duplicate identifiers, inconsistent formats, and unexpected changes in record counts after merging.

We will compare record counts before and after integration, document matching rates, and investigate any unexpected duplicates or unmatched records. These checks will help determine whether the integration was reasonably successful.

The integration process will be documented in a reproducible Python script with relative file paths. We will also prepare a summary of the integration methods, quality assessment results, and remaining limitations for the final report.


### Automation, Reproducibility, and Ethics

We plan to use python to automatically collect data, clean data, and integrate data to reduce manual error and improve efficiency. We will organize the code into reusable function, ensuring that processing to be consistant. To enure that the result will be reproducable, we will present data source, data cleaning process, and method of analysis. Meanwhile, we will also use GitHub to tract the modification of codes and files. Allowing other to trace back from result. In the aspect of ethics, we will use crash data from public and ensure that the usage comply with applicable requirements. Moreover, we will try to avoid identifying the identy of the individual in the observation and present our results in an agregated manner as much as we can.

### Metadata and Data Documentation

We will create a data dictionary in docs/ describing field names, meanings, data types, identifiers, category values, and missing-value conventions for the fields used in our project. Each member will document their own dataset, and Stacy will compile these descriptions and document derived fields, including road-user groups and injury indicators.

We will also create a machine-readable metadata file in JSON-LD using Schema.org Dataset. It will describe the project title, purpose, contributors, data sources, temporal and spatial coverage, file formats, access locations, and applicable data-use terms. The documentation will explain how the datasets are linked and how derived variables are calculated to support understanding and reuse.

## Timeline

| Target Date | Task Description / Deliverable | Responsible Member(s) |
|---|---|---|
| October 12, 2026 | Complete and submit ProjectPlan.md and create the project-plan GitHub release | All; Stacy submits |
| October 13–20 | Review instructor feedback, finalize acquisition scripts, and record SHA-256 checksums | Stacy |
| October 21–25 | Conduct pre-integration assessments covering accuracy, completeness, timeliness, and consistency | Stacy, Allen, Zijian |
| October 26–November 2 | Clean individual datasets and document cleaning methods | Stacy, Allen, Zijian |
| November 3–8 | Integrate cleaned datasets using shared identifiers and create combined datasets | Netsh |
| November 9–13 | Conduct post-integration quality assessment, check join accuracy, and document results | Netsh |
| November 14–18 | Perform initial analysis, create visualizations, and prepare status report | Zijian; all contribute |
| November 19, 2026 | Submit status report and GitHub release | All |
| November 20–26 | Address feedback and improve integration and analysis | Netsh, Zijian |
| November 23–30 | Finalize automated workflow, data-use documentation, software license, and reproduction steps | Allen |
| November 24–December 1 | Complete data dictionary and machine-readable metadata | Stacy |
| December 1–3 | Compile final README.md with each member's completed report sections | Zijian; all contribute |
| December 4–6 | Test the full workflow on a fresh clone, review documentation, and make final corrections | All |
| December 7, 2026 | Create final GitHub release and submit final project | Stacy; all review |

This timeline includes time for feedback, revisions, and reproducibility testing. Exact submission times will be confirmed through Canvas.


## Constraints

The analysis is limited to crashes recorded by the Chicago Police Department and included in the City of Chicago data portal. It therefore does not include every crash that occurred, and reporting practices may differ between crashes reported at the scene and those reported later. Injury classifications reflect information recorded by the responding or reporting officer rather than independently verified medical outcomes. Records may also be amended after their initial publication, so results depend on the acquisition date of our data snapshot.

The datasets contain people involved in recorded crashes but do not contain measures of travel exposure, such as the number of trips, travelers, or miles traveled by each transportation mode. Consequently, the calculated proportions describe injury outcomes among people appearing in recorded crashes and cannot be interpreted as the overall risk of walking, cycling, driving, riding in a passenger car, or riding in an SUV.

Missing injury classifications, road-user categories, vehicle identifiers, and vehicle types may reduce the number of records available for some comparisons. Linking the People and Vehicles datasets may also create duplicated person records if the one-to-many relationships are handled incorrectly. We will address this risk by validating identifier relationships, checking row counts before and after each merge, and reporting unmatched records.

The passenger-car and SUV comparison will be descriptive. Differences may reflect crash circumstances, occupant characteristics, vehicle use, reporting patterns, or other factors not controlled for in this project, so we will not make causal claims about vehicle type. Finally, although the three datasets contain distinct and complementary records, they are all published by the City of Chicago. We will confirm with the instructor that this satisfies the requirement for three distinct data sources.
## Gaps


One remaining question is whether using three distinct datasets from the same City of Chicago publisher satisfies the course requirement for multiple data sources. Although the datasets provide different information and share common identifiers, we plan to confirm this with the instructor.

We also need to finalize our research questions and decide how certain variables will be categorized during analysis. We will coordinate with Allen to confirm data reuse terms and automated acquisition requirements. We will also work with Zijian to establish consistent injury categories and determine how to handle missing values, including fields that do not apply to certain types of records.

Another challenge is ensuring that the datasets merge correctly without creating unintended duplicates or losing important records. We still need to verify the relationship between vehicle and person identifiers and assess how many records successfully match.

Finally, full data quality assessments and end-to-end reproducibility testing have not yet been completed. These will be addressed during the implementation process. We will document any issues, update our methods as needed, and revise the project plan based on instructor feedback.

