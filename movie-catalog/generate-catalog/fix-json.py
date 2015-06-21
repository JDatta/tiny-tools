#!/usr/bin/python

import sys
import json


def to_camel_case(snake_str):
    components = snake_str.split('_')
    camel = components[0] + "".join(x.title() for x in components[1:])
    camel_list = list(camel)
    camel_list[0] = camel_list[0].lower()
    return "".join(camel_list)


def get_json_map(dic):
    if not isinstance(dic, dict):
        return dic

    for key in dic.keys():
        val = get_json_map(dic[key])
        del dic[key]
        new_key = to_camel_case(key)
        dic[new_key] = val
    return dic


def main():
    f = open(sys.argv[1])
    movies = json.loads(f.read())
    json_movies = map(get_json_map, movies)
    print json.dumps(json_movies, indent=4, sort_keys=True)

if __name__ == '__main__':
    main()