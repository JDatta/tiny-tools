#!/usr/bin/env python
'''
subtitle downloader

@author: manoj m j
@copyright: (c) www.manojmj.com
'''

import os
import hashlib
import urllib2
import sys

def get_hash(name):
        readsize = 64 * 1024
        with open(name, 'rb') as f:
            size = os.path.getsize(name)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
        return hashlib.md5(data).hexdigest()

def sub_downloader(path):

    hash = get_hash(path)
    replace = [".avi",".mp4",".mkv",".mpg",".mpeg", ".flv"]
    for content in replace:
        path = path.replace(content,"")
   
    if not (os.path.exists(path+".srt") or os.path.exists(path+".sub")):
        print "Searching http://thesubdb.com/..."
        headers = { 'User-Agent' : 
                   'SubDB/1.0 (subtitle-downloader/1.0; http://github.com/manojmj92/subtitle-downloader)' }
        url = "http://api.thesubdb.com/?action=download&hash=" + hash + "&language=en"
    
        try:
            req = urllib2.Request(url, '', headers)
            response = urllib2.urlopen(req).read()
            with open (path + ".srt" , "wb") as subtitle:
                subtitle.write(response)
            print "Subtitle downloaded!"
            return 0
        except urllib2.HTTPError, e:
            print "Subtitle not found."
            return -1
    else:
        print "Subtitle already exists."
        return 1

if __name__ == '__main__':
    ret = 0
    try:
        path = sys.argv[1]
        ret = sub_downloader(path)
    except Exception, e:
        print str(e)
        ret = e.errno
    exit(ret)
    