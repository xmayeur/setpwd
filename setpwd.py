
import requests
import getpass
import sys
import json
import argparse
from RSAcipher import RSAcipher


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
    parser.add_argument("-if", "--inputfile", required=False,
                        help="specify a text file containing a password - file name is used as username")
    parser.add_argument("-of", "--outputfile", required=False,  action='store_true',
                        help="Save the password to the file having  the Username as name")
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

        if args.inputfile is not None:
            with open(args.inputfile, 'r') as f:
                uname = args.inputfile
                pwd = f.read()
                
        # for a new record, also ask for a username
        if args.new and uname == '':
            if args.username:
                uname = args.username
            else:
                uname = input('Enter a User Name: ')
            
        if args.password:
            pwd = args.password
        elif pwd == '':
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
                rsa = RSAcipher(certfile=args.key + '.key')
                curr_name = rsa.decrypt(curr_name)
                curr_pwd = rsa.decrypt(curr_pwd)
    
            # Check if passwords match or exit
            if curr_pwd != pwd and args.outputfile is None:
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
            
            if args.username and uname != '':
                uname = args.username
            elif uname != '':
                uname = curr_name
                if uname == '':
                    uname = input('Enter your username')
                
            # encrypt if required
            if args.key:
                rsa = RSAcipher(certfile= args.key + '.pub')
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
                    rsa = RSAcipher(certfile=args.key + '.pub')
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
