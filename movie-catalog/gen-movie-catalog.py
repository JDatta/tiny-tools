#!/usr/bin/env python

import sys
import os
import re
import json
import urllib2
from copy import deepcopy

# Config
MIN_MOVIE_SIZE = 100 * 1024 * 1024; # 100 mb
RESTRICTED_EXTN = [".pdf", ".docx", ".mp3"]
#TOKENIZING_REGEX = "[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+"
TOKENIZING_REGEX = "[A-Z]{2,}(?![a-z])|[A-Za-z]+(?=[A-Z0-9])|[\'a-zA-Z0-9]+"
NON_TOKEN_REGEX = "([A-Z]*[0-9]+)|([0-9]*[A-Z]+)"
FIRST_MOVIE_YEAR = 1890


# todo: make this a class
def regex_tokenize(s):
    return re.findall(TOKENIZING_REGEX, s)


def is_non_name_token(token):
    if (re.match(".*[\d].*", token) and re.match(".*[\D].*", token)) or is_year(token):
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


# todo: move to a different class
def csv_dumps(flat_dict, skip_keys=None, accept_keys=None):

    if skip_keys is None:
        skip_keys = []
    s = ""

    if len(flat_dict) == 0:
        return s

    first_movie = flat_dict[0]
    first = True
    keys = first_movie.keys()

    print accept_keys
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
    s += "\n"

    for movie in flat_dict:
        first = True
        for key in keys:
            if first:
                first = False
            else:
                s += ","
            s += str(movie[key])
        s += "\n"

    return s


def tokenize(movie):
    #movie = deepcopy(movie_a)
    #print movie
    s = movie['meta']['basename']
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
    movie['name'] = movie_name.strip()
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
    dir_name = movie['meta']['dir_name']
    dir_name = dir_name.strip("/")
    movie['tags'] = dir_name.split("/")
    return movie


def human_readable_size(movie, suffix='B'):
    num = movie['size']
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            movie['human_size'] = "%3.1f%s%s" % (num, unit, suffix)
            return movie
        num /= 1024.0
    movie['human_size'] = "%.1f%s%s" % (num, 'Yi', suffix)
    return movie


def get_imdb_info(movie):

    name = movie['name']
    year = movie['year']
    name = name.strip()
    name = name.replace(" ", "%20")

    headers = {}
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
    def filter_movie_fn(filename):
        abs_path = os.path.join(root, filename)
        size = os.path.getsize(abs_path)
        name_regex = get_regex_filter_str()

        if (size > MIN_MOVIE_SIZE and
                (not re.match(name_regex, filename))):
            return True
        else:
            return False

    return filter_movie_fn


def set_basic_info(root, filename):
    abs_path = os.path.join(root, filename)
    size = os.path.getsize(abs_path)
    basename, ext = os.path.splitext(filename)

    return {
        'filename': filename,
        'abs_path': abs_path,
        'size': size,
        'ext': ext,
        'meta': {
            'dir_name': root,
            'basename': basename
        }
    }


def call(fn):
    def apply_fn(movie):
        #movie_c = deepcopy(movie)
        movie_c = movie
        fn(movie_c)
        return movie_c
    return apply_fn


def pipeline_each(data, fns):
    return reduce(lambda a, x: map(x, a),
                  fns,
                  data)


def walk(root):

    for root, dirs, files in os.walk(root):
        files = filter(filter_movie(root), files)
        for filename in files:
            movie = set_basic_info(root, filename)

            movie = reduce(lambda a, x: x(a), [
                tokenize,
                get_tags,
                get_movie_name,
                human_readable_size
            ], movie)
            """
            pipeline_each(movie, [
                call(tokenize),
                call(get_tags),
                call(get_movie_name),
                call(human_readable_size)
            ])
            """
            #tokenize(movie)
            #get_tags(movie)
            #get_movie_name(movie)
            #get_movie_year(movie)
            #human_readable_size(movie)
            #get_imdb_info(movie)
            yield movie


def extend(a, x):
    d = deepcopy(a)
    d.extend(x)
    return d


def main():
    movies = reduce(lambda a, x: extend(a, x), map(walk, sys.argv[1:]), [])
    print json.dumps(movies)
    #print csv_dumps(movies, None, ['human_size'])


if __name__ == '__main__':
    main()
