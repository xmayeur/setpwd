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

    parser = argparse.ArgumentParser(prog='setpwd', description="Manage vault passwords")

    parser.add_argument("-D", "--dumpFile", required=False,
                        help="dump all passwords to file")
    parser.add_argument("-L", "--loadFile", required=False,
                        help="load all password from file")
    parser.add_argument("-g", "--genkeys", required=False,
                        help="generate a key pair to files")
    parser.add_argument("-k", "--key", required=False,
                        help="encrypt/decrypt the data using the provided key")
    parser.add_argument("id", nargs='?', default=None,
                        help="record identifier in the vault datastore")
    parser.add_argument("-l", "--local", required=False, action='store_true',
                        help="use a localhost vault server")
    parser.add_argument("-d", "--delete", required=False, action='store_true',
                        help="delete the vault entry corresponding to 'id'")
    parser.add_argument("-r", "--read", required=False, action='store_true',
                        help="read the vault entry corresponding to 'id'")
    parser.add_argument("-n", "--new", required=False, action='store_true',
                        help="create a new vault entry with the identity='id'")
    parser.add_argument("-c", "--newPassword", required=False, nargs='?', default=None,
                        help="change the vault entry password corresponding to 'id'")
    parser.add_argument("-u", "--username", required=False,
                        help="specify a user name")
    parser.add_argument("-p", "--password", required=False,
                        help="specify the user password")
    
    args = parser.parse_args()

    url = 'http://192.168.0.4:5000/api/ID'
    url2 = 'http://192.168.0.4:5000/api/admin'
    
    headers = {'Content-type': 'application/json'}
    curr_name = ''
    uname = ''
    
    if args.local:
        url = 'http://localhost:8080/api/ID'
        url2 = 'http://localhost:8080/api/admin'
    
    if args.dumpFile:
        r = requests.get(url=url2, headers=headers)
        print(r.json()['status'])
        data = r.json()['data']
        with open(args.dumpFile, 'w') as f:
            json.dump(json.loads(data), f, indent=4)
        sys.exit(0)
        
    elif args.loadFile:
        with open(args.loadFile, 'r') as f:
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
        new_id['username'] = rsa.pubkey.exportKey().decode()
        new_id['password'] = args.genkeys
        r = requests.post(url=url, data=json.dumps(new_id), headers=headers)
        if r.json()['status'] == 200:
            print('Key pair created - public key saved in the vault')
        else:
            print(r.json())
        sys.exit(0)
        
    else:
        # we need a valid vault id and password in all case below
        if args.id is not None:
            uid = args.id
        else:
            uid = input('Enter a IdentityId: ')
            if uid == '' or uid is None:
                print('Please enter a valid Identity name')
                sys.exit(-1)
                
        # for a new record, also ask for a username
        if args.new:
            if args.username:
                uname = args.username
            else:
                uname = input('Enter a User Name: ')
        
        if args.password:
            pwd = args.password
        else:
            pwd = getpass.getpass('Enter your password: ')

        # Retrieve the username / password pair using the given Identity
        headers = {'Content-type': 'application/json'}
        r = requests.get(url=url + '?uid=%s' % uid, headers=headers)
        id = r.json()

        if id['status'] == 200:
            curr_name = id['username']
            curr_pwd = id['password']
    
            # decrypt if needed
            if args.key:
                rsa = RSAcipher(certfile='priv_' + args.key + '.pem')
                curr_name = rsa.decrypt(curr_name)
                curr_pwd = rsa.decrypt(curr_pwd)
    
            # Check if passwords match or exit
            if curr_pwd != pwd:
                print('Password mismatch!')
                exit(-1)
                
        else:
            # No vault entry for that id - ok to create a new one with that identity
            curr_uname = ''
            curr_pwd = ''

        # delete a vault record
        if args.delete:
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
        
        # change the password in a record
        if args.newPassword:
            if pwd is not None:
                pwd = args.newPassword
            else:
                pwd = getpass.getpass('Enter your password: ')
            
            if args.username:
                uname = args.username
            else:
                uname = curr_name
                if uname == '':
                    uname = input('Enter your username')
                
            # encrypt if required
            if args.key:
                rsa = RSAcipher(certfile='pub_' + args.key + '.pem')
                uname = rsa.encrypt(uname)
                pwd = rsa.encrypt(pwd)
                
            new_id = dict()
            new_id['id'] = uid
            new_id['username'] = uname
            new_id['password'] = pwd
            
            r = requests.put(url=url, data=json.dumps(new_id), headers=headers)
            if r.json()['status'] == 200:
                print('Identity updated!')
            else:
                print(r.json())
            sys.exit(0)
        
        # create a new record
        if args.new:
            if curr_name != '' and curr_pwd != '':
                print('Cannot create a new record with the same id than an existing one')
                
            # create a new username / password entry
            if uname != '' and pwd != '' and curr_name == '':
                if args.key:
                    rsa = RSAcipher(certfile='pub_' + args.key + '.pem')
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

        # if vault read is requested, display the result if a correct password is given
        if curr_name != '':
            print('Username:password = ' + curr_name + ':' + curr_pwd)
        else:
            print('Password mismatch or no such identity in the vault')
        sys.exit(0)


if __name__ == "__main__":
    main()
