#!/usr/bin/env python
'''
Created on Jan 29, 2014

@author: jd
'''
import sys
import oauth2 as oauth
import json

CONSUMER_KEY="yHhgOjThdUnuNSeqHNWTQw"
CONSUMER_SECRET="hP99GNPsJQg7hVDidb0G9VcRsu8Fjwd02yB1oZbsGeY"

def oauth_req(url, key, secret, http_method="GET", post_body="",
        http_headers=""):
    
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)
 
    resp, content = client.request(
        url,
        method=http_method,
        body=post_body,
        headers=http_headers
    )
    return content
 
if __name__ == '__main__':
    count = "20"
    if len(sys.argv) == 2:
        count = sys.argv[1]
        
    home_timeline = oauth_req(
      'https://api.twitter.com/1.1/statuses/home_timeline.json?count=' + count,
      '68445429-Je48T4gPYkfvtbOfSdA8uCYPMLiF5Vw0lo8uOG6b3',
      '8SrtwLv03E3GEF0egEWrEOhl0w4Ps6gHTcsGMyrQGFldK'
    )
    jsonvalues = json.loads(home_timeline)
    
    for tweet in jsonvalues:
        s = '\033[94m' + tweet['user']['name'] + '\033[0m' + ": " + tweet['text']
        print s
    
