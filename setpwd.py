import crypto_helpers as c
import getpass
import sys

db = input('Enter the database pathname')
aes = c.AEScipher(db=db)
uid = input('Enter a IdentityId:')
uname, pwd = aes.read(uid)

if uname == '':
    uname = input('Enter a new User Name: ')
    pwd1 = getpass.getpass('Enter a new password: ')
    pwd2 = getpass.getpass('Repeat the new password: ')
    if pwd1 != pwd2:
        print('Password mismatch!')
        sys.exit(1)
    else:
        aes.save(uid, uname, pwd1)
        print('Identity saved!')
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
            aes.remove(uid, pwd)
            print('Identify removed!')
            sys.exit(0)
        else:
            aes.save(uid, uname, pwd1)
            print('Identity saved!')
            sys.exit(0)
