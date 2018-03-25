import logging
import os

from base64 import b64encode, b64decode

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
if os.name == 'nt':
    logging.basicConfig(filename='crypto_h.log', level=logging.INFO)
else:
    logging.basicConfig(filename='/var/log/crypto_h.log', level=logging.INFO)
 

def create_keyset(name='key'):
    key = RSA.generate(2048)
    with open('priv_' + name + '.pem', 'wb') as f:
        f.write(key.exportKey('PEM'))
    pubkey = key.publickey()
    with open('pub_' + name + '.pem', 'wb') as f:
        f.write(pubkey.exportKey())


Base = declarative_base()


class Identity(Base):
    __tablename__ = 'id_tbl'
    uid = Column(String, primary_key=True)
    id = Column(String)


def create_table_id_tbl(db):
    engine = create_engine('sqlite:///'+db)
    Base.metadata.create_all(engine)


class AEScipher:
    def __init__(self, db='/conf/.id.db'):
        if os.name == 'nt':
            db = 'id.db'
        engine = create_engine('sqlite:///'+db)
        Base.metadata.bind = engine
        DBsession = sessionmaker()
        DBsession.bind = engine
        self.sql = DBsession()
        
        # self.identity = Identity(db)
        self.key = MD5.new(db.encode('utf-8')).digest()
 
    def encrypt(self, text):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return b64encode(iv + cipher.encrypt(text))

    def decrypt(self, msg):
        msg = b64decode(msg)
        iv = msg[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher.decrypt(msg[AES.block_size:]).decode()

    def save(self, uid, username, password):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        ID = username + ':' + password
        ID_ = b64encode(iv + cipher.encrypt(ID.encode()))
 
        # if self.identity.fetch(uid) is None:
        #     self.identity.add(uid, ID_)
        # else:
        #     self.identity.update(uid, ID_)
        
        row = self.sql.query(Identity).filter(Identity.uid == uid).first()
        if row is None:
            self.sql.add(Identity(uid=uid, id=ID_))
        else:
            row.ID = ID_
        self.sql.commit()
        
    def read(self, uid):
        # ID_ = self.identity.fetch(uid)
        row = self.sql.query(Identity).filter(Identity.uid == uid).first()
        
        if row is None:
            return '', ''
        else:
            ID_ = row.id
            ID_ = b64decode(ID_)
            iv = ID_[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CFB, iv)
            ID = cipher.decrypt(ID_[AES.block_size:]).decode()
            user = ID.split(':')[0]
            pwd = ID.split(':')[1]
            return user, pwd
    
    def remove(self, uid, pwd):
        _, pwd1 = self.read(uid)
        if pwd == pwd1:
            row = self.sql.query(Identity).filter(Identity.uid == uid).first()
            if row is not None:
                self.sql.delete(row)
                self.sql.commit()
                return True
            else:
                return False
            # self.identity.remove(uid)
            # return True
        else:
            return False

    def dump(self):
        rows = self.sql.query(Identity)
        dd = []
        for row in rows:
            d = dict()
            uid_ = row.uid
            ID_ = row.id
            ID_ = b64decode(ID_)
            iv = ID_[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CFB, iv)
            ID = cipher.decrypt(ID_[AES.block_size:]).decode()
            user = ID.split(':')[0]
            pwd = ID.split(':')[1]
            d['id'] = uid_
            d['username'] = user
            d['password'] = pwd
            dd.append(d)
            del d
        return json.dumps(dd, indent=4)
      
    def load(self, data):
        # dd = json.loads(data)
        for d in data:
            uid_ = d['id']
            user = d['username']
            pwd = d['password']
            self.save(uid_, user, pwd)
    
    def close(self):
        # self.identity.close()
        self.sql.close()
        

class RSAcipher:

    def __init__(self, certfile):
        self.key = RSA.importKey(open(certfile).read())
        self.rsa = PKCS1_OAEP.new(self.key)

    def encrypt(self, text):
        return b64encode(self.rsa.encrypt(text.encode())).decode()

    def decrypt(self, msg):
        try:
            return self.rsa.decrypt(b64decode(msg)).decode()
        except Exception as e:
            return None


def main():
    
    create_table_id_tbl(db='id.db')
    text = 'Hello Lobo'
    aes = AEScipher(db='id.db')
    msg = aes.encrypt(text.encode())
    if aes.decrypt(msg) != text:
        print('Failed AES encrypt-decrypt')
        return
        
    create_keyset('test')
    rsa = RSAcipher('pub_test.pem')
    msg = rsa.encrypt(text)
    rsa = RSAcipher('priv_test.pem')
    if rsa.decrypt(msg) != text:
        print('Failed RSA encrypt-decrypt')
        return

    user = 'KeyUser'
    pwd = 'KeyPwd123'
    uid = '20'
    
    aes.save(uid, user, pwd)
    user1, pwd1 = aes.read(uid)

    if user != user1 or pwd != pwd1:
        print('Failed user/pwd store & decode')
        return
    
    if not aes.remove(uid, pwd):
        print('Failed to remove uid')
        return
    
    for i in range(1, 10):
        user = 'user' + str(i)
        pwd = 'pwd' + str(i)
        uid = i
        aes.save(uid, user, pwd)
    
    dd = aes.dump()
    
    for i in range(1, 10):
        aes.remove(i, 'pwd'+str(i))
        
    aes.load(dd)
    dd1 = aes.dump()
    if dd == dd1:
        print(aes.dump())
    
    print('All tests passed')
    
    # perform some cleaning here - remove test files
    aes.close()
    os.remove('id.db')

    os.remove('priv_test.pem')
    os.remove('pub_test.pem')

    log = logging.getLogger()
    x = list(log.handlers)
    for i in x:
        log.removeHandler(i)
        i.flush()
        i.close()
    try:
        os.remove('crypto_h.log')
    except:
        pass
    

if __name__ == "__main__":
    main()
