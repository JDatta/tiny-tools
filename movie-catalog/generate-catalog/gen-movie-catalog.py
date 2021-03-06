#!/usr/bin/env python

import sys
import os
import re
import json
import urllib2
from copy import deepcopy

help = """
    Sample usage:

    FIRST RUN:
    ``` bash
    ./gen-movie-catalog.py ~/movie_catalogs/all_movies_pretty_imdb_2.json \
    /run/media/jd/STORE/Movies/ /run/media/jd/Linux/Movies/ \
    /run/media/jd/winstore2/Movies/ /run/media/jd/Windows_store/Movies/ \
    /run/media/jd/STORE_GANDALF/Movies/ /run/media/jd/winstore2/Soaps/ \
    /run/media/jd/Windows_store/Soaps/ /run/media/jd/STORE/Soaps/ \
    /run/media/jd/Linux/Soaps/ > \
    ~/movie_catalogs/all_movies.json
    ```

    INCREMENTAL RUN:
    ``` bash
    ./gen-movie-catalog.py \
    ~/movie_catalogs/all_movies.json \
    /run/media/jd/STORE_GANDALF/Movies/ \
    > ~/movie_catalogs/all_movies_updated.json
    ```

    JSON to CSV:
    ``` bash
    ./gen-movie-catalog.py json2csv ~/all_movies.json > ~/all_movies.csv
    ```
"""

# todo: omit confidence value. How?

# Configuration
MIN_MOVIE_SIZE = 100 * 1024 * 1024  # 100 mb
RESTRICTED_EXTN = [".pdf", ".docx", ".mp3"]
#TOKENIZING_REGEX = "[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+"
TOKENIZING_REGEX = "[A-Z]{2,}(?![a-z])|[A-Za-z]+(?=[A-Z0-9])|[\'a-zA-Z0-9]+"
NON_TOKEN_REGEX = "([A-Z]*[0-9]+)|([0-9]*[A-Z]+)"
FIRST_MOVIE_YEAR = 1890

movie_cache = {}

# todo: move to a new class
def regex_tokenize(s):
    return re.findall(TOKENIZING_REGEX, s)


# todo: break at dvdrip,
def is_non_name_token(token):
    if (re.match(".*[\d].*", token) and re.match(".*[\D].*", token)) or is_year(token) or token.lower() == "dvd":
        return True
    else:
        return False


def is_year(s):
    try:
        n = int(s)
        if n >= FIRST_MOVIE_YEAR:
            return True
        else:
            return False
    except ValueError:
        return False


def get_regex_filter_str():
    names = ""
    for ext in RESTRICTED_EXTN:
        escaped_ext = re.escape(ext)
        if names != "":
            names += "|"
        names += escaped_ext
    return ".*[" + names + "]$"


def get_cell_value(dic, key):
    try:
        return "," + str(dic[key]).replace(",", "")
    except:
        return ","


# todo: move to a new class
def csv_dumps(flat_dict, skip_keys=None, accept_keys=None):

    if skip_keys is None:
        skip_keys = []
    s = ""

    if len(flat_dict) == 0:
        return s

    first_movie = flat_dict[0]
    first = True
    keys = first_movie.keys()

    if accept_keys is not None:
        filter_fn = lambda x: x in accept_keys and x not in skip_keys
    else:
        filter_fn = lambda x: x not in skip_keys

    keys = filter(filter_fn, keys)

    for key in keys:
        if first:
            first = False
        else:
            s += ","
        s += key
    s += ", Rating, Votes, IMDB_Year, Runtime"
    s += "\n"

    for movie in flat_dict:

        newline = ""
        first = True
        for key in keys:
            if first:
                first = False
            else:
                newline += ","
            try:
                newline += str(movie[key]).replace(",", "<comma>")
            except (UnicodeEncodeError, UnicodeDecodeError):
                newline += movie[key].replace(",", "<comma>")

        if 'imdb' in movie:
            newline += get_cell_value(movie['imdb'], 'imdbRating')
            newline += get_cell_value(movie['imdb'], 'imdbVotes')
            newline += get_cell_value(movie['imdb'], 'Year')
            newline += get_cell_value(movie['imdb'], 'Runtime')
        else:
            newline += ",,,,"

        s += newline + "\n"

    return s.encode('utf-8')


def pipeline_each(data, fns):
    return reduce(lambda a, x: map(x, a),
                  fns,
                  data)


def operate(opt, a, x):
    d = deepcopy(a)
    opt(d, x)
    return d


# todo: TBD: Currently tokenizes the longest path component. Not sure if foolproof.
def tokenize(movie):
    s = movie['meta']['movie_name_pick']
    tags = movie['tags']
    tags.append(s)
    maxtag = max(tags, key=len)
    s = s if len(maxtag) < 20 else maxtag

    tokens = regex_tokenize(s)
    movie['meta']['tokens'] = tokens
    return movie


def get_movie_name(movie):
    tokens = movie['meta']['tokens']
    movie_name = ""
    for token in tokens:
        if is_non_name_token(token):
            break
        movie_name += " " + token
    movie['name'] = movie_name.strip().title()
    return movie


def get_movie_year(movie):
    tokens = movie['meta']['tokens']
    for token in tokens:
        if is_year(token):
            movie['year'] = int(token)
            return movie
    movie['year'] = None
    return movie


def get_tags(movie):
    dir_path = movie['meta']['dir_path']
    dir_path = dir_path.strip("/")
    movie['tags'] = dir_path.split("/")
    return movie


def get_human_readable_size(movie, suffix='B'):
    num = movie['size']
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            movie['human_size'] = "%3.1f%s%s" % (num, unit, suffix)
            return movie
        num /= 1024.0
    movie['human_size'] = "%.1f%s%s" % (num, 'Yi', suffix)
    return movie


def finalize(movie):
    print >> sys.stderr, "Done processing:", movie['abs_path']
    movie.pop('meta', None)
    return movie


def get_imdb_info(movie):

    name = movie['name']
    year = movie['year']
    name = name.strip()
    name = name.replace(" ", "%20")

    url = "http://www.omdbapi.com/?t=" + name

    if year:
        url += "&y=" + str(year)

    req = urllib2.Request(url)
    response = urllib2.urlopen(req).read()

    json_values = json.loads(response)
    if json_values["Response"] == "True":
        movie['imdb'] = json_values
    else:
        movie['imdb'] = None
    return movie


def filter_movie(root):
    global movie_cache

    def filter_movie_fn(filename):
        global movie_cache
        abs_path = os.path.join(root, filename)
        size = os.path.getsize(abs_path)
        name_regex = get_regex_filter_str()

        if abs_path in movie_cache:
            return False

        if (size > MIN_MOVIE_SIZE and
                (not re.match(name_regex, filename))):
            print >> sys.stderr, "New movie found:", abs_path
            return True
        else:
            return False

    return filter_movie_fn


def set_basic_info(root, movie_in_dirname=False):

    def set_basic_info_fn(filename):
        abs_path = os.path.join(root, filename)
        size = os.path.getsize(abs_path)
        basename, ext = os.path.splitext(filename)
        dir_basename = os.path.basename(os.path.normpath(root))

        if movie_in_dirname:
            movie_name_pick = dir_basename
        else:
            movie_name_pick = basename

        return {
            'filename': filename,
            'dir_basename': dir_basename,
            'abs_path': abs_path,
            'size': size,
            'ext': ext,
            'meta': {
                'dir_path': root,
                'basename': basename,
                'movie_name_pick': movie_name_pick
            }
        }
    return set_basic_info_fn


def should_take_dir(files):

    ext_set = reduce(lambda a, x: operate(set.add, a, x), map(lambda f: os.path.splitext(f)[1], files), set())

    if len(files) == 0:
        avg_length = 0
    else:
        avg_length = reduce(lambda a, x: a + len(x), map(lambda f: os.path.splitext(f)[0], files), 0) * 1.0 / len(files)

    max_length = reduce(lambda a, x: len(x) if len(x) > a else a, map(lambda f: os.path.splitext(f)[0], files), 0)

    # todo: additional cases: diff between max and max_common_substr; diff between dirbasename and filebasename etc
    # todo: weighted sum of these numbers?
    # todo: how to define these heuristic values more formally?
    few_files = 5 >= len(files) >= 2
    same_type = len(ext_set) == 1
    similar_file_name_sz = (max_length - avg_length) <= 2

    return few_files and same_type and similar_file_name_sz


def process_dir(rdf):
    root = rdf[0]
    files = rdf[2]
    files = filter(filter_movie(root), files)
    movies = map(set_basic_info(root, should_take_dir(files)), files)
    return pipeline_each(movies, [
        get_tags,
        tokenize,
        get_movie_name,
        get_movie_year,
        get_human_readable_size,
        get_imdb_info,
        finalize
    ])


def walk(root):
    return reduce(lambda a, x: operate(list.extend, a, x), map(process_dir, os.walk(root)))


def populate_cache(file_name):
    global movie_cache
    with open(file_name) as data_file:
        cached_movies = json.load(data_file)
    for amovie in cached_movies:
        movie_cache[amovie['abs_path']] = amovie


def merge_movies(movies):
    global movie_cache
    # assert
    for movie in movies:
        if movie['abs_path'] in movie_cache:
            print "FATAL:: Merge did not work::",movie['abs_path']
    movies.extend(movie_cache.values())

def main():
    populate_cache(sys.argv[1])
    movies = reduce(lambda a, x: a + x, map(walk, sys.argv[2:]), [])
    merge_movies(movies)
    print json.dumps(movies, indent=4, sort_keys=True)
    #print csv_dumps(movies, None, ['name', 'abs_path', 'year', 'human_size'])


def json2csv():
    f = open(sys.argv[2])
    json_movies = json.loads(f.read())
    f.close()
    print csv_dumps(json_movies, None, ['name', 'abs_path', 'year', 'human_size'])

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        print help
    elif sys.argv[1] == "json2csv":
        json2csv()
    else:
        main()
