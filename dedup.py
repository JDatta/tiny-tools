#!/usr/bin/python

import sys

file_i = open(sys.argv[1])

last_md5 = ""
for i in file_i:
	fields = i.split(" ", 1)
	md5 = fields[0].strip()
	path = fields[1].strip()
	
	if not last_md5 == md5:
		last_md5 = md5;
	else:
		print path		
	


