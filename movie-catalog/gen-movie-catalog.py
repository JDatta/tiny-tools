#!/usr/bin/env python

import sys
import os
import re
import json
import urllib2

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


def tokenize(s):
    return regex_tokenize(s)


def is_non_name_token(token):
    if (re.match(".*[\d].*", token) and re.match(".*[\D].*", token)) or is_year(token):
        #print token, "True"
        return True
    else:
        #print token, "False"
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


def get_movie_name(movie):
    name = movie['basename']
    tokens = tokenize(name)
    movie_name = ""
    for token in tokens:
        if is_non_name_token(token):
            break
        movie_name += " " + token
    return movie_name.strip()


def get_movie_year(filename):
    tokens = tokenize(filename)
    for token in tokens:
        if is_year(token):
            return int(token)
    return None


def get_tags(dir_name):
    dir_name = dir_name.strip("/")
    return dir_name.split("/")


def get_regex_filter_str():
    names = ""
    for ext in RESTRICTED_EXTN:
        escaped_ext = re.escape(ext)
        if names != "":
            names += "|"
        names += escaped_ext
    return ".*[" + names + "]$"


def human_readable_size(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


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
        return json_values
    else:
        return None


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


def walk(root):

    movies = []
    for root, dirs, files in os.walk(root):
        files = filter(filter_movie(root), files)
        for filename in files:
            abs_path = os.path.join(root, filename)
            size = os.path.getsize(abs_path)
            
            movie = {
                'filename': filename,
                'abs_path': abs_path,
                'size': size
            }

            # Todo: Make this a pipeline
            basename, ext = os.path.splitext(filename)
            movie['basename'] = basename
            movie['ext'] = ext
            movie['tags'] = get_tags(root)
            movie['name'] = get_movie_name(movie)
            movie['year'] = get_movie_year(filename)
            movie['human_size'] = human_readable_size(movie['size'])
            #movie['imdb'] = get_imdb_info(movie)
            movies.append(movie)

    return movies


# todo: move to a different class
def csv_dumps(flat_dict, skip_keys=None):

    if skip_keys is None:
        skip_keys = []
    s = ""

    if len(flat_dict) == 0:
        return s

    first_movie = flat_dict[0]
    first = True
    keys = first_movie.keys()
    keys = [item for item in keys if item not in skip_keys]

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


def test():
    f = open("/home/jd/all_movies.txt")
    for path in f:
        if "." in path:
            path = path.strip()
            head, tail = os.path.split(path)
            print get_movie_name(tail), "==>", tail


def main():
    movies = []
    for i in sys.argv[1:]:
        movies.extend(walk(i))

    movie_names = map(lambda x: (x['name'], x['year'], x['filename']), movies)
    for i in movie_names:
        print i

    #print csv_dumps(movies, ["tags"])
    #print json.dumps(movies)
    
if __name__ == '__main__':
    main()
    #test()
