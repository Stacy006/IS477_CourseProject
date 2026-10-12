# Project Plan: Chicago Traffic Crashes in 2024

## Overview

This project will compare injury proportions and severity among pedestrians, cyclists, drivers, and passengers in recorded Chicago traffic crashes in 2024, and injury proportions between passenger-car and SUV occupants. We will integrate the Chicago Data Portal's Crashes, Vehicles, and People datasets.

Our focus is reproducible data curation: acquisition, assessment across four quality dimensions, cleaning, integration, post-integration validation, and descriptive analysis. Separate Python scripts coordinated by a run-all script will produce tables and charts. Preserved data and documented sources, methods, and field definitions will support reuse.

## Team

Members will write and commit their own sections and field descriptions using their GitHub accounts. Compilation means organizing completed contributions; all members will review the final report and documentation.

| Member | Planned responsibilities |
| --- | --- |
| Stacy | Acquire all three 2024 datasets and record checksums; assess and clean Crashes; compile the data dictionary and metadata; create releases and submit. |
| Allen | Assess and clean Vehicles; document reuse terms and license the code; build run-all, declare dependencies, document reproduction, and test a fresh clone. |
| Zijian | Assess and clean People; analyze and visualize results; compile completed sections into README.md. |
| Netsh | Integrate cleaned datasets; assess integrated quality; document integration methods and results. |

## Research Questions

1. How do injury proportions and severity distributions differ among pedestrians, cyclists, drivers, and passengers in recorded Chicago crashes in 2024?
2. Among drivers and passengers, how do injury proportions differ between passenger-car and SUV occupants?

Groups correspond to PEDESTRIAN, BICYCLE, DRIVER, and PASSENGER in People.PERSON_TYPE. Vehicle categories are PASSENGER and SPORT UTILITY VEHICLE (SUV) in Vehicles.VEHICLE_TYPE.

### Planned Analysis Approach

At the person-record level, we will report total, known-classification, injured, and missing/unknown-classification counts for each road-user group. Injury proportions will equal records with fatal, incapacitating, non-incapacitating, or reported-but-not-evident injuries divided by records with known classifications. Missing/unknown classifications will not count as uninjured. Severity distributions will show each injury category's percentage among injured people.

The second comparison will include drivers and passengers linked to passenger cars or SUVs through CRASH_RECORD_ID and VEHICLE_ID in both People and Vehicles. Unmatched records and missing or other vehicle types will be counted separately and excluded.

Tables will show counts and percentages. Bar charts will compare injury proportions across road-user groups and vehicle types; proportional stacked bars will show severity distributions. Missing classifications and unmatched records will accompany results. Findings will not establish causality or overall travel risk.

## Datasets and Planned Workflow

### Sources and Preliminary Feasibility

Initial CSV extracts were downloaded on October 7, 2026, restricted to 2024 crash dates. Each exceeds 100 records; none uses Kaggle.

| Official dataset | Initial extract | Contribution and identifiers |
| --- | --- | --- |
| [Traffic Crashes – Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if) | 112,057 rows; 49 columns | One row per crash, keyed by CRASH_RECORD_ID. Dates define coverage; crash circumstances provide context; injury summaries validate aggregated People counts. |
| [Traffic Crashes – Vehicles](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Vehicles/68nd-jvt3) | 228,318 rows; 71 columns | One row per unit, keyed by CRASH_UNIT_ID. Crash and vehicle IDs support linkage; UNIT_TYPE and VEHICLE_TYPE describe units and identify passenger cars/SUVs. |
| [Traffic Crashes – People](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d) | 246,702 rows; 29 columns | One row per person, keyed by PERSON_ID. Crash and vehicle IDs support linkage; PERSON_TYPE and INJURY_CLASSIFICATION provide groups and outcomes. |

### Cross-Dataset Feasibility

All three datasets share CRASH_RECORD_ID; People and Vehicles additionally link through VEHICLE_ID within each crash. Preliminary checks confirmed unique, non-missing crash identifiers, 2024 dates throughout, and Crashes matches for every People and Vehicles crash ID. Of 240,735 driver and passenger records, 240,698 matched Vehicles through the combined keys. Unmatched records and structural missingness require investigation.

### Lifecycle, Acquisition, and Organization

We will follow the USGS Science Data Lifecycle from Week 1: plan, acquire, process, analyze, preserve, and publish/share. Assessment, cleaning, and integration constitute processing; documentation, quality management, and backups support all stages.

Acquisition scripts will retrieve 2024 records and record source URLs, retrieval dates, filters, row counts, and SHA-256 checksums. Checksums verify copies against preserved snapshots; source updates may change later downloads.

The tabular CSVs contain string identifiers, categorical and numeric values, and dates. Raw, cleaned, and integrated data will occupy data/raw/, data/cleaned/, and data/integrated/. Scripts, outputs, and documentation will occupy scripts/, results/, and docs/. Paths will be relative.

### Overall Assessment and Cleaning

Before integration, each dataset will be assessed for accuracy, completeness, timeliness, and consistency. Validation identifies potential errors but cannot independently verify every crash detail.

Cleaning scripts will standardize dates, whitespace, equivalent categories, and documented missing-value codes while preserving string identifiers and raw files. Missing information will be distinguished from inapplicable fields. Duplicates and invalid values will be investigated before correction or removal. Decisions and affected record counts will be logged, and cleaned data reassessed.

### Crashes Assessment and Cleaning

Accuracy checks will test non-negative integer injury counts and agreement between INJURIES_TOTAL and the sum of fatal, incapacitating, non-incapacitating, and reported-but-not-evident injuries. Completeness checks will measure missing crash identifiers, dates, and injury summaries. Timeliness checks will revalidate 2024 coverage, acknowledging historical revisions. Consistency checks will test identifier uniqueness and agreement between CRASH_DATE and CRASH_MONTH.

Initial checks confirmed unique, non-missing crash IDs and 2024 dates. Missing injury counts will not become zero automatically; unresolved inconsistencies will be flagged.

### Vehicles Assessment and Cleaning

Accuracy checks will validate UNIT_TYPE, VEHICLE_TYPE, and identifier formats. Completeness checks will measure missing unit, crash, and vehicle IDs, dates, and vehicle types, distinguishing inapplicable values from missing information and UNKNOWN/NA. Timeliness checks will verify 2024 coverage. Consistency checks will test CRASH_UNIT_ID uniqueness, non-missing crash–vehicle key uniqueness, and links to Crashes. Repeated crash IDs are expected.

Vehicle types will not be guessed. Unresolved types will be counted separately and excluded from the passenger-car/SUV comparison.

### People Assessment and Cleaning

Accuracy checks will validate PERSON_TYPE, INJURY_CLASSIFICATION, and identifier formats. Completeness checks will report missing counts and percentages for identifiers, person types, dates, and injury classifications. Missing or unknown injuries will remain separate from no injury. Timeliness checks will verify 2024 coverage. Consistency checks will test PERSON_ID uniqueness and crash and vehicle links.

Pedestrians and cyclists without vehicle IDs will be retained. Documented derived fields will identify road-user groups, known injury classifications, injury status, and severity.

### Integration and Post-Integration Assessment

Using Pandas, we will left-join People to Crashes on CRASH_RECORD_ID and to Vehicles on CRASH_RECORD_ID plus VEHICLE_ID. Only Vehicles records with non-missing VEHICLE_ID will enter the vehicle join. Many-to-one validation will prevent row multiplication while preserving all People records.

Post-integration checks will assess:

- **Accuracy:** Agreement of linked dates and person-level injury totals with Crashes summaries; discrepancies will be investigated.
- **Completeness:** Missing values, matching rates, and unmatched records by person type, distinguishing expected absent links from failures.
- **Timeliness:** 2024 coverage, acquisition dates, and differences in source update timing.
- **Consistency:** Identifier uniqueness at each record level, formats, and row counts before and after joins.

The integration script will save assessment results. Success requires no unexplained row multiplication and documented unmatched records, discrepancies, and limitations.

### Automation, Reproducibility, and Ethics

A run-all script will coordinate separate scripts from acquisition through assessment, cleaning, integration, validation, and analysis. Package versions will be declared in requirements.txt. We will document the execution command and test a fresh clone without code edits. Git history, acquisition records, checksums, and cleaning logs will capture provenance.

We will verify and document reuse terms, cite datasets and software, and license our code. Permitted input snapshots will be committed; files exceeding 50 MB will use accessible Box links and tested download code. Results will be aggregated without identifying individuals.

### Metadata and Data Documentation

Stacy will compile members’ field descriptions into a data dictionary covering meanings, types, identifiers, categories, missing-value conventions, derived fields, and linkage definitions.

A Schema.org Dataset JSON-LD file will record title, purpose, contributors, sources, temporal and spatial coverage, formats, access locations, and reuse terms. Both documents will be stored in docs/.

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
| November 23–30 | Finalize and verify stage scripts and the run-all workflow; complete data-use documentation, software license, and reproduction steps | Allen |
| November 24–December 1 | Complete data dictionary and machine-readable metadata | Stacy |
| December 1–3 | Compile final README.md with each member's completed report sections | Zijian; all contribute |
| December 4–6 | Test the full workflow on a fresh clone, review documentation, and make final corrections | All |
| December 7, 2026 | Create final GitHub release and submit final project | Stacy; all review |

This timeline includes time for feedback, revisions, and reproducibility testing. Exact submission times will be confirmed through Canvas.


## Constraints

The datasets cover police-recorded crashes rather than all crashes. Reporting practices vary, injury classifications are not independently verified medical outcomes, and historical revisions make results snapshot-dependent.

Without travel-exposure measures, injury proportions cannot represent overall travel risk. Missing classifications or identifiers may limit comparisons. Passenger-car/SUV differences may reflect uncontrolled crash circumstances, occupant characteristics, vehicle use, or reporting patterns; we will not infer causal effects.

## Gaps

We need instructor confirmation that three complementary datasets from one publisher satisfy the source requirement. Allen will verify reuse terms and acquisition requirements; Zijian will implement and validate the stated injury mappings and missing-value rules.

Unmatched records, full quality assessments, cleaning validation, and fresh-clone workflow testing remain to be addressed. We will verify that joins preserve person counts without duplication, document unresolved issues, and revise methods and the plan following instructor feedback.
