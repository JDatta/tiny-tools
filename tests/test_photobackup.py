from __future__ import annotations

import datetime as dt
import os
import tempfile
import types
import unittest
from collections import namedtuple
from pathlib import Path

import photobackup


class DependencyPrecheckTests(unittest.TestCase):
    def test_precheck_accepts_available_dependencies(self) -> None:
        calls = []

        def import_module(name: str):
            if name == "pillow_heif":
                return types.SimpleNamespace(register_heif_opener=lambda: calls.append("registered"))
            return types.SimpleNamespace()

        photobackup.check_dependencies(import_module=import_module, python_version=(3, 11, 0))
        self.assertEqual(calls, ["registered"])

    def test_precheck_reports_missing_dependency(self) -> None:
        def import_module(name: str):
            if name == "PIL.Image":
                raise ImportError("not installed")
            if name == "pillow_heif":
                return types.SimpleNamespace(register_heif_opener=lambda: None)
            return types.SimpleNamespace()

        with self.assertRaises(photobackup.DependencyError) as error:
            photobackup.check_dependencies(import_module=import_module, python_version=(3, 11, 0))

        self.assertIn("./setup_venv.sh", str(error.exception))
        self.assertIn("PIL.Image", str(error.exception))

    def test_precheck_reports_heif_registration_failure(self) -> None:
        def import_module(name: str):
            if name == "pillow_heif":
                def fail() -> None:
                    raise RuntimeError("bad heif")

                return types.SimpleNamespace(register_heif_opener=fail)
            return types.SimpleNamespace()

        with self.assertRaises(photobackup.DependencyError) as error:
            photobackup.check_dependencies(import_module=import_module, python_version=(3, 11, 0))

        self.assertIn("register_heif_opener", str(error.exception))


class DateParsingTests(unittest.TestCase):
    def test_supported_filename_patterns(self) -> None:
        cases = {
            "IMG20250316115804 Copy.JPG": dt.datetime(2025, 3, 16, 11, 58, 4),
            "IMG-20251029-WA0003 Copy.JPG": dt.datetime(2025, 10, 29),
            "DESHMUKH 2025-08-12 at 08.41.30.JPEG": dt.datetime(2025, 8, 12, 8, 41, 30),
            "20240102_030405.mov": dt.datetime(2024, 1, 2, 3, 4, 5),
            "scan-20240203.png": dt.datetime(2024, 2, 3),
        }

        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(photobackup.parse_filename_datetime(filename), expected)

    def test_filename_parser_rejects_invalid_dates(self) -> None:
        self.assertIsNone(photobackup.parse_filename_datetime("IMG20250230115804.JPG"))
        self.assertIsNone(photobackup.parse_filename_datetime("note-20241301.txt"))

    def test_metadata_datetime_parser_handles_exif_and_iso(self) -> None:
        self.assertEqual(
            photobackup.parse_metadata_datetime("2025:08:12 08:41:30"),
            dt.datetime(2025, 8, 12, 8, 41, 30),
        )
        self.assertEqual(
            photobackup.parse_metadata_datetime("2025-08-12T08:41:30Z"),
            dt.datetime(2025, 8, 12, 8, 41, 30),
        )


class MetadataSelectionTests(unittest.TestCase):
    def test_exif_priority_prefers_original_then_digitized_then_datetime(self) -> None:
        exif = {
            306: "2020:01:01 01:01:01",
            36868: "2021:01:01 01:01:01",
            36867: "2022:01:01 01:01:01",
        }
        tags = {
            306: "DateTime",
            36868: "DateTimeDigitized",
            36867: "DateTimeOriginal",
        }

        self.assertEqual(
            photobackup.choose_image_datetime(exif, {}, tags),
            dt.datetime(2022, 1, 1, 1, 1, 1),
        )

    def test_image_datetime_uses_xmp_when_exif_missing(self) -> None:
        info = {
            "XML:com.adobe.xmp": (
                "<x:xmpmeta><rdf:Description "
                "xmp:CreateDate=\"2024-06-01T12:13:14Z\" /></x:xmpmeta>"
            )
        }

        self.assertEqual(
            photobackup.choose_image_datetime({}, info, {}),
            dt.datetime(2024, 6, 1, 12, 13, 14),
        )

    def test_video_datetime_uses_hachoir_metadata_fields(self) -> None:
        metadata = {
            "date_time": "2020:01:01 00:00:00",
            "creation_date": dt.datetime(2023, 5, 6, 7, 8, 9),
        }

        self.assertEqual(
            photobackup.choose_video_datetime(metadata),
            dt.datetime(2023, 5, 6, 7, 8, 9),
        )

    def test_video_datetime_can_read_export_dictionary(self) -> None:
        class Metadata:
            def get(self, name: str):
                return None

            def exportDictionary(self):
                return {"Metadata": {"Creation date": "2022-03-04T05:06:07Z"}}

        self.assertEqual(
            photobackup.choose_video_datetime(Metadata()),
            dt.datetime(2022, 3, 4, 5, 6, 7),
        )


class BackupPlanningTests(unittest.TestCase):
    def filename_detector(self, path: Path) -> photobackup.DateDetection:
        parsed = photobackup.parse_filename_datetime(path)
        self.assertIsNotNone(parsed)
        return photobackup.DateDetection(parsed, "filename")

    def test_modified_time_is_final_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-date-name.HEIC"
            path.write_bytes(b"image")
            timestamp = dt.datetime(2021, 7, 8, 9, 10, 11).timestamp()
            os.utime(path, (timestamp, timestamp))

            detection = photobackup.detect_capture_datetime(path, image_reader=lambda _: None)

        self.assertEqual(detection.source, "modified-time")
        self.assertEqual(detection.captured_at, dt.datetime(2021, 7, 8, 9, 10, 11))

    def test_build_plan_skips_sidecars_unsupported_and_existing_same_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src"
            target = root / "dst"
            source.mkdir()
            (source / "._IMG20240101120000.JPG").write_bytes(b"sidecar")
            (source / "notes.txt").write_text("skip")
            image = source / "IMG20240101120000.JPG"
            image.write_bytes(b"abc")

            month = target / "202401"
            month.mkdir(parents=True)
            (month / image.name).write_bytes(b"abc")

            plan = photobackup.build_backup_plan(source, target, detector=self.filename_detector)

        self.assertEqual(plan.total_files, 3)
        self.assertEqual(plan.skipped_sidecars, 1)
        self.assertEqual(plan.skipped_unsupported, 1)
        self.assertEqual(plan.skipped_existing, 1)
        self.assertEqual(plan.tasks, [])

    def test_build_plan_renames_different_size_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src"
            target = root / "dst"
            source.mkdir()
            image = source / "IMG20240101120000.JPG"
            image.write_bytes(b"abc")

            month = target / "202401"
            month.mkdir(parents=True)
            (month / image.name).write_bytes(b"different-size")

            plan = photobackup.build_backup_plan(source, target, detector=self.filename_detector)

        self.assertEqual(len(plan.tasks), 1)
        self.assertEqual(plan.tasks[0].destination.name, "IMG20240101120000_1.JPG")
        self.assertEqual(plan.renamed_collisions, 1)

    def test_disk_space_abort(self) -> None:
        Usage = namedtuple("Usage", "total used free")

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(photobackup.DiskSpaceError):
                photobackup.check_free_space(
                    Path(tmp) / "future-destination",
                    100,
                    disk_usage=lambda _: Usage(total=1000, used=950, free=50),
                )


if __name__ == "__main__":
    unittest.main()
