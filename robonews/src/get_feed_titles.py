#!/usr/bin/env python

import feedparser
import sys
from sys import argv
from os import popen
import os

import html2text

if (len(argv) < 2):
	print "Usage:"
	print "get_feed_titles.py <feed_url>"
	sys.exit(1)

python_wiki_rss_url = argv[1]

print "Getting your feed.."
feed = feedparser.parse( python_wiki_rss_url )

print "\n"
if len(argv) == 2:
	print "NEWS HEADLINES"
	print "=================="

	c = 0
	for an_item in feed["items"]:
		c += 1
		print "%2d: %s" % (c, an_item["title"])
	print "=================="

elif len(argv) == 3:
	i = int(argv[2]) - 1
	if ( i < 0 ):
		print "Invalid argument"
		sys.exit(1)
	
	item = feed["items"][i]
	print item["title"]
	print "=================="
	data = item["description"] 
	html2text.wrapwrite(html2text.html2text(data, ''))

elif len(argv) == 4:
	i = int(argv[2]) - 1
	item = feed["items"][i]
	print item["title"]
	print item[argv[3]]

else:
	print "Usage:"
	print "get_feed_titles.py <feed_url>"

