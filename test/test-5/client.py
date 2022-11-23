import socket
import json
from getpass import getpass
import psycopg2
import string
import random
import hashlib
import threading
import os
import base64
import rsa
from datetime import datetime

try:

        def is_json(myjson):
            try:
                json.loads(myjson)
            except ValueError as e:
                return False
            return True

        conn = psycopg2.connect(
            database='fastchatdb',
            user='postgres',
            password='password',
            host='localhost',
            port='5432'
        )

        cursor = conn.cursor()

        class client:
            def __init__(self, host):
                self.credentials = self.auth()
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
                    {'name': self.credentials[0]}).encode())
                self.sendThread = threading.Thread(target=self.send, args=())
                self.recvThread = threading.Thread(target=self.recv, args=())
                self.sendThread.start()
                self.recvThread.start()

            def download_unsavedimages(self, username):
                cursor.execute(
                    '''SELECT * FROM image WHERE reciever = %s''', (username,))
                output = cursor.fetchall()
                if len(output) != 0:
                        today = datetime.now()
                        basename = "recvimg"+str(today)+".jpg"
                        stry = output[0][5]
                        for x in output:
                            if not x[4]:
                                    myfile = open(basename, 'ab')
                                    if x[5] != stry:
                                        basename = "recvimg"+str(today)+".jpg"
                                        myfile.close()
                                        myfile = open(basename, 'ab')
                                        myfile.write(x[2])
                                        cursor.execute(
                                            '''UPDATE image SET displayed = TRUE  WHERE img = %s ''', (x[2],))
                                        conn.commit()

                                    else:
                                        myfile.write(x[2])
                                        cursor.execute(
                                            '''UPDATE image SET displayed = TRUE  WHERE img = %s ''', (x[2],))
                                        conn.commit()

            def auth(self):
                found = False
                while not found:
                    cmd = int(input("press 1 for Login else 0 for SignUp:"))
                    if cmd == 1:
                        username = input("Username:")
                        password = getpass("Password:")
                        cursor.execute(
                            '''SELECT password,salt FROM auth WHERE username = %s''', (username,))
                        output = cursor.fetchall()
                        print(output)  # testing
                        if len(output) == 0:
                            print('Such Credentials does not exist')
                        elif self.isSame(password, output[0][0], output[0][1]):
                            found = True
                            return (username, password)
                    elif cmd == 0:
                        username = input("Username:").strip(' ')
                        password = getpass("Password:")
                        co_password = getpass("Confirm Password:")
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
                cursor.execute(
                    '''SELECT * FROM message WHERE reciever = %s''', (username,))
                output = cursor.fetchall()
                for x in output:
                    if x[2] != '':
                        decrypted = self.decrypt(x[2])
                        if decrypted != '':
                            print("sender:" + x[0])
                            print("time:" + x[3].strftime("%Y-%m-%d %H:%M:%S"))
                            print("msg:" + decrypted)

            def encrypt_password(self,password):
                random_string = ''.join(random.choices(string.ascii_uppercase +string.digits, k=5))
                return (hashlib.sha256((password+random_string).encode()).hexdigest(),random_string)
    
            def isSame(self,password,stored,salt):
                return (hashlib.sha256((password+salt).encode()).hexdigest() == stored)
            

            def generateKeys(self,username):
                (publicKey, privateKey) = rsa.newkeys(1024)
                # with open('keys/publicKey.pem', 'wb') as p:
                #     p.write(publicKey.save_pkcs1('PEM'))
                self.publicKey = publicKey
                with open('keys/privateKey_'+str(username)+'.pem', 'w+') as p:
                    p.write(privateKey.save_pkcs1('PEM').decode())        
                return publicKey
            
            # def loadKeys(self):
            #     with open('keys/publicKey.pem','rb') as p:
            #         publicKey = rsa.PublicKey.load_pkcs1(p.read())
            #     with open('keys/privateKey.pem','rb') as p:
            #         privateKey = rsa.PrivateKey.load_pkcs1(p.read())
            #     return privateKey, publicKey
            
            def encrypt_message(self,message, key):
                return rsa.encrypt(message.encode('ascii'), key).decode('ISO-8859-1')

            def decrypt(self,ciphertext):
                with open('keys/privateKey_'+self.credentials[0]+'.pem','rb') as p:
                    key = rsa.PrivateKey.load_pkcs1(p.read())
                try:
                    return rsa.decrypt(ciphertext.encode('ISO-8859-1'), key).decode()
                except:
                    return False

            def sign(message, key):
                return rsa.sign(message.encode('ascii'), key, 'SHA-1')
            
            def verify(message, signature, key):
                try:
                    return rsa.verify(message.encode('ascii'), signature, key,) == 'SHA-1'
                except:
                    return False

# <<<<<<< HEAD
# def is_json(myjson):
#   try:
#     json.loads(myjson)
#   except ValueError as e:
#     return False
#   return True


# conn = psycopg2.connect(
#     database='fastchatdb',
#     user='postgres',
#     password='password',
#     host='localhost',
#     port='5432'
# )

# cursor = conn.cursor()


# class client:
#     def __init__(self, host):
#         self.credentials = self.auth()
#         self.print_all_msgs(self.credentials[0])
#         self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.clientSuperSocket = socket.socket(
#             socket.AF_INET, socket.SOCK_STREAM)
#         self.clientSuperSocket.connect((host, 7998))
#         address = json.loads(self.clientSuperSocket.recv(1024).decode())[
#                              'server']
#         print(address)  # testing
#         self.clientsocket.connect((host, address))
#         self.clientsocket.sendall(json.dumps(
#             {'name': self.credentials[0]}).encode())
#         self.sendThread = threading.Thread(target=self.send, args=())
#         self.recvThread = threading.Thread(target=self.recv, args=())
#         self.sendThread.start()
#         self.recvThread.start()

    

#     def auth(self):
#         found = False
#         while not found:
#             cmd = int(input("press 1 for Login else 0 for SignUp:"))
#             if cmd == 1:
#                 username = input("Username:")
#                 password = getpass("Password:")
#                 cursor.execute(
#                     '''SELECT password,salt FROM auth WHERE username = %s''', (username,))
#                 output = cursor.fetchall()
#                 print(output)  # testing
#                 if len(output) == 0:
#                     print('Such Credentials does not exist')
#                 elif self.isSame(password,output[0][0],output[0][1]):
#                     found = True                    
#                     return (username, password)
#             elif cmd == 0:
#                 username = input("Username:").strip(' ')
#                 password = getpass("Password:")
#                 co_password = getpass("Confirm Password:")
#                 if co_password == password:
#                     cursor.execute(
#                         '''SELECT password,salt FROM auth WHERE username = %s ;''', (username,))
# =======
            # def print_all_msgs(self, username):
            #     cursor.execute(
            #         '''SELECT * FROM message WHERE reciever = %s''', (username,))
            #     output = cursor.fetchall()
            #     for x in output:
            #         if x[2] != "":
            #             print("sender:" + x[0])
            #             print("time:" + x[3].strftime("%Y-%m-%d %H:%M:%S"))
            #             print("msg:" + x[2])
            
                            
                                        
    
                            
                        
                        
                        
                
            

            def send(self):
                i = 0
                while i >= 0:

                    name = input('To:').strip(' ')
                    cursor.execute(
                        '''SELECT * FROM auth WHERE username = %s''', (name,))
# >>>>>>> remotes/origin/naman
                    output = cursor.fetchall()
                    if len(output) == 0:
# <<<<<<< HEAD                        
# =======
                        print('such user doesn\'t exist')
                        continue
                    print("Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
                    check = int(input())
                    if check == 0:
                        
                            # msg = ''
                            # while msg == '':
                            #     msg = input('Msg:')
                            #     if msg == '':
                            #         print('Can\'t send a empty message')
                            # msgdict = {'sender': self.credentials[0], 'reciever': name, 'msg': msg, 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            # cursor.execute(
                            #     '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, msg,))
                            # conn.commit()
                            # self.clientsocket.send(json.dumps(msgdict).encode())
                            msg = ''
                            while msg == '':
                                msg = input('Msg:')
                                if msg == '':
                                    print('Can\'t send a empty message')
                            cursor.execute('''SELECT publicKeyn,publicKeye FROM auth WHERE username = %s''',(name,))
                            public = cursor.fetchall()[0]
                            encrypted_msg = self.encrypt_message(msg,(rsa.key.PublicKey(int(public[0]),public[1])))
                            msgdict = {'sender': self.credentials[0], 'reciever': name, 'msg': encrypted_msg, 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            print(msgdict)  # testing
                            cursor.execute(
                                '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, encrypted_msg))
                            conn.commit()
                            self.clientsocket.send(json.dumps(msgdict).encode())
                    else:
                        msg = ""
                        msgdict = {
                            'sender': self.credentials[0], 'reciever': name, 'msg': msg }
                        cursor.execute(
                            '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name ,msg))
                        conn.commit()
                        self.clientsocket.send(json.dumps(msgdict).encode())
                        
                        imagename = input('imagename:')
                        myfile = open(imagename, 'rb')
                        imagedata = myfile.read(2048)
                        cursor.execute(
                            '''INSERT INTO image( sender, reciever , img , time ,displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], name ,imagedata, imagename))
# >>>>>>> remotes/origin/naman
                        conn.commit()
                        while imagedata:
                            self.clientsocket.send(imagedata)
                            imagedata = myfile.read(2048)
                            cursor.execute(
                            '''INSERT INTO image( sender, reciever , img , time, displayed , imagenames) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP),FALSE,%s)''', (self.credentials[0], name ,imagedata ,imagename ))
                            conn.commit()
                    # i += 1

            def recv(self):

                while True:
                    
                    msgdict = self.clientsocket.recv(1024)
                    today = datetime.now()
                    basename = "recvimg"+str(today)+".jpg"
                    if is_json(msgdict):
                        msgdict = json.loads(msgdict.decode())
                        if msgdict['msg'] != "":
                            print("sender:" + msgdict['sender'])
                            print("time:" + msgdict['time'])
                            print("msg:" + self.decrypt(msgdict['msg']))
                    else:
# <<<<<<< HEAD
 

   

    # def send(self):
    #     i = 0
    #     while i >= 0:
    #         name = input('To:').strip(' ')
    #         cursor.execute(
    #             '''SELECT * FROM auth WHERE username = %s''', (name,))
    #         output = cursor.fetchall()
    #         if len(output) == 0:
    #             print('such user doesn\'t exist')
    #             continue
    #         print("Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
    #         check = int(input())
    #         if check == 0:
    #                 # msg = input('Msg:')
    #                 # msgdict = {'id':id,'msg':msg}
    #                 # print(msgdict)
    #                 # self.clientsocket.send(json.dumps(msgdict).encode())
    #                 msg = ''
    #                 while msg == '':
    #                     msg = input('Msg:')
    #                     if msg == '':
    #                         print('Can\'t send a empty message')
    #                 cursor.execute('''SELECT publicKeyn,publicKeye FROM auth WHERE username = %s''',(name,))
    #                 public = cursor.fetchall()[0]
    #                 encrypted_msg = self.encrypt_message(msg,(rsa.key.PublicKey(int(public[0]),public[1])))
    #                 msgdict = {'sender': self.credentials[0], 'reciever': name, 'msg': encrypted_msg, 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    #                 print(msgdict)  # testing
    #                 cursor.execute(
    #                     '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, encrypted_msg))
    #                 conn.commit()
    #                 self.clientsocket.send(json.dumps(msgdict).encode())
    #         else:
    #             msg = ""
    #             msgdict = {
    #                 'sender': self.credentials[0], 'reciever': name, 'msg': msg}
    #             self.clientsocket.send(json.dumps(msgdict).encode())
    #             imagename = input('imagename:')
    #             myfile = open(imagename, 'rb')
    #             imagedata = myfile.read(2048)
    #             while imagedata:
    #                 self.clientsocket.send(imagedata)
    #                 imagedata = myfile.read(2048)
    #         # i += 1

    # def recv(self):

    #     while True:
    #         # print(1000)
    #         msgdict = self.clientsocket.recv(1024)
    #         today = datetime.now()
    #         basename = "recvimg"+str(today)+".jpg"
    #         # print(type(msgdict))
    #         if is_json(msgdict):
    #             # msgDict = json.loads(msgdict)
    #             # if msgDict['msg'] != "":
    #             #     print(msgDict['msg'])
    #             # msgdict  = self.clientsocket.recv(1024)
    #             msgdict = json.loads(msgdict.decode())
    #             if msgdict['msg'] != "":
    #                 print("sender:" + msgdict['sender'])
    #                 print("time:" + msgdict['time'])
    #                 print("msg:" + self.decrypt(msgdict['msg']))
    #         else:
    #             while msgdict and is_json(msgdict) is not True:
    #                 with open(basename, 'ab') as myfile:
    #                     myfile.write(msgdict)
    #                 msgdict = self.clientsocket.recv(1024)
    #             # noofimages += 1
    #             if is_json(msgdict) is True:
    #                 msgdict = json.loads(msgdict)
    #                 if msgdict['msg'] != "":
    #                     print("sender:" + msgdict['sender'])
    #                     print("time:" + msgdict['time'])
    #                     print("msg:" + msgdict['msg'])
    #             myfile.close()
            # i += 1

    # def recv(self):        
    #     while True :
    #         msgdict  = self.clientsocket.recv(1024)
    #         msgdict = json.loads(msgdict.decode())
    #         print("sender:" + msgdict['sender'])
    #         print("time:" + msgdict['time'])
    #         print("msg:" + msgdict['msg'])


# if __name__ == '__main__':
#     Client  = client('127.0.0.1')
# =======
                        # siti = ""
                        # sit = ""
                        # basename = ""
                        while msgdict and is_json(msgdict) is not True:
                            # cursor.execute('''SELECT * FROM image WHERE img = %s''', (msgdict,))
                            # out = cursor.fetchall()
                            # if len(out)!= 0 :
                                    
                            #         # print(len(out[0]))
                            #         sit = out[0][5]
                                    
                            #         if sit != siti:
                            #             spst = sit.split(".")
                            #             sit = siti
                            #             basename = "recv"+str(out[0][0]) +" " + str(out[0][1]) + str(out[0][3]) + "."+ spst[-1]
                                        
                                    
                            with open(basename, 'ab') as myfile:
                                myfile.write(msgdict)
                                cursor.execute('''UPDATE image SET displayed = TRUE  WHERE img = %s ''',(msgdict,))
                                conn.commit()
                                
                                
                            msgdict = self.clientsocket.recv(1024)
                        # noofimages += 1
                        if is_json(msgdict) is True:
                            msgdict = json.loads(msgdict)
                            if msgdict['msg'] != "":
                                print("sender:" + msgdict['sender'])
                                print("time:" + msgdict['time'])
                                print("msg:" + self.decrypt(msgdict['msg']))
                        myfile.close()
                            
            def __del__(self):
                    cursor.execute('''UPDATE server SET serverId = %s  WHERE clientId = %s ''',(-1,self.credentials[0]))
                    conn.commit()
                
                

        if __name__ == '__main__':
            
            Client  = client('127.0.0.1')
            
            print("end")
except KeyboardInterrupt:
    print ('Caught KeyboardInterrupt')             
                
# >>>>>>> remotes/origin/naman
