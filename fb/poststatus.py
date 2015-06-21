#!/usr/bin/python
import requests
import json
import sys

TOKEN = "CAACEdEose0cBAKkZAsozBZAEzxMvsmEnQQj8nHYlS6dhijT76dxadySsTXnUZAkTWMsAOS4BFeOd4oiIZB3ioHWOZCAVMjHySxpxdejA7qehMfj9DdEiwIyd4hj3ZC8ZBz4YGRBgztKD2ZCnnpmArzmpoZCJNs2E19iQZD"
MY_ID = "1456095741"

url = 'https://graph.facebook.com/'+MY_ID+'/feed'
message = sys.argv[1]
payload = {'access_token': TOKEN, 'message': message}
s = requests.post(url, data=payload)
print s
