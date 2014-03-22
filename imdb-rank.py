#!/usr/bin/env python
'''
Created on Jan 29, 2014

@author: jd
'''

import sys
import urllib2
import json

def get_imdb_rating(iname):
    iname = iname.strip()
    name = iname.replace(" ", "%20")
    
    headers = {}
    url = "http://www.omdbapi.com/?t="+name
    
    req = urllib2.Request(url)
    response = urllib2.urlopen(req).read()
    
    #print response
    #print "============="
    
    jsonvalues = json.loads(response)
    if jsonvalues["Response"]=="True":
        s = jsonvalues['Type'] + ": " + jsonvalues['Title'] +\
          " (" + jsonvalues['Year'] + ") " +\
          "by " + jsonvalues['Director'] + "\t" +\
          "Rating=" + jsonvalues['imdbRating'] + " " +\
          "by " + jsonvalues['imdbVotes'] + " users" + "\t"
        print s
    else:
        print "Movie not found."
          
    
        
if __name__ == '__main__':
    name = sys.argv[1]
    get_imdb_rating(name)