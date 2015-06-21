#!/usr/bin/python
import requests
import json

TOKEN = "CAACEdEose0cBAKkZAsozBZAEzxMvsmEnQQj8nHYlS6dhijT76dxadySsTXnUZAkTWMsAOS4BFeOd4oiIZB3ioHWOZCAVMjHySxpxdejA7qehMfj9DdEiwIyd4hj3ZC8ZBz4YGRBgztKD2ZCnnpmArzmpoZCJNs2E19iQZD"
MY_ID = "1456095741"

query = ("SELECT message FROM status WHERE uid = "+MY_ID+" LIMIT 5")
payload = {'q': query, 'access_token': TOKEN}
r = requests.get('https://graph.facebook.com/fql', params=payload)

print r
result = json.loads(r.text)
c = 0
for i in result['data']:
	c = c+1
	print(str(c)+") "+i['message'])


