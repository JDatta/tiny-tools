# tiny-tools

`tiny-tools` is a collection of small personal command-line utilities, scripts,
and experiments. The repository is intentionally broad rather than packaged as a
single application: some tools are current and self-contained, while others are
older helpers kept here as references or starting points for local automation.

## Repository Contents

### Photo and Media Tools

- `photobackup2/` contains the most complete utility in the repo. It backs up
  iPhone photos and videos into month-based destination folders named `YYYYMM`.
  It detects capture dates from image metadata, video metadata, filename
  patterns, and file modification time. It also supports dry-run and mock-copy
  modes, handles filename collisions, checks destination free space before
  copying, and includes unit tests.
- `resize_images.sh` recursively resizes `.jpg` files from a source tree into a
  target tree using ImageMagick.
- `extract-audio` extracts MP3 audio from matching media files with `ffmpeg`.
- `photomailer` captures a webcam image with `fswebcam` and sends it through a
  local mail setup using `mutt`.
- `download-subtitle.py` is an older Python 2 script that computes a video hash
  and downloads English subtitles from the SubDB API.

### News, Web, and API Helpers

- `robonews/` is a Python command-line RSS headline reader. It can show a
  configured set of Google News feeds from `robonews/res/urls.txt` and
  `robonews/res/topics.txt`, or search for an arbitrary topic from the command
  line.
- `twitter-home.py` is an older Python 2 OAuth example for reading a Twitter
  home timeline.
- `imdb-rank.py` queries OMDb for a movie title and prints rating details.

### Movie Catalog Tools

- `movie-catalog/generate-catalog/` contains Python scripts for scanning movie
  directories, deriving movie names and years from file paths, optionally adding
  IMDb metadata, and converting catalog JSON to CSV.
- `movie-catalog/movieCatalogAccess/` is a small Java/Maven project that reads
  movie catalog JSON into Java entities and persists or retrieves it through a
  JPA/Hibernate-backed `MovieManager`. It includes sample JSON data under
  `data/` and JPA/Hibernate configuration under `src/main/resources/`.

### Finance and Dashboard Helpers

- `mf-dashboard/` contains a mutual fund dashboard script and local data files.
  The script reads `funds.json`, fetches NAV values, and prints purchase value,
  current value, total change, and approximate yearly change.

### Shell and Developer Utilities

- `bash-utils/` contains reusable shell helpers that can be installed into
  `~/.bashrc.d`. The current helper set includes `jdsync`, Git log shortcuts,
  and a `tojpg` conversion function that uses ImageMagick or `ffmpeg`.
- `find-jar.sh` searches recursively through JAR files for a class name or fully
  qualified class name.
- `raise_pr.sh` is a template-style helper for cherry-picking commits onto
  several upstream branches, pushing those branches, and opening GitHub compare
  pages.
- `plotfilesz.py` plots the probability density of file sizes in a directory
  using SciPy and Matplotlib.

## Getting Started

Most tools are independent. Start from the subdirectory or script that matches
the task you want to run, then check its shebang and imports for runtime
requirements.

The actively documented tools are:

```sh
cd photobackup2
./setup.sh
photobackup.sh --dry-run <source_directory> <target_directory>
```

```sh
cd robonews/src
./robonews.py search "topic"
```

```sh
cd movie-catalog/movieCatalogAccess
mvn test
```
## Runtime Notes

- `photobackup2` targets Python 3.9+ and installs its Python dependencies from
  `photobackup2/requirements.txt`.
- Several older Python scripts use Python 2 syntax and libraries such as
  `urllib2`. They may need modernization before running on a current Python 3
  environment.
- Media scripts assume common command-line tools are installed, especially
  `ffmpeg`, ImageMagick, `fswebcam`, and `mutt`.
- Java code in `movie-catalog/movieCatalogAccess` is Maven based and uses older
  versions of Jackson, Derby, Hibernate, and JUnit.
- Some API-oriented scripts are historical and may reference services,
  credentials, or endpoints that are no longer valid. Review them before use.

## Tests

The primary test suite is in `photobackup2`:

```sh
cd photobackup2
python3 -m unittest discover -v
```

The Java movie catalog project also includes a Maven test scaffold:

```sh
cd movie-catalog/movieCatalogAccess
mvn test
```
