import requests
import json

r = requests.get(url='http://lobo.local:5000/api/ID?uid=Gmail_mickey')
id = r.json()
print(id)

id['username'] = 'Minnie'
id['password'] = id['pwd']
del id['pwd']
del id['status']
id['id'] = 'Gmail_mickey'
print(id)
headers = {'Content-type': 'application/json'}
r = requests.put(url='http://lobo.local:5000/api/ID', data=json.dumps(id), headers=headers)
print(r.json())
