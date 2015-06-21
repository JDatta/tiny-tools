#!/usr/bin/env python

import json
import facebook
import requests
import sys

secrets = json.load(open('./secrets.json'))
graph = facebook.GraphAPI(secrets['access_token'])


def show_profile(profileId):
    profile = graph.get_object(profileId)
    print profile.get('name')


def print_friends():
    friends = graph.get_object('me/friends')

    while True:
        try:
            [show_profile(friend['id']) for friend in friends['data']]
            friends = requests.get(friends['paging']['next']).json()
        except KeyError:
            break


def show_post(post):
    print post

def print_me():
    me = graph.get_object('me')
    her_id = me['significant_other']['id']
    her_profile = graph.get_object(her_id)

    for key in her_profile:
        print key, "::", her_profile[key]

    #posts = graph.get_connections(her_id, 'posts')
    #print posts

def print_my_wall():

    my_id = graph.get_object('me')['id']
    posts = graph.get_connections(my_id, 'posts')

    while True:
        try:
            #[show_post(post=post) for post in posts['data']]
            print json.dumps(posts['data'], indent=4, sort_keys=True)
            sys.stdin.read()
            posts = requests.get(posts['paging']['next']).json()
        except KeyError:
            break


# === MAIN ===
print_me()




