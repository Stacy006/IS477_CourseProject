# People Data Quality Assessment and Cleaning

**Responsible member:** Zijian Chen  
**Validation snapshot:** November 15, 2026; crash dates in 2024  
**Scripts:** [assess_people.py](../assess_people.py), [clean_people.py](../clean_people.py)

## 1. Inputs and scope

The People input contains **246,702 records and 29 columns**. Its source is the
[Chicago Traffic Crashes - People dataset](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d).
Reference checks used all 112,056 Crashes records and 228,316 Vehicles records
in the corresponding 2024 extracts. For this validation run, only reference
identifiers and crash dates were downloaded from those two datasets; all People
columns were retained. The repository's existing [acquire_data.py](../acquire_data.py)
downloads the full three datasets, which the new scripts also accept.

The [verification summary](../results/people/verification_summary.json) records
input hashes, sizes, environment versions, and validation scope. CSV serialization
and selected columns affect byte-level hashes; the reference-file hashes in this
validation run are not hashes of the full Crashes and Vehicles downloads.
Counts can change if the source revises historical records.

## 2. Quality assessment

### Accuracy

Person types and injury classifications were checked against explicit recognized
categories. No unrecognized nonblank values were found. Identifier format checks
found no unusual nonblank person, crash, or vehicle identifiers. These checks
identify formatting and category problems; they cannot verify the accuracy of
police-recorded events or medical outcomes.

### Completeness

| Check | Records | Percentage of People |
|---|---:|---:|
| Missing person ID, crash ID, person type, or crash date | 0 each | 0% |
| Missing injury classification | 39 | 0.0158% |
| Missing vehicle ID | 5,986 | 2.4264% |
| Drivers/passengers missing vehicle ID | 37 | 0.0150% |

The 5,986 absent vehicle IDs comprise 3,345 pedestrians, 2,349 cyclists, 246
non-motor-vehicle records, nine non-contact-vehicle records, and 37 drivers.
All passengers have a vehicle ID. Missing links for pedestrians and cyclists
are retained and distinguished from missing driver linkage; no record is dropped
solely because it lacks a vehicle ID.

The script measures missingness for every input column. For example, age is
missing for 70,305 records (28.50%). Fields such as seat number, pedestrian
attributes, and hospital information can be inapplicable; missingness alone does
not justify imputing values. See the full [missing-value table](../results/people/missing_values.csv).

### Timeliness

All People crash dates were parseable and within 2024, ranging from January 1
00:00 to December 31 23:47. This verifies temporal coverage, not publication
latency. The acquisition filter excludes undated source records before this
assessment, and the resulting missing-date count does not describe the entire
unfiltered source dataset.

### Consistency and feasibility of integration

No duplicate nonblank `person_id` values were found. All 246,702 records matched
Crashes on normalized `crash_record_id`. Using the Project Plan's composite key
`crash_record_id + vehicle_id`, all 240,716 People records with a vehicle ID
matched Vehicles. These include 240,698 drivers/passengers and 18 non-contact
vehicle records. The 37 remaining drivers/passengers lack vehicle IDs.

Neither reference lookup had ambiguous nonblank composite keys, and no linked
crash timestamps differed. Blank keys are excluded from reference matching;
6,155 Vehicles records lack the vehicle join key. Lookup counts are aggregated
before matching so that reference duplicates cannot multiply People rows.
These are pre-integration checks, not a claim that the final integrated dataset
or Netsh's post-integration assessment has been completed.

**Identifier discrepancy:** The source People metadata describes `vehicle_id`
as corresponding to Vehicles `crash_unit_id`. In this snapshot, those fields
contain different numbers and that substitution produced no matches. Actual
matching supports the Project Plan's use of `vehicle_id` in both datasets.
Allen's current `viechle assessment.py` selects `crash_unit_id` but omits
`vehicle_id`; it must retain `vehicle_id` before its output can replace the raw
Vehicles reference. The People assessment fails explicitly if this field is
absent. See [vehicle match counts by person type](../results/people/vehicle_links_by_person_type.csv).

## 3. Cleaning decisions and derived fields

The cleaning script preserves all input rows and the raw file. It standardizes
identifier whitespace and case, category whitespace/case, and valid ISO date
representations. Malformed dates, unknown categories, and potential duplicate IDs
are retained and flagged for review rather than guessed or silently removed.
In this snapshot, 246,702 crash IDs were uppercased and 246,702 timestamps changed
representation; no other original field values changed. These are formatting
normalizations, not corrections to crash facts. All joining datasets must use
the same ID normalization. See [field-change counts](../results/people/changed_fields.csv).

| New field | Definition |
|---|---|
| `road_user_group` | DRIVER, PASSENGER, PEDESTRIAN, BICYCLE; otherwise OTHER_OR_UNRESOLVED. |
| `injury_classification_status` | KNOWN, MISSING, UNKNOWN, NOT_APPLICABLE, or UNRECOGNIZED. |
| `injury_known` | True only for an explicitly recognized injury or no-injury category. |
| `injured` | Nullable Boolean: True for the four injury categories, False for NO INDICATION OF INJURY, blank otherwise. |
| `injury_severity` | FATAL, INCAPACITATING, NONINCAPACITATING, REPORTED_NOT_EVIDENT, NO_INJURY; blank for unresolved classifications. |
| `quality_*` | Fifteen review flags for missing fields, unusual IDs, duplicate person IDs, unrecognized categories, date problems, and occupants missing vehicle IDs. |

The injured categories are `FATAL`, `INCAPACITATING INJURY`,
`NONINCAPACITATING INJURY`, and `REPORTED, NOT EVIDENT`. Only
`NO INDICATION OF INJURY` maps to False. Missing or unrecognized values remain
blank in `injured` and `injury_severity`, preventing them from becoming uninjured
observations. Quality flags do not automatically exclude records from analysis.

## 4. Results and validation

The cleaned output contains **246,702 rows and 49 columns**: the 29 input columns
plus five analysis fields and 15 quality flags. The source file was unchanged.
CSV round-trip checks confirmed preserved row order and values, retained unknowns,
and valid Boolean classifications. Reassessment found the same matching counts
and no new identifier or date issues. All seven [output checks](../results/people/validation.csv)
passed. Three [regression tests](../tests/test_people.py) cover injury mappings,
unknowns, leading zeros, ambiguous/blank joins, CSV round trips, reruns, and
missing required columns.

The preparatory classification counts are:

| Classification | People |
|---|---:|
| No indication of injury | 220,957 |
| Nonincapacitating injury | 13,632 |
| Reported, not evident | 10,020 |
| Incapacitating injury | 1,931 |
| Fatal | 123 |
| Missing classification | 39 |

Thus 246,663 people have known classifications and 25,706 are classified as
injured. These totals cover all person types; they are not the completed
four-group or passenger-car/SUV comparisons. The comparisons and charts remain
pending. See [classification counts](../results/people/injury_classification_counts.csv)
and [person-type counts](../results/people/person_type_counts.csv).

## 5. Reproducing this stage

Place both scripts in the repository root. `clean_people.py` imports shared
definitions from `assess_people.py`; neither performs work when imported.
Use Python 3.11+ for the existing acquisition script and pandas 2.0+ for these
People scripts. The recorded validation environment used Python 3.12.14 and
pandas 3.0.1. Acquisition additionally requires `requests`.

```bash
python -m pip install "pandas>=2.0" requests
python acquire_data.py
python assess_people.py
python clean_people.py
python assess_people.py --people data/processed/people_2024_clean.csv --report-dir data/processed/people_quality_after
python -m unittest discover -s tests -p "test_people.py" -v
```

The first command installs the stage dependencies; Allen will finalize the
project-wide dependency specification. Existing raw files are reused by the
acquisition script. People-script relative paths are resolved from the scripts'
directory. Outputs are:

- `data/processed/people_quality/`: pre-cleaning assessment tables, record checks, and metadata.
- `data/processed/people_2024_clean.csv`: cleaned People data.
- `data/processed/people_cleaning/`: field changes, validation, mappings, and cleaning metadata.
- `data/processed/people_quality_after/`: reassessment results.

Selected aggregate outputs from the verified run are committed under
[`results/people/`](../results/people). Raw and cleaned People snapshots exceed
50 MB and are not included in this commit; publishing accessible snapshots and
the required Box retrieval code remains a team follow-up. The API can currently
regenerate inputs, but later downloads may differ from the saved hashes. This
stage has been tested; the team's entire acquisition-to-analysis workflow has
not yet been validated from a fresh clone.

Read `person_id`, `crash_record_id`, and `vehicle_id` as strings downstream, and
read `injured` as pandas' nullable `boolean`. Normalize identifier case on both
sides before joining. Do not cast the string `"False"` using Python `bool()`.

## 6. Next steps

Coordinate retention of `vehicle_id` with Allen and normalized joins with Netsh;
complete road-user comparisons, injury-severity charts, and vehicle comparisons
after integration validation; contribute People field definitions to Stacy's
data dictionary; and compile completed team sections into the final README.
