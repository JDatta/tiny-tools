#!/usr/bin/env python

import feedparser
import sys
from sys import argv
from os import popen
import os
from datetime import datetime
import time
import html2text

def usage():
	print "Usage:"
	print "get_feed_titles.py <feed_url>"
	sys.exit(1)

def errorExit(msg):
	print >> sys.stderr, msg
	sys.exit(-1)

flagCLS = False
def clearScreen():
	if flagCLS:
		os.system('clear') # Non portable

def getFeedTitles(feedUrl):
	feed = feedparser.parse( feedUrl )
	titles = []
	for an_item in feed["items"]:
		titles.append(an_item["title"])
	return titles

def readFeedSources(filename):
	f = open(filename)
	feedSources = {}
	for aline in f:
		flds = aline.split()
		if len(flds) == 2: 
			feedSources[flds[0].strip()] = flds[1].strip()
	f.close()
	return feedSources

def readTopicOrder(filename):
	f = open(filename)
	if f == None:
		errorExit("Topic file not found")

	topics = []
	for aline in f:
		flds = aline.split()
		for i in flds:
			i = i.strip()
			if i not in topics:
				topics.append(i)

	return topics

def chkTopicSanity(topics, feedSources):
	if len(topics) == 0:
		errorExit("Topic list not supplied.")

	for i in topics:
		if i not in feedSources.keys():
			errorExit("Topic '"+i+"' is not valid")
	return True

def toSentance(s):
	flds = s.split("_")
	ret = ""
	for i in flds:
		ret += i.capitalize() + " "
	return ret.strip()

def showFeeds(order, feedSources):
	INTERVAL=60*1000*500
	firstTime = True
	for i in order:
		if firstTime == True:
			print "Getting your feeds. Please wait..."
		
		t1	= datetime.now()
		titles	= getFeedTitles(feedSources[i])
		
		tdiff	= datetime.now() - t1
		tdiff	= tdiff.seconds * 1000 * 1000 + tdiff.microseconds
		sleept	= (INTERVAL-tdiff)/(1000*1000)

		if firstTime == True:
			firstTime = False
			clearScreen()
		else:
			if flagCLS:
				time.sleep(sleept)
			clearScreen()

		print "\n\n"
		print "=========================================="
		print "  %s HEADLINES (%.2f ms)"% (toSentance(i),tdiff/1000.0)
		#print " took "+str(tdiff)+"ms "+str(tdiff/1000000.0)+"s"
		print "=========================================="
		c = 0
		for j in titles:
			c += 1
			print "%2d: %s" % (c, j)
		

def main():
	global flagCLS

	if len(argv) == 1:
		feeds = readFeedSources("../res/urls.txt")
		order = readTopicOrder("../res/topics.txt")
		flagCLS = True
	elif len(argv) == 3 and argv[1] == "search":
		feeds = {argv[2]:"http://news.google.com/news?q="+argv[2]+"&output=rss"}
		order = [argv[2]]
	else:
		feeds = readFeedSources("../res/urls.txt")
		order = argv[1:]
	
	chkTopicSanity(order, feeds)

	clearScreen()
	showFeeds(order, feeds)	
	print "\n\n"
	clearScreen()


if __name__ == "__main__":
	main()
