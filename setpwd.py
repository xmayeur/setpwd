# import crypto_helpers as c
import requests
import getpass
import sys
import json

# db = input('Enter the database pathname: ')
# aes = c.AEScipher(db=db)

uid = input('Enter a IdentityId: ')
url = 'http://192.168.0.4:5000/api/ID'
url2 = 'http://192.168.0.4:5000/api/admin'

if len(sys.argv) >1:
    if sys.argv[1] == 'local':
        url = 'http://localhost:8080/api/ID'
        url2 = 'http://localhost:8080/api/admin'
       

if uid == 'dump':

    headers = {'Content-type': 'application/json'}
    r = requests.get(url=url2)
    print(r.json()['status'])
    data = r.json()['data']
    with open('id.json', 'w') as f:
        json.dump(json.loads(data), f, indent=4)
    sys.exit(0)

elif uid == 'load':

    with open('id.json', 'r') as f:
        data = json.load(f)
    headers = {'Content-type': 'application/json'}
    r = requests.post(url=url2, data=json.dumps(data), headers=headers)
    if r.json()['status'] == 200:
        print('DB saved!')
    else:
        print(r.json())
    sys.exit(0)
    
else:

    headers = {'Content-type': 'application/json'}
    r = requests.get(url=url + '?uid=%s' % uid)
    id = r.json()
    if id['status'] == 200:
        uname = id['username']
        pwd = id['password']
    else:
        uname = ''
        pwd = ''
        
    # uname, pwd = aes.read(uid)
    
    if uname == '':
        uname = input('Enter a new User Name: ')
        pwd1 = getpass.getpass('Enter a new password: ')
        pwd2 = getpass.getpass('Repeat the new password: ')
        if pwd1 != pwd2:
            print('Password mismatch!')
            sys.exit(1)
        else:
            # aes.save(uid, uname, pwd1)
            new_id = dict()
            new_id['id'] = uid
            new_id['username'] = uname
            new_id['password'] = pwd1
            r = requests.post(url=url, data=json.dumps(new_id), headers=headers)
            if r.json()['status'] == 200:
                print('Identity saved!')
            else:
                print(r.json())
            sys.exit(0)
    else:
        pwd1 = getpass.getpass('Enter current password: ')
        if pwd1 != pwd:
            print('Password mismatch!')
            sys.exit(1)
        else:
            pwd1 = getpass.getpass('Enter a new password: ')
            pwd2 = getpass.getpass('Repeat the new password: ')
            if pwd1 != pwd2:
                print('Password mismatch!')
                sys.exit(1)
            elif pwd1 == '' and pwd2 == '':
                # aes.remove(uid, pwd)
                new_id = dict()
                new_id['id'] = uid
                new_id['username'] = uname
                new_id['password'] = pwd
                r = requests.delete(url=url, data=json.dumps(new_id), headers=headers)
                if r.json()['status'] == 200:
                    print('Identity removed!')
                else:
                    print(r.json())
                sys.exit(0)
            else:
                # aes.save(uid, uname, pwd1)
                # print('Identity saved!')
                new_id = dict()
                new_id['id'] = uid
                new_id['username'] = uname
                new_id['password'] = pwd1
                r = requests.put(url=url, data=json.dumps(new_id), headers=headers)
                if r.json()['status'] == 200:
                    print('Identity updated!')
                else:
                    print(r.json())
                sys.exit(0)
                

