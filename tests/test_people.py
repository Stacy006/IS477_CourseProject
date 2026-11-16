"""Regression checks for injury denominators, joins, raw preservation and paths."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from assess_people import canonicalize, check_links, quality_flags, read_csv
from clean_people import clean_people


def sample():
    crash = "a" * 128
    return pd.DataFrame([
        [" O001 ", " driver ", crash, "001", "2024-01-01T12:00:00.123", " fatal "],
        ["P2", "PASSENGER", crash, "001", "2024-01-01T12:00:00.123", "NO INDICATION OF INJURY"],
        ["O3", "PEDESTRIAN", crash, "", "2024-01-01", ""],
        ["O4", "BICYCLE", crash, "", "2024-01-01", "UNKNOWN"],
        ["O5", "DRIVER", crash, "999", "not-a-date", "UNLISTED INJURY"],
        ["O6", "DRIVER", crash, "002", "2025-01-01", "N/A"],
        ["P2", "PASSENGER", "", "", "", "NONINCAPACITATING INJURY"],
        ["O8", "NON-MOTOR VEHICLE", crash, "003", "2024-01-01", "REPORTED, NOT EVIDENT"],
        ["O9", "NON-CONTACT VEHICLE", crash, "004", "2024-01-01", "INCAPACITATING INJURY"],
    ], columns=["person_id", "person_type", "crash_record_id", "vehicle_id", "crash_date", "injury_classification"])


class PeopleTests(unittest.TestCase):
    def test_clean_rules_and_retention(self):
        raw = sample()
        untouched = raw.copy(deep=True)
        cleaned, changes, flags = clean_people(raw)
        pd.testing.assert_frame_equal(raw, untouched)
        self.assertEqual(len(cleaned), len(raw))
        self.assertEqual(cleaned.loc[0, "person_id"], "O001")
        self.assertEqual(cleaned.loc[0, "vehicle_id"], "001")
        self.assertEqual(cleaned.loc[0, "crash_date"], "2024-01-01T12:00:00.123000")
        self.assertEqual(cleaned.loc[4, "crash_date"], "not-a-date")
        self.assertEqual(cleaned.injury_known.sum(), 5)
        self.assertEqual(cleaned.injured.sum(), 4)
        self.assertFalse(cleaned.loc[1, "injured"])
        self.assertTrue(cleaned.loc[2:5, "injured"].isna().all())
        self.assertTrue(cleaned.loc[2:5, "injury_severity"].isna().all())
        self.assertEqual(cleaned.loc[2, "road_user_group"], "PEDESTRIAN")
        self.assertEqual(cleaned.loc[3, "road_user_group"], "BICYCLE")
        self.assertEqual(cleaned.loc[7, "road_user_group"], "OTHER_OR_UNRESOLVED")
        self.assertEqual(flags.duplicate_person_id.sum(), 2)
        self.assertEqual(flags.invalid_crash_date.sum(), 1)
        self.assertEqual(flags.outside_selected_year.sum(), 1)
        self.assertEqual(flags.occupant_missing_vehicle_id.sum(), 1)
        self.assertEqual(flags.unrecognized_injury_classification.sum(), 1)

    def test_join_key_duplicate_blank_and_case(self):
        people = canonicalize(sample())
        ref = pd.DataFrame([
            ["a" * 128, "1001", "001", "2024-01-01T12:00:00.123"],
            ["a" * 128, "1002", "002", "2024-01-01"],
            ["a" * 128, "1003", "002", "2024-01-01"],
            ["", "1004", "", "2024-01-01"],
            ["b" * 128, "1005", "999", "2024-01-01"],
            ["a" * 128, "1006", "003", "2024-02-01"],
            ["a" * 128, "1007", "004", "not-a-date"],
        ], columns=["crash_record_id", "crash_unit_id", "vehicle_id", "crash_date"])
        status, comparison, summary, info = check_links(people, ref, vehicle=True)
        self.assertEqual(status.tolist(), ["MATCHED", "MATCHED", "MISSING_KEY", "MISSING_KEY", "UNMATCHED", "AMBIGUOUS", "MISSING_KEY", "MATCHED", "MATCHED"])
        self.assertEqual(comparison.loc[0], "AGREE")
        self.assertEqual(comparison.loc[5], "NOT_COMPARABLE")
        self.assertEqual(comparison.loc[7], "DIFFERENT")
        self.assertEqual(comparison.loc[8], "NOT_COMPARABLE")
        self.assertEqual(summary["count"].sum(), len(people))
        self.assertEqual(info["reference_duplicate_key_rows"], 2)
        self.assertEqual(info["reference_rows_missing_key"], 1)

    def test_cli_roundtrip_rerun_and_bad_schema(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            rawdir = root / "data" / "raw"
            rawdir.mkdir(parents=True)
            raw = sample()
            source = rawdir / "people.csv"
            raw.to_csv(source, index=False)
            before = source.read_bytes()
            crashes = rawdir / "crashes.csv"
            vehicles = rawdir / "vehicles.csv"
            pd.DataFrame([["a" * 128, "2024-01-01T12:00:00.123"]], columns=["crash_record_id", "crash_date"]).to_csv(crashes, index=False)
            pd.DataFrame([["a" * 128, "001", "2024-01-01T12:00:00.123"]], columns=["crash_record_id", "vehicle_id", "crash_date"]).to_csv(vehicles, index=False)
            assessment = root / "reports" / "assessment"
            subprocess.run([sys.executable, str(SCRIPTS / "assess_people.py"), "--people", str(source), "--crashes", str(crashes), "--vehicles", str(vehicles), "--report-dir", str(assessment)], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads((assessment / "assessment.json").read_text())["people_rows"], 9)
            output = root / "data" / "processed" / "people.csv"
            reports = root / "reports" / "cleaning"
            command = [sys.executable, str(SCRIPTS / "clean_people.py"), "--people", str(source), "--output", str(output), "--report-dir", str(reports)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            bytes_first = output.read_bytes()
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual(bytes_first, output.read_bytes())
            self.assertEqual(before, source.read_bytes())
            saved = pd.read_csv(output, dtype={"person_id": "string", "vehicle_id": "string", "injured": "boolean"})
            self.assertEqual(saved.loc[0, "vehicle_id"], "001")
            self.assertTrue(saved.loc[2:5, "injured"].isna().all())
            # Reassessment uses a different report folder and all the same rules.
            subprocess.run([sys.executable, str(SCRIPTS / "assess_people.py"), "--people", str(output), "--crashes", str(crashes), "--vehicles", str(vehicles), "--report-dir", str(root / "reports" / "after")], check=True, capture_output=True, text=True)
            source.write_text("person_id\nO1\n", encoding="utf-8")
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("missing required columns", bad.stderr)
            # Allen's current output lacks vehicle_id: never silently substitute crash_unit_id.
            pd.DataFrame([["A" * 128, "001", "2024-01-01"]], columns=["crash_record_id", "crash_unit_id", "crash_date"]).to_csv(vehicles, index=False)
            with self.assertRaisesRegex(ValueError, "vehicle_id"):
                read_csv(vehicles, ["crash_record_id", "vehicle_id", "crash_date"], only_required=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
