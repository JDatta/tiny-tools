# Photo Backup

`photobackup.py` backs up iPhone photo and video folders into month-based destination directories named `YYYYMM`.

The supported command is:

```sh
./photobackup.sh [--dry-run] [--mock-copy] <source_directory> <target_directory>
```

## Setup

Create the local virtual environment and install the media metadata dependencies:

```sh
./setup_venv.sh
```

The wrapper script uses `.venv/bin/python` automatically:

```sh
./photobackup.sh --dry-run ./iPhone2 ./destination
```

You can also run `photobackup.py` directly if your active Python environment has the required packages installed.

## Supported Files

The tool includes:

- `.heic`, `.heif`
- `.jpg`, `.jpeg`
- `.png`
- `.mov`, `.mp4`, `.m4v`

AppleDouble sidecar files named `._*` are ignored. Unsupported files are skipped and counted in the summary.

## Date Detection

Files are placed into destination month folders based on the best available date:

1. Image metadata from EXIF/XMP via Pillow and pillow-heif.
2. Video metadata via Hachoir.
3. Filename patterns such as `IMG20250316115804`, `IMG-20251029-WA0003`, `2025-08-12 at 08.41.30`, `YYYYMMDD_HHMMSS`, `YYYY-MM-DD`, and `YYYYMMDD`.
4. File modification time.

Creation time is not used.

## Copy Behavior

Before copying, the tool calculates the bytes that would actually be copied and checks destination free space.

Destination files are handled as follows:

- Same name and same size: treated as already backed up and skipped.
- Same name and different size: copied with a numbered suffix such as `IMG_0001_1.HEIC`.
- New file: copied with `shutil.copy2`, preserving available metadata.

## Modes

`--dry-run` scans, plans, and prints the copies without creating files.

```sh
./photobackup.sh --dry-run ./iPhone2 ./destination
```

`--mock-copy` runs the full planning, disk-space check, and progress workflow, but sleeps instead of writing files.

```sh
./photobackup.sh --mock-copy ./iPhone2 ./destination
```

Run without either flag to perform the backup:

```sh
./photobackup.sh ./iPhone2 ./destination
```

## Tests

Run the unit tests with:

```sh
python3 -m unittest discover -v
```

The tests do not require the media dependencies to be installed; dependency imports are mocked where needed.
