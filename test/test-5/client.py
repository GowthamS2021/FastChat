import socket
import json
from getpass import getpass
import psycopg2
import string
import random
import hashlib
import threading
import sys
import os
import base64
import rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
from datetime import datetime

# try:


def is_json(myjson):
    """Checks if a particular object is a valid json string
        
    :param myjson: parameter to check
    :type myjson: string,byte
    """
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


conn = psycopg2.connect(
    database='fastchatdb',
    user='client',
    password='Client@fastchat',
    host='localhost',
    port='5432'
)

cursor = conn.cursor()


class client:
    """ | This is a client class , it represents the client side of our code, it has a constructor Client(host).It has eight parameters and twelve member functions 

    :param credentials: login details of the client
    :type credentials: tuple
    :param privateKeysFound: to keep track of privateKeys
    :type privateKeysFound: bool
    :param var: Checks whether the client is present or not
    :type var: bool
    :param clientsocket: connects to the server 
    :type clientsocket: socket
    :param clientSuperSocket: connects to the SuperServer 
    :type clientSuperSocket: socket
    :param address: address of the server to which the client is connected to
    :type address: string
    :param sendThread: Thread for sending messages
    :type sendThread: thread
    :param recvThread: Thread for receiving messages
    :type recvThread: thread
    """
    def __init__(self, host):
        """ Constructor method, initializes everything

        :param host: address of the host
        :type host: string
        """
        self.credentials = self.auth()
        print(self.credentials[0])
        self.privateKeysFound = os.path.isfile(
            'keys/privateKey_'+str(self.credentials[0])+'.pem')
        print(self.privateKeysFound)
        self.var = True
        self.key = None
        self.iv = None
        self.print_all_msgs(self.credentials[0])
        self.download_unsavedimages(self.credentials[0])
        self.clientsocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.clientSuperSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.clientSuperSocket.connect((host, 7998))
        address = json.loads(self.clientSuperSocket.recv(1024).decode())[
            'server']
        print(address)  # testing
        self.clientsocket.connect((host, address))
        self.clientsocket.sendall(json.dumps(
            {'name': self.credentials[0], 'PrivateKeys': self.privateKeysFound}).encode())
        if not self.privateKeysFound:
            output = json.loads(self.clientsocket.recv(4096).decode())
            self.generate_privatekeyfile(output)
        try:
            self.sendThread = threading.Thread(target=self.send, args=())
            self.recvThread = threading.Thread(target=self.recv, args=())
            self.sendThread.start()
            self.recvThread.start()
        except KeyboardInterrupt:
            print('Yo handled man!!')

    def download_unsavedimages(self, username):
        """ Downloads the images which client received while he was offline

        :param username: username of the client
        :type username: string
        """
        cursor.execute(
            '''SELECT * FROM image WHERE reciever = %s ORDER BY TIME ASC''', (username,))
        output = cursor.fetchall()
        if len(output) != 0:
            today = datetime.now()
            basename = "recvimg"+str(today)+"_"+str(self.credentials[0])+".jpg"
            stry = output[0][5]
            for x in output:
                if not x[4]:
                    myfile = open(basename, 'ab')
                    if x[5] != stry:
                        basename = "recvimg"+str(today)+"_"+str(self.credentials[0])+".jpg"
                        myfile.close()
                        myfile = open(basename, 'ab')
                        myfile.write(x[2])
                        cursor.execute(
                            '''UPDATE image SET displayed = TRUE  WHERE img = %s AND reciever = %s ''', (x[2],self.credentials[0]))
                        conn.commit()
                    else:
                        myfile.write(x[2])
                        cursor.execute(
                            '''UPDATE image SET displayed = TRUE  WHERE img = %s AND reciever = %s ''', (x[2],self.credentials[0]))
                        conn.commit()

    def auth(self):
        """ It is used for authentication of client when we enter its login/SignUp

        :return: returns username and password of the client while signing up
        :rtype: tuple
        """
        found = False
        while not found:
            cmd = int(input("press 1 for Login else 0 for SignUp:"))
            if cmd == 1:
                username = input("Username:")
                # password = getpass("Password:")
                password = input("Password:")
                cursor.execute(
                    '''SELECT password,salt FROM auth WHERE username = %s''', (username,))
                output = cursor.fetchall()
                print(output)  # testing
                if len(output) == 0:
                    print('Such Credentials does not exist')
                elif self.isSame(password, output[0][0], output[0][1]):
                    found = True

                    # self.privateKeysFound = False
                    return (username, password)
            elif cmd == 0:
                username = input("Username:").strip(' ')
                # password = getpass("Password:")
                password = input("Password:")
                # co_password = getpass("Confirm Password:")
                co_password = input("Confirm Password:")

                if co_password == password:
                    cursor.execute(
                        '''SELECT password,salt FROM auth WHERE username = %s ;''', (username,))
                    output = cursor.fetchall()
                    # print(output)
                    if len(output) == 0:
                        (password, salt) = self.encrypt_password(password)
                        self.generateKeys(username)
                        cursor.execute(
                            '''INSERT INTO auth(username,password,salt,publicKeyn,publicKeye) VALUES(%s,%s,%s,%s,%s) ;''', (username, password, salt, str(self.publicKey.n), self.publicKey.e))
                        conn.commit()
                        print('Registered!!')
                        found = True
                        return (username, password)
                    elif output[0][0] == password:
                        print('Such Credentials already exist')
                    else:
                        print(output)  # testing
                else:
                    print('password and confirm password don\'t match')
            else:
                print('Enter a valid command')

    def print_all_msgs(self, username):
        """ Print all the messages which client received while he was offline

        :param username: username of the client
        :type username: string
        """
        cursor.execute(
            '''SELECT * FROM message WHERE reciever = %s''', (username,))
        output = cursor.fetchall()
        for x in output:
            if x[2] != '':
                decrypted = self.decrypt_message(x[2])
                if decrypted != '':
                    print("sender:" + x[0])
                    print("time:" + x[3].strftime("%Y-%m-%d %H:%M:%S"))
                    print("msg:" + decrypted)

    def generate_privatekeyfile(self, dict):
        """generated a .pem file containing private keys
        
        :param dict: dictionary containing private keys
        :type dict: dictionary
        """
        privateKey = rsa.key.PrivateKey(int(dict['privateKeyn']), int(dict['privateKeye']), int(
            dict['privateKeyd']), int(dict['privateKeyp']), int(dict['privateKeyq']))
        with open('keys/privateKey_'+str(self.credentials[0])+'.pem', 'w+') as p:
            p.write(privateKey.save_pkcs1('PEM').decode())

    def encrypt_password(self, password):
        """ Encryption of password

        :param password: password to be encrypted
        :type password: string
        :return: hashed value of password
        :rtype: tuple
        """
        random_string = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=5))
        return (hashlib.sha256((password+random_string).encode()).hexdigest(), random_string)

    def isSame(self, password, stored, salt):
        """ Checks if th salted password is same as the stored password
        
        :param password: string having password
        :type password: bytes
        :param salt: string having salt 
        :type password: bytes
        :param stored: stored password
        :type stored: string
        """

        return (hashlib.sha256((password+salt).encode()).hexdigest() == stored)

    def generateKeys(self, username):
        """ generate oublic and private keys for the user using rsa
        
        :param username: denotes the username of the user
        :type username: string
        """
        (publicKey, privateKey) = rsa.newkeys(1024)
        # with open('keys/publicKey.pem', 'wb') as p:
        #     p.write(publicKey.save_pkcs1('PEM'))
        self.publicKey = publicKey
        cursor.execute('''INSERT INTO privateKeyTable(username,privateKeyn,privateKeye,privateKeyd,privateKeyp,privateKeyq) 
        values(%s,%s,%s,%s,%s,%s)''', (username, str(privateKey.n), str(privateKey.e), str(privateKey.d), str(privateKey.p), str(privateKey.q)))
        with open('keys/privateKey_'+str(username)+'.pem', 'w+') as p:
            p.write(privateKey.save_pkcs1('PEM').decode())

    def encrypt_message(self, message, key):
        """ encrypts the message given a key

        :param message: message to be encrypted
        :type message: string
        :param key: key which is used to encrypt the message
        :type key: bytes
        :return: encrypted message
        :rtype: string
        """
        return base64.b64encode(rsa.encrypt(message.encode(), key)).decode()
    
    def encrypt_images(self,imagedata,key):
        """ encrypts the imagebytes given a key

        :param imagedata: imagedata to be encrypted
        :type imagedata: bytes
        :param key: key which is used to encrypt the message
        :type key: bytes
        :return: encrypted image
        :rtype: bytes
        """
        return base64.b64encode(rsa.encrypt(imagedata,key)).decode()

    def decrypt_message(self, ciphertext):
        """ Decrypts the message given the encoded message
        
        :param ciphertext: encrypted message
        :type ciphertext: string 
        :return: decrypted message
        :rtype: string

        """
        with open('keys/privateKey_'+self.credentials[0]+'.pem', 'rb') as p:
            key = rsa.PrivateKey.load_pkcs1(p.read())
        try:
            return rsa.decrypt(base64.b64decode(ciphertext.encode()), key).decode()
        except:
            return False

    def decrypt_images(self,imagedata):
        """ Decrypts the message given the encrypted image
        
        :param imagedata: encrypted image
        :type imagedata: bytes 
        :return: decrypted image
        :rtype: bytes

        """
        with open('keys/privateKey_'+self.credentials[0]+'.pem', 'rb') as p:
            key = rsa.PrivateKey.load_pkcs1(p.read())
        # try:
        return rsa.decrypt(base64.b64decode(imagedata.encode()), key)
        # except:
        #     return False

    def send(self):
        """ Used for sending messages from one client to other client or client
        to its group
        """

        # try:
        while self.var:
            # name = input('Type \'exit\' to exit \n To:').strip(' ')
            # if (name == 'exit'):
            #     # print('anen')
            #     self.var = False
            #     self.update()
            #     return
            print("Press 0 for DM and anything else for group operations or Type 'exit' to exit FastChat")
            checks = input()
            if checks == '0':
                name = input('To:').strip(' ')
                # if (name == 'exit'):
                #     # print('anen')
                #     self.var = False
                #     self.update()
                #     return
                cursor.execute('''SELECT * FROM auth WHERE username = %s''', (name,))

                output = cursor.fetchall()
                if len(output) == 0:
                    print('such user doesn\'t exist')
                    continue
                print(
                    "Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
                check = int(input())
                if check == 0:
                    msg = ''
                    while msg == '':
                        msg = input('Msg:')
                        if msg == '':
                            print('Can\'t send a empty message')
                    cursor.execute('''SELECT publicKeyn,publicKeye FROM auth WHERE username = %s''',(name,))
                    public = cursor.fetchall()[0]
                    encrypted_msg = self.encrypt_message(msg,(rsa.key.PublicKey(int(public[0]),public[1])))
                    msgdict = {'sender': self.credentials[0], 'reciever': name, 'msg': encrypted_msg, 'time': datetime.now(
                    ).strftime("%Y-%m-%d %H:%M:%S")}
                    print(msgdict)  # testing
                    cursor.execute(
                        '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, encrypted_msg))
                    conn.commit()
                    self.clientsocket.send(json.dumps(msgdict).encode())
                else:
                    msg = ""

                    msgdict = {
                        'sender': self.credentials[0], 'reciever': name, 'msg': msg}
                    cursor.execute(
                        '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, msg))
                    conn.commit()
                    self.clientsocket.send(json.dumps(msgdict).encode())

                    imagename = input('imagename:')
                    myfile = open(imagename, 'rb')
                    imagedata = myfile.read(2048)
                    cursor.execute(
                        '''INSERT INTO image( sender, reciever , img , time ,displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], name, imagedata, imagename))

                    conn.commit()
                    while imagedata:
                        self.clientsocket.sendall(imagedata)
                        imagedata = myfile.read(2048)
                        if not imagedata:
                            break
                        cursor.execute(
                            '''INSERT INTO image( sender, reciever , img , time, displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], name, imagedata, imagename))
                        conn.commit()
                    # msg = ""
                    # # key = Fernet.generate_key()
                    # # print(key)
                    # msgdict = {
                    #     'sender': self.credentials[0], 'reciever': name, 'msg': msg}
                    # cursor.execute(
                    #     '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP));''', (self.credentials[0], name, msg))
                    # conn.commit()
                    # self.clientsocket.send(json.dumps(msgdict).encode())

                    # imagename = input('imagename:')
                    # # myfile = open(imagename, 'rb')
                    # # imagedata = myfile.read(117)
                    # cursor.execute('''SELECT publicKeyn,publicKeye FROM auth WHERE username = %s;''',(name,))
                    # public = cursor.fetchall()[0]
                    # # image_key = get_random_bytes(16)
                    # # print(image_key)
                    # # cipher = AES.new(image_key,AES.MODE_CBC)
                    # # encrypted_image_key = self.encrypt_images(image_key,(rsa.key.PublicKey(int(public[0]),public[1])))
                    # # # encrypted_image,_ = cipher.encrypt_and_digest(imagedata)
                    # # # encrypted_image = self.encrypt_images(imagedata,(rsa.key.PublicKey(int(public[0]),public[1])))
                    # # encrypted_iv = self.encrypt_images(cipher.iv,(rsa.key.PublicKey(int(public[0]),public[1])))
                    # # print(cipher.iv)
                    # # key = Fernet.generate_key()
                    # # with open('info/key.txt', mode='wb+') as keyValue:
                    # #     keyValue.write(key)
                    # # msgdict = {'key':encrypted_image_key,'iv':encrypted_iv,'reciever':name}
                    # # self.clientsocket.send(json.dumps(msgdict).encode())
                    # with open(imagename, 'rb') as f:
                    #     content = f.read(4096)
                    #     if not content:
                    #         break
                    #     # encrypted_image = base64.b64encode(cipher.encrypt(pad(content,AES.block_size)))
                    #     # hexValue = binascii.hexlify(content)
                    #     # f = Fernet(key)
                    #     # encHexVal = f.encrypt(hexValue) 
                    #     self.clientsocket.sendall(content)
                    #     cursor.execute(
                    #     '''INSERT INTO image( sender, reciever , img, time ,displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s);''', (self.credentials[0], name,content, imagename))
                    #     conn.commit()
                    # # with open('info/encryptedHex.txt', mode='wb+') as hexValueFile:
                    # #     hexValueFile.write(encHexVal)
                    # # self.clientsocket.sendfile(open('info/encryptedHex.txt',mode='rb'))
                    # # cursor.execute(
                    # #     '''INSERT INTO image( sender, reciever , img, key, time ,displayed , imagenames) VALUES(%s,%s,%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s);''', (self.credentials[0], name,encrypted_image, encrypted_image_key, encrypted_iv, imagename))

                    # # conn.commit()
                    # # while imagedata:
                    # #     self.clientsocket.sendall(encrypted_image)
                    # #     imagedata = myfile.read(117)
                    # #     if not imagedata:
                    # #         break
                    # #     # encrypted_image,_ = cipher.encrypt_and_digest(imagedata)
                    # #     # encrypted_image = base64.b64encode(cipher.encrypt(pad(imagedata,AES.block_size))).decode()
                    # #     encrypted_image = self.encrypt_images(imagedata,(rsa.key.PublicKey(int(public[0]),public[1])))
                    
            elif checks == 'exit':
                self.var = False
                self.update()
                return
            else:

                print("press 0 for making new group ,1 for adding and removing participants from an existing group if you are admin, 2 for group chatting , any other thing for exiting")
                checkgroup = int((input()))
                if checkgroup == 0:

                    print("Enter the groupname and non- zero group_id")
                    try:
                        groupname = ""
                        id = -1
                        output = [1]
                        while len(output) != 0:
                            groupname = input()
                            id = int(input())
                            cursor.execute(
                                '''SELECT * FROM Groups WHERE group_name = %s AND id = %s ;''', (groupname, id))
                            output = cursor.fetchall()
                        cursor.execute(
                            '''INSERT INTO Groups( group_name, participant ,is_admin ,id ) VALUES(%s,%s,TRUE,%s)''', (groupname, self.credentials[0], id))
                        conn.commit()
                    except:
                        output = []
                        cursor.execute(
                            '''INSERT INTO Groups( group_name, participant ,is_admin ,id ) VALUES(%s,%s,TRUE,%s)''', (groupname, self.credentials[0], id))
                        conn.commit()

                elif checkgroup == 1:
                    output = []
                    print("Press 0 to delete participant and 1 to insert participant")
                    take_input = int(input())
                    if take_input == 0:
                        print("Enter the groupname and non- zero group_id")

                        groupname = input()
                        id = int(input())
                        name = input('Remove:').strip(' ')
                        cursor.execute(
                            '''SELECT * FROM auth WHERE username = %s''', (name,))

                        outp = cursor.fetchall()
                        if len(outp) == 0:

                            print('such user doesn\'t exist')
                        else:
                            cursor.execute(
                                '''SELECT * FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ;''', (groupname, id, self.credentials[0]))
                            output = cursor.fetchall()
                            if len(output) == 0:
                                print("The participant is not in the group")

                            else:
                                print(output)
                                if output[0][2]:
                                    cursor.execute(
                                        '''SELECT * FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ;''', (groupname, id, name))
                                    outp = cursor.fetchone()
                                    if len(outp) != 0:
                                        cursor.execute(
                                            '''DELETE FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ; ''', (
                                                groupname, id, name)
                                        )
                                        conn.commit()
                                    else:
                                        print(
                                            "The participant to be removed is not in the group")

                                else:
                                    print("Participant is not the admin")

                    else:
                        print("Enter the groupname and non- zero group_id")

                        groupname = input()
                        id = int(input())
                        name = input('Add:').strip(' ')
                        cursor.execute(
                            '''SELECT * FROM auth WHERE username = %s''', (name,))

                        outp = cursor.fetchall()
                        if len(outp) == 0:

                            print('such user doesn\'t exist')
                        else:
                            cursor.execute(
                                '''SELECT * FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ;''', (groupname, id, self.credentials[0]))
                            output = cursor.fetchall()
                            if len(output) == 0:
                                print("The participant is not in the group")

                            else:
                                print(output[0][2])
                                if output[0][2]:
                                    cursor.execute(
                                        '''SELECT * FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ;''', (groupname, id, name))
                                    outp = cursor.fetchall()
                                    if len(outp) != 0:
                                        print(
                                            "The person already exists in the group")
                                    else:
                                        cursor.execute(
                                            '''INSERT INTO Groups( group_name, participant ,is_admin ,id ) VALUES(%s,%s,FALSE,%s)''', (groupname, name, id))
                                        conn.commit()
                                else:
                                    print("Participant is not the admin")
                elif checkgroup == 2:
                    print("Enter the groupname and non- zero group_id")
                    groupname = input()
                    id = int(input())
                    cursor.execute(
                        '''SELECT * FROM Groups WHERE group_name = %s AND id = %s AND participant = %s ;''', (groupname, id, self.credentials[0]))
                    output = cursor.fetchone()
                    if len(output) == 0:
                        print("The participant is not in the group")
                    else:
                        print(
                            "Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
                        check = int(input())
                        if check == 0:
                            cursor.execute(
                                '''SELECT participant FROM Groups WHERE group_name = %s AND id = %s  ;''', (groupname, id,))
                            output = cursor.fetchall()
                            msg = ''
                            while msg == '':
                                msg = input('Msg:')
                                if msg == '':
                                    print('Can\'t send a empty message')
                            for i in output:
                                cursor.execute('''SELECT publicKeyn,publicKeye FROM auth WHERE username = %s''',(i[0],))
                                public = cursor.fetchall()[0]
                                encrypted_msg = self.encrypt_message(msg,(rsa.key.PublicKey(int(public[0]),public[1])))
                                msgdict = {'sender': self.credentials[0], 'reciever': i[0], 'msg': encrypted_msg, 'time': datetime.now(
                                ).strftime("%Y-%m-%d %H:%M:%S")}
                                print(msgdict)  # testing
                                print(i[0])

                                cursor.execute(
                                    '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], i[0], encrypted_msg))
                                conn.commit()
                                self.clientsocket.send(
                                    json.dumps(msgdict).encode())
                        else:
                            cursor.execute(
                                '''SELECT participant FROM Groups WHERE group_name = %s AND id = %s  ;''', (groupname, id,))
                            output = cursor.fetchall()
                            imagename = input('imagename:')
                            print(output)
                            for i in output:
                                msg = ""
                                msgdict = {
                                    'sender': self.credentials[0], 'reciever': i[0], 'msg': msg}
                                cursor.execute(
                                    '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], i[0], msg))
                                conn.commit()
                                self.clientsocket.sendall(
                                    json.dumps(msgdict).encode())

                                myfile = open(imagename, 'rb')
                                imagedata = myfile.read(2048)
                                cursor.execute(
                                    '''INSERT INTO image( sender, reciever , img , time ,displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], i[0], imagedata, imagename))

                                conn.commit()
                                while imagedata:
                                    self.clientsocket.sendall(imagedata)
                                    imagedata = myfile.read(2048)
                                    if not imagedata:
                                        break
                                    cursor.execute(
                                        '''INSERT INTO image( sender, reciever , img , time, displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], i[0], imagedata, imagename))
                                    conn.commit()

    def recv(self):
        """For receiving the messages from other clients either in the form of DM's
        or groupchats
        """
        while self.var:
            try:
                msgdict = self.clientsocket.recv(1024)
            except Exception or KeyboardInterrupt or socket.timeout:  # KeyboardInterrupt:
                return
            today = datetime.now()
            basename = "recvimg"+str(today)+"_"+str(self.credentials[0])+".jpg"
            if is_json(msgdict):#msgdict.get('img') == None:
                msgdict = json.loads(msgdict.decode())
                print(msgdict)
                # if msgdict.get('key') != None and msgdict.get('key') != "":
                #     self.key = msgdict['key']
                #     self.iv = msgdict['iv']
                #     print(msgdict)
                if msgdict['msg'] != "":
                    print("sender:" + msgdict['sender'])
                    print("time:" + msgdict['time'])
                    print("msg:" + self.decrypt_message(msgdict['msg']))
            else:
                # if self.iv != None:
                #     iv = self.decrypt_images(self.iv)
                # if self.key != None:
                #     key = self.decrypt_images(self.key)
                # print(iv)
                # print(key)
                # key = base64.b64decode(self.key.encode())
                # print(key)
                # with open('info/key.txt', mode='rb') as keyValue:
                #     key = keyValue.read()
                while msgdict :
                    with open(basename, 'ab') as myfile:
                        # key = Fernet.generate_key()                        
                        # f =Fernet(key)
                        # hexValue = f.decrypt(msgdict)
                        # binValue = binascii.unhexlify(hexValue)
                        myfile.write(msgdict)
                        # if iv == None and key == None :
                        #     cursor.execute(
                        #         '''SELECT key, iv FROM image WHERE img = %s AND reciever = %s;''', (msgdict,self.credentials[0]))
                        #     output = cursor.fetchone()
                        #     print(output)
                        #     key = self.decrypt_images(output[0][0])
                        #     iv = self.decrypt_images(output[0][1])
                        # encrypted_imagedata = msgdict
                        # cipher = AES.new(key,AES.MODE_CBC,iv)
                        # imagedata = unpad(cipher.decrypt(base64.b64decode(encrypted_imagedata)),AES.block_size) 
                        # imagedata = self.decrypt_images(encrypted_imagedata)
                        # myfile.write(i)
                        cursor.execute(
                            '''UPDATE image SET displayed = TRUE  WHERE img = %s AND reciever = %s;''', (msgdict,self.credentials[0]))
                        conn.commit()
                                          

                    msgdict = self.clientsocket.recv(1024)
                    if is_json(msgdict) is True:
                        break

                # noofimages += 1
                if is_json(msgdict) is True:
                    msgdict = json.loads(msgdict)
                    if msgdict['msg'] != "":
                        print("sender:" + msgdict['sender'])
                        print("time:" + msgdict['time'])
                        print("msg:" + self.decrypt_message(msgdict['msg']))
                # myfile.close()

    def update(self):
        """When client wants to leave this function is called, its job is to 
        disconnect the client from its presently connected server
        """
        self.clientsocket.send(json.dumps({'Client-shutdown':True,'client_id':self.credentials[0]}).encode())            
        self.clientsocket.shutdown(socket.SHUT_RDWR)
        # self.recvThread.join()

if __name__ == '__main__':
    Client = client('127.0.0.1')
    # print("end")
# except KeyboardInterrupt:
#     print ('Caught KeyboardInterrupt')

# >>>>>>> remotes/origin/naman
