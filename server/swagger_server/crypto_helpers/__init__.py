import logging
import os
import sqlite3
from base64 import b64encode, b64decode

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA

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


class Identity:
    
    def __init__(self, db='id.db'):
        self.db = db

        try:
            self.connection = sqlite3.connect(db)
        except sqlite3.Error:
            logging.error('Cannot connect to the database: %s' % self.db)
            
        try:
            cursor = self.connection.cursor()
            sql = '''CREATE TABLE IF NOT EXISTS `id_tbl` (
                    `uid` text NOT NULL,
                    `ID` text NOT NULL,
                    PRIMARY KEY  (`uid`)
                    )
            '''
            cursor.execute(sql)
        except sqlite3.Error:
            logging.error('Cannot create table `id_tbl`')
  
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def __enter__(self):
        return self
    
    def close(self):
        self.connection.close()
       
    def add(self, uid, ID):
        try:
            cursor = self.connection.cursor()
            sql = 'INSERT INTO `id_tbl` (`uid`, `ID`) VALUES (?, ?)'
            cursor.execute(sql, (uid, ID))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error('Error adding record - %s' % e)
            return False
        
    def update(self, uid, ID):
        try:
            cursor = self.connection.cursor()
            sql = 'UPDATE `id_tbl` SET `ID` = ? WHERE `uid` = ?'
            cursor.execute(sql, (ID, uid))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error('Error adding record - %s' % e)
            return False

    def remove(self, uid):
        try:
            cursor = self.connection.cursor()
            sql = "DELETE FROM `id_tbl` WHERE `uid` = ?"
            cursor.execute(sql, (uid, ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error('Error deleting record - %s' % e)
            return False
        
    def fetch(self, uid):
        try:
            cursor = self.connection.cursor()
            sql = "SELECT `ID` FROM `id_tbl` WHERE `uid` = ?"
            cursor.execute(sql, (uid, ))
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return result[0]
        except sqlite3.Error as e:
            logging.error('Error fetching record - %s' % e)
            return None


class AEScipher:
    def __init__(self, db='id.db'):
        self.identity = Identity(db)
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
        ID_ = b64encode(iv + cipher.encrypt(ID))
 
        if self.identity.fetch(uid) is None:
            self.identity.add(uid, ID_)
        else:
            self.identity.update(uid, ID_)

    def read(self, uid):
        ID_ = self.identity.fetch(uid)
        if ID_ is None:
            return '', ''
        else:
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
            self.identity.remove(uid)
            return True
        else:
            return False
      
    def close(self):
        self.identity.close()
        

class RSAcipher:

    def __init__(self, certfile):
        self.key = RSA.importKey(open(certfile).read())
        self.rsa = PKCS1_OAEP.new(self.key)

    def encrypt(self, text):
        return b64encode(self.rsa.encrypt(text.encode()))

    def decrypt(self, msg):
        try:
            return self.rsa.decrypt(b64decode(msg)).decode()
        except Exception as e:
            return None


def main():
    
    id=Identity()
    id.add('abc', 'ID')
    uid=id.fetch('abc')
    print('uid')
    id.add('abc', 'ID1')
    id.update('abc', 'ID1')
    id.remove('abc')
    id.update('abc1', 'id')
    id.close()
    
    text = 'Hello Lobo'
    aes = AEScipher()
    msg = aes.encrypt(text)
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
    uid ='2'
    
    aes.save(uid, user, pwd)
    user1, pwd1 = aes.read(uid)

    if user != user1 or pwd != pwd1:
        print('Failed user/pwd store & decode')
        return
    
    print('All test passed')
    
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
