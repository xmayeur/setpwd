import requests
import getpass
import sys
import json
import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode


class RSAcipher:
    
    def __init__(self, certfile=None, key=None):
        try:
            if key is not None:
                self.key = RSA.importKey(key)
            
            elif certfile is not None:
                self.key = RSA.importKey(open(certfile).read())
            
            else:
                self.key = RSA.generate(2048)
            
            _pubkey = self.key.publickey()
            self.pubkey = _pubkey.exportKey()
            self.privkey = self.key.exportKey('PEM')
            self.rsa = PKCS1_OAEP.new(self.key)
            
        except Exception as e:
            print('Error initializing RSAcipher : ' + e.message)
            self.key = None
    
    def create_keyset(self, name='key'):
        self.key = RSA.generate(2048)
        with open('priv_' + name + '.pem', 'wb') as f:
            f.write(self.key.exportKey('PEM'))
        self.pubkey = self.key.publickey()
        with open('pub_' + name + '.pem', 'wb') as f:
            f.write(self.pubkey.exportKey())
        return self.key
    
    def encrypt(self, text):
        return b64encode(self.rsa.encrypt(text.encode())).decode()
    
    def decrypt(self, msg):
        try:
            return self.rsa.decrypt(b64decode(msg)).decode()
        except Exception as e:
            return None


def main():

    parser = argparse.ArgumentParser("Manage vault passwords")

    parser.add_argument("-d", "--dump", required=False,
                        help="dump all passwords to file")
    parser.add_argument("-l", "--load", required=False,
                        help="load all password from file")
    parser.add_argument("-k", "--genkeys", required=False,
                        help="generate a keys pair to file")
    parser.add_argument("-e", "--encrypt", required=False,
                        help="encrypt the data using the provided key")
    parser.add_argument("-id", "--identity", required=False,
                        help="specify id record in the vault datastore")
    parser.add_argument("-u", "--username", required=False,
                        help="specify a user name")
    parser.add_argument("-p", "--password", required=False,
                        help="specify the user password")
    parser.add_argument("-L", "--local", required=False, action='store_true',
                        help="use a localhost vault server")
    parser.add_argument("-D", "--delete", required=False, action='store_true',
                        help="delete the vault entry ")
    parser.add_argument("-r", "--read", required=False, action='store_true',
                        help="only read a vault entry ")
    args = parser.parse_args()

    url = 'http://192.168.0.4:5000/api/ID'
    url2 = 'http://192.168.0.4:5000/api/admin'
    headers = {'Content-type': 'application/json'}
    rsa = None
    curr_name = ''
    curr_pwd = ''
    uname = ''
    pwd = ''
    
    if args.local:
        url = 'http://localhost:8080/api/ID'
        url2 = 'http://localhost:8080/api/admin'
    
    if args.dump:
        r = requests.get(url=url2, headers=headers)
        print(r.json()['status'])
        data = r.json()['data']
        with open('id.json', 'w') as f:
            json.dump(json.loads(data), f, indent=4)
        sys.exit(0)
        
    elif args.load:
        with open('id.json', 'r') as f:
            data = json.load(f)
        r = requests.post(url=url2, data=json.dumps(data), headers=headers)
        if r.json()['status'] == 200:
            print('DB saved!')
        else:
            print(r.json())
        sys.exit(0)
        
    elif args.genkeys:
        rsa = RSAcipher()
        rsa.create_keyset(args.genkeys)
        new_id = dict()
        new_id['id'] = 'pk_'+ args.genkeys
        new_id['username'] = args.genkeys
        new_id['password'] = rsa.pubkey.exportKey().decode()
        r = requests.post(url=url, data=json.dumps(new_id), headers=headers)
        if r.json()['status'] == 200:
            print('Key pair created - public key saved in the vault')
        else:
            print(r.json())
        sys.exit(0)
        
    else:
    
        if args.identity:
            uid = args.identity
        else:
            uid = input('Enter a IdentityId: ')
            if uid == '' or uid is None:
                print('Please enter a valid Identity name')
                sys.exit(-1)
   
        if args.username:
            uname = args.username
        elif not args.read:
            uname = input('Enter a new User Name: ')

        if args.password:
            pwd = args.password
        elif not args.read:
            pwd = getpass.getpass('Enter a new password: ')
            pwd2 = getpass.getpass('Repeat the new password: ')
            if pwd != pwd2:
                print('Password mismatch!')
                sys.exit(-1)

        # Retrieve a username / password from given Identity
        headers = {'Content-type': 'application/json'}
        r = requests.get(url=url + '?uid=%s' % uid, headers=headers)
        id = r.json()
        
        if id['status'] == 200:
            curr_name = id['username']
            curr_pwd = id['password']
            
            # decrypt if needed
            if args.encrypt:
                rsa = RSAcipher(certfile='priv_' + args.encrypt + '.pem')
                curr_name = rsa.decrypt(curr_name)
                curr_pwd = rsa.decrypt(curr_pwd)
                
            if uname == '' and pwd == '':
                print('Username:password = ' + curr_name + ':'+ curr_pwd)
                sys.exit(0)
        else:
            curr_uname = ''
            curr_pwd = ''
            
        # create a new username / password entry
        if uname != '' and pwd != '' and curr_name == '':
            if args.encrypt:
                rsa = RSAcipher(certfile='pub_' + args.encrypt + '.pem')
                uname = rsa.encrypt(uname)
                pwd = rsa.encrypt(pwd)
                
            new_id = dict()
            new_id['id'] = uid
            new_id['username'] = uname
            new_id['password'] = pwd
            r = requests.post(url=url, data=json.dumps(new_id), headers=headers)
            if r.json()['status'] == 200:
                print('Identity saved!')
            else:
                print(r.json())
            sys.exit(0)
            
        # or update an existing entry
        else:

            if curr_pwd != pwd:
                print('Password mismatch!')
                sys.exit(-1)
                
            elif args.delete:
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
                

if __name__ == "__main__":
    main()
