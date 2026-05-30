#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import importlib
import os
import re
import shutil
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


MIN_PYTHON = (3, 9)

SUPPORTED_EXTENSIONS = {
    ".heic",
    ".heif",
    ".jpg",
    ".jpeg",
    ".png",
    ".mov",
    ".mp4",
    ".m4v",
}
IMAGE_EXTENSIONS = {".heic", ".heif", ".jpg", ".jpeg", ".png"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".m4v"}

EXIF_DATE_PRIORITY = ("DateTimeOriginal", "DateTimeDigitized", "DateTime")
XMP_DATE_PRIORITY = (
    "exif:DateTimeOriginal",
    "DateTimeOriginal",
    "xmp:CreateDate",
    "CreateDate",
    "photoshop:DateCreated",
    "DateCreated",
    "xmp:ModifyDate",
    "ModifyDate",
    "xmp:MetadataDate",
    "MetadataDate",
)
VIDEO_DATE_PRIORITY = (
    "creation_date",
    "date_time_original",
    "datetime_original",
    "date_time",
    "creation_time",
    "created",
    "date",
    "last_modification",
    "modification_date",
)


class DependencyError(RuntimeError):
    """Raised when runtime media metadata dependencies are missing."""


class DiskSpaceError(RuntimeError):
    """Raised when the destination does not have enough free space."""


@dataclass(frozen=True)
class DateDetection:
    captured_at: dt.datetime
    source: str


@dataclass(frozen=True)
class DestinationResolution:
    destination: Path | None
    skip_reason: str | None = None
    renamed: bool = False


@dataclass(frozen=True)
class BackupTask:
    source: Path
    destination: Path
    captured_at: dt.datetime
    date_source: str
    size: int
    renamed: bool = False


@dataclass
class BackupPlan:
    source_root: Path
    target_root: Path
    tasks: list[BackupTask] = field(default_factory=list)
    total_files: int = 0
    supported_files: int = 0
    skipped_sidecars: int = 0
    skipped_unsupported: int = 0
    skipped_existing: int = 0
    renamed_collisions: int = 0
    date_source_counts: Counter[str] = field(default_factory=Counter)

    @property
    def bytes_to_copy(self) -> int:
        return sum(task.size for task in self.tasks)


def check_dependencies(
    *,
    import_module: Callable[[str], Any] = importlib.import_module,
    python_version: Sequence[int] = sys.version_info,
) -> None:
    errors: list[str] = []

    if tuple(python_version[:2]) < MIN_PYTHON:
        errors.append(
            f"- Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required; "
            f"found {python_version[0]}.{python_version[1]}"
        )

    modules = (
        ("Pillow", "PIL.Image"),
        ("Pillow", "PIL.ExifTags"),
        ("pillow-heif", "pillow_heif"),
        ("hachoir", "hachoir.parser"),
        ("hachoir", "hachoir.metadata"),
    )
    loaded: dict[str, Any] = {}

    for package_name, module_name in modules:
        try:
            loaded[module_name] = import_module(module_name)
        except Exception as exc:  # pragma: no cover - exact import errors vary.
            errors.append(f"- {package_name} ({module_name}): {exc}")

    pillow_heif = loaded.get("pillow_heif")
    if pillow_heif is not None:
        register = getattr(pillow_heif, "register_heif_opener", None)
        if register is None:
            errors.append("- pillow-heif: register_heif_opener() is unavailable")
        else:
            try:
                register()
            except Exception as exc:
                errors.append(f"- pillow-heif: register_heif_opener() failed: {exc}")

    if errors:
        message = "\n".join(
            [
                "photobackup.py cannot start because required dependencies are missing or unusable.",
                *errors,
                "",
                "Run:",
                "  ./setup.sh",
                "",
                "Then run:",
                "  ./photobackup.sh [--dry-run] [--mock-copy] <source_directory> <target_directory>",
            ]
        )
        raise DependencyError(message)


def parse_metadata_datetime(value: Any) -> dt.datetime | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return _without_timezone(value)
    if isinstance(value, dt.date):
        return dt.datetime(value.year, value.month, value.day)
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")

    text = str(value).strip().strip("\x00")
    if not text:
        return None

    text = re.sub(r"\s+", " ", text)

    # EXIF commonly uses "YYYY:MM:DD HH:MM:SS".
    parsed = _datetime_from_match(
        re.search(
            r"(?<!\d)(?P<year>\d{4})[:/-](?P<month>\d{2})[:/-](?P<day>\d{2})"
            r"[ T](?P<hour>\d{2})[:.](?P<minute>\d{2})[:.](?P<second>\d{2})"
            r"(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?(?!\d)",
            text,
        )
    )
    if parsed:
        return parsed

    # Try stdlib ISO parsing after normalizing a trailing Z.
    iso_text = text.replace("Z", "+00:00")
    try:
        return _without_timezone(dt.datetime.fromisoformat(iso_text))
    except ValueError:
        pass

    parsed_date = _date_from_match(
        re.search(r"(?<!\d)(?P<year>\d{4})[-/](?P<month>\d{2})[-/](?P<day>\d{2})(?!\d)", text)
    )
    if parsed_date:
        return parsed_date

    parsed_compact = _date_from_match(
        re.search(r"(?<!\d)(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})(?!\d)", text)
    )
    if parsed_compact:
        return parsed_compact

    return None


def parse_filename_datetime(path: str | Path) -> dt.datetime | None:
    name = Path(path).stem

    patterns = (
        # IMG20250316115804
        re.compile(
            r"(?<!\d)IMG[-_ ]?(?P<date>\d{8})(?P<time>\d{6})(?!\d)",
            re.IGNORECASE,
        ),
        # 2025-08-12 at 08.41.30
        re.compile(
            r"(?<!\d)(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
            r"\s+at\s+(?P<hour>\d{2})[.:](?P<minute>\d{2})[.:](?P<second>\d{2})(?!\d)",
            re.IGNORECASE,
        ),
        # YYYYMMDD_HHMMSS or YYYYMMDD-HHMMSS
        re.compile(r"(?<!\d)(?P<date>\d{8})[-_](?P<time>\d{6})(?!\d)"),
    )

    for pattern in patterns:
        parsed = _datetime_from_filename_match(pattern.search(name))
        if parsed:
            return parsed

    # IMG-20251029-WA0003 and generic YYYYMMDD.
    parsed = _datetime_from_filename_match(re.search(r"(?<!\d)(?P<date>\d{8})(?!\d)", name))
    if parsed:
        return parsed

    parsed = _date_from_match(
        re.search(r"(?<!\d)(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(?!\d)", name)
    )
    if parsed:
        return parsed

    return None


def choose_image_datetime(
    exif: Mapping[Any, Any] | None,
    info: Mapping[str, Any] | None,
    tag_names: Mapping[Any, str] | None = None,
) -> dt.datetime | None:
    exif = exif or {}
    tag_names = tag_names or {}

    for wanted_name in EXIF_DATE_PRIORITY:
        for raw_tag, raw_value in exif.items():
            tag_name = raw_tag if isinstance(raw_tag, str) else tag_names.get(raw_tag, str(raw_tag))
            if tag_name == wanted_name:
                parsed = parse_metadata_datetime(raw_value)
                if parsed:
                    return parsed

    return choose_xmp_datetime(info or {})


def choose_xmp_datetime(info: Mapping[str, Any]) -> dt.datetime | None:
    direct_values: dict[str, Any] = {}
    xmp_blobs: list[str] = []

    for key, value in info.items():
        key_text = str(key)
        if key_text in XMP_DATE_PRIORITY:
            direct_values[key_text] = value
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="ignore")
        if isinstance(value, str) and _looks_like_xmp(value):
            xmp_blobs.append(value)

    for field_name in XMP_DATE_PRIORITY:
        parsed = parse_metadata_datetime(direct_values.get(field_name))
        if parsed:
            return parsed

    for field_name in XMP_DATE_PRIORITY:
        for blob in xmp_blobs:
            parsed = _extract_xmp_field_datetime(blob, field_name)
            if parsed:
                return parsed

    return None


def read_image_datetime(path: Path) -> dt.datetime | None:
    pillow_heif = importlib.import_module("pillow_heif")
    pillow_heif.register_heif_opener()

    image_module = importlib.import_module("PIL.Image")
    exif_tags_module = importlib.import_module("PIL.ExifTags")
    tag_names = getattr(exif_tags_module, "TAGS", {})

    with image_module.open(path) as image:
        try:
            exif = image.getexif()
        except Exception:
            exif = {}
        info = getattr(image, "info", {}) or {}
        return choose_image_datetime(exif, info, tag_names)


def choose_video_datetime(metadata: Any) -> dt.datetime | None:
    metadata_objects = list(_walk_metadata_objects(metadata))

    for field_name in VIDEO_DATE_PRIORITY:
        for metadata_object in metadata_objects:
            value = _metadata_get(metadata_object, field_name)
            parsed = parse_metadata_datetime(value)
            if parsed:
                return parsed

    for value in _walk_metadata_exports(metadata):
        parsed = parse_metadata_datetime(value)
        if parsed:
            return parsed

    return None


def read_video_datetime(path: Path) -> dt.datetime | None:
    parser_module = importlib.import_module("hachoir.parser")
    metadata_module = importlib.import_module("hachoir.metadata")

    parser = parser_module.createParser(str(path))
    if parser is None:
        return None

    try:
        metadata = metadata_module.extractMetadata(parser)
        if metadata is None:
            return None
        return choose_video_datetime(metadata)
    finally:
        close = getattr(parser, "close", None)
        if close is not None:
            close()


def detect_capture_datetime(
    path: Path,
    *,
    image_reader: Callable[[Path], dt.datetime | None] = read_image_datetime,
    video_reader: Callable[[Path], dt.datetime | None] = read_video_datetime,
) -> DateDetection:
    suffix = path.suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        parsed = image_reader(path)
        if parsed:
            return DateDetection(parsed, "image-metadata")
    elif suffix in VIDEO_EXTENSIONS:
        parsed = video_reader(path)
        if parsed:
            return DateDetection(parsed, "video-metadata")

    parsed = parse_filename_datetime(path)
    if parsed:
        return DateDetection(parsed, "filename")

    return DateDetection(dt.datetime.fromtimestamp(path.stat().st_mtime), "modified-time")


def build_backup_plan(
    source_root: Path,
    target_root: Path,
    *,
    detector: Callable[[Path], DateDetection] = detect_capture_datetime,
) -> BackupPlan:
    source_root = source_root.resolve()
    target_root = target_root.resolve()
    plan = BackupPlan(source_root=source_root, target_root=target_root)

    for path in sorted(source_root.rglob("*"), key=lambda item: str(item).lower()):
        if not path.is_file():
            continue

        plan.total_files += 1
        if path.name.startswith("._"):
            plan.skipped_sidecars += 1
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            plan.skipped_unsupported += 1
            continue

        plan.supported_files += 1
        detection = detector(path)
        plan.date_source_counts[detection.source] += 1
        month_dir = target_root / detection.captured_at.strftime("%Y%m")
        size = path.stat().st_size
        destination = resolve_destination(path, month_dir, size)

        if destination.skip_reason == "same-size":
            plan.skipped_existing += 1
            continue

        if destination.destination is None:
            raise RuntimeError(f"Could not resolve a destination for {path}")

        if destination.renamed:
            plan.renamed_collisions += 1

        plan.tasks.append(
            BackupTask(
                source=path,
                destination=destination.destination,
                captured_at=detection.captured_at,
                date_source=detection.source,
                size=size,
                renamed=destination.renamed,
            )
        )

    return plan


def resolve_destination(source: Path, month_dir: Path, size: int | None = None) -> DestinationResolution:
    size = source.stat().st_size if size is None else size
    candidate = month_dir / source.name

    if not candidate.exists():
        return DestinationResolution(candidate)
    if _same_size_file(candidate, size):
        return DestinationResolution(None, skip_reason="same-size")

    stem = source.stem
    suffix = source.suffix
    index = 1
    while True:
        renamed = month_dir / f"{stem}_{index}{suffix}"
        if not renamed.exists():
            return DestinationResolution(renamed, renamed=True)
        if _same_size_file(renamed, size):
            return DestinationResolution(None, skip_reason="same-size", renamed=True)
        index += 1


def check_free_space(
    destination_root: Path,
    bytes_needed: int,
    *,
    disk_usage: Callable[[Path], Any] = shutil.disk_usage,
) -> None:
    if bytes_needed <= 0:
        return

    usage_path = _nearest_existing_path(destination_root)
    usage = disk_usage(usage_path)
    try:
        free = usage.free
    except AttributeError:
        free = usage[2]

    if free < bytes_needed:
        raise DiskSpaceError(
            f"Not enough free space for {destination_root}: need {format_bytes(bytes_needed)}, "
            f"available {format_bytes(free)} at {usage_path}"
        )


def execute_backup_plan(
    plan: BackupPlan,
    *,
    dry_run: bool = False,
    mock_copy: bool = False,
    copy_function: Callable[[Path, Path], Any] = shutil.copy2,
    sleep_function: Callable[[float], Any] = time.sleep,
    stdout: Any = sys.stdout,
) -> None:
    if dry_run:
        for task in plan.tasks:
            print(f"DRY-RUN copy {task.source} -> {task.destination}", file=stdout)
        return

    copied_bytes = 0
    total_bytes = plan.bytes_to_copy
    if total_bytes == 0:
        return

    for task in plan.tasks:
        if mock_copy:
            sleep_function(0.01)
        else:
            task.destination.parent.mkdir(parents=True, exist_ok=True)
            copy_function(task.source, task.destination)

        copied_bytes += task.size
        _print_progress(copied_bytes, total_bytes, stdout=stdout)

    print(file=stdout)


def print_plan_summary(plan: BackupPlan, *, stdout: Any = sys.stdout) -> None:
    print(f"Scanned files: {plan.total_files}", file=stdout)
    print(f"Supported media: {plan.supported_files}", file=stdout)
    print(f"Queued copies: {len(plan.tasks)} ({format_bytes(plan.bytes_to_copy)})", file=stdout)
    print(f"Already backed up: {plan.skipped_existing}", file=stdout)
    print(f"Skipped sidecars: {plan.skipped_sidecars}", file=stdout)
    print(f"Skipped unsupported: {plan.skipped_unsupported}", file=stdout)
    print(f"Renamed collisions: {plan.renamed_collisions}", file=stdout)
    if plan.date_source_counts:
        counts = ", ".join(f"{name}={count}" for name, count in sorted(plan.date_source_counts.items()))
        print(f"Date sources: {counts}", file=stdout)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Back up photos and videos into destination YYYYMM directories."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="scan and print intended copies without writing")
    mode.add_argument(
        "--mock-copy",
        action="store_true",
        help="run copy workflow and progress without writing files",
    )
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("target_directory", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        check_dependencies()
    except DependencyError as exc:
        print(exc, file=sys.stderr)
        return 2

    source = args.source_directory
    target = args.target_directory

    if not source.is_dir():
        print(f"Source directory does not exist or is not a directory: {source}", file=sys.stderr)
        return 2

    try:
        plan = build_backup_plan(source, target)
        print_plan_summary(plan)
        if not args.dry_run:
            check_free_space(target, plan.bytes_to_copy)
        execute_backup_plan(plan, dry_run=args.dry_run, mock_copy=args.mock_copy)
    except DiskSpaceError as exc:
        print(exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Backup failed: {exc}", file=sys.stderr)
        return 1

    return 0


def _without_timezone(value: dt.datetime) -> dt.datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(dt.timezone.utc).replace(tzinfo=None)


def _datetime_from_filename_match(match: re.Match[str] | None) -> dt.datetime | None:
    if match is None:
        return None
    groups = match.groupdict()

    if "date" in groups and groups.get("date"):
        date_text = groups["date"]
        year = int(date_text[0:4])
        month = int(date_text[4:6])
        day = int(date_text[6:8])
    else:
        year = int(groups["year"])
        month = int(groups["month"])
        day = int(groups["day"])

    if "time" in groups and groups.get("time"):
        time_text = groups["time"]
        hour = int(time_text[0:2])
        minute = int(time_text[2:4])
        second = int(time_text[4:6])
    else:
        hour = int(groups.get("hour") or 0)
        minute = int(groups.get("minute") or 0)
        second = int(groups.get("second") or 0)

    return _safe_datetime(year, month, day, hour, minute, second)


def _datetime_from_match(match: re.Match[str] | None) -> dt.datetime | None:
    if match is None:
        return None
    groups = match.groupdict()
    return _safe_datetime(
        int(groups["year"]),
        int(groups["month"]),
        int(groups["day"]),
        int(groups.get("hour") or 0),
        int(groups.get("minute") or 0),
        int(groups.get("second") or 0),
    )


def _date_from_match(match: re.Match[str] | None) -> dt.datetime | None:
    if match is None:
        return None
    groups = match.groupdict()
    return _safe_datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]))


def _safe_datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> dt.datetime | None:
    try:
        return dt.datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


def _looks_like_xmp(value: str) -> bool:
    return "xmp" in value.lower() or "DateCreated" in value or "DateTimeOriginal" in value


def _extract_xmp_field_datetime(blob: str, field_name: str) -> dt.datetime | None:
    escaped = re.escape(field_name)
    patterns = (
        rf"{escaped}\s*=\s*['\"]([^'\"]+)['\"]",
        rf"<{escaped}>([^<]+)</{escaped}>",
    )
    bare_name = field_name.split(":")[-1]
    if bare_name != field_name:
        escaped_bare = re.escape(bare_name)
        patterns += (
            rf"{escaped_bare}\s*=\s*['\"]([^'\"]+)['\"]",
            rf"<{escaped_bare}>([^<]+)</{escaped_bare}>",
        )

    for pattern in patterns:
        match = re.search(pattern, blob)
        if match:
            parsed = parse_metadata_datetime(match.group(1))
            if parsed:
                return parsed
    return None


def _walk_metadata_objects(metadata: Any) -> Iterable[Any]:
    if metadata is None:
        return
    yield metadata

    for method_name in ("iterGroups", "iterGroupsTree"):
        method = getattr(metadata, method_name, None)
        if method is None:
            continue
        try:
            for item in method():
                yield item
        except Exception:
            continue


def _metadata_get(metadata: Any, field_name: str) -> Any:
    getter = getattr(metadata, "get", None)
    if getter is not None:
        try:
            return getter(field_name)
        except Exception:
            return None

    if isinstance(metadata, Mapping):
        return metadata.get(field_name)

    return getattr(metadata, field_name, None)


def _walk_metadata_exports(metadata: Any) -> Iterable[Any]:
    exporter = getattr(metadata, "exportDictionary", None)
    if exporter is not None:
        try:
            yield from _walk_values(exporter())
        except Exception:
            pass

    plaintext_exporter = getattr(metadata, "exportPlaintext", None)
    if plaintext_exporter is not None:
        try:
            for line in plaintext_exporter():
                yield line
        except Exception:
            pass


def _walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, Mapping):
        for child in value.values():
            yield from _walk_values(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            yield from _walk_values(child)
    else:
        yield value


def _same_size_file(path: Path, size: int) -> bool:
    try:
        return path.is_file() and path.stat().st_size == size
    except OSError:
        return False


def _nearest_existing_path(path: Path) -> Path:
    current = path.resolve() if path.exists() else path.absolute()
    while not current.exists():
        parent = current.parent
        if parent == current:
            return Path("/")
        current = parent
    return current


def _print_progress(copied_bytes: int, total_bytes: int, *, stdout: Any = sys.stdout) -> None:
    width = 32
    ratio = 1 if total_bytes <= 0 else min(1.0, copied_bytes / total_bytes)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    print(
        f"\r[{bar}] {ratio * 100:5.1f}% {format_bytes(copied_bytes)}/{format_bytes(total_bytes)}",
        end="",
        file=stdout,
        flush=True,
    )


def format_bytes(size: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


if __name__ == "__main__":
    raise SystemExit(main())
