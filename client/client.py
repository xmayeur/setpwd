import requests

r = requests.get('http://lobo.local:5000/api/ID?uid=Gmail_mickey')
print(r.content)
