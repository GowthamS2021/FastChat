import socket
import json
from getpass import getpass
import psycopg2
import threading
import re
from datetime import datetime


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
        credentials = self.auth()
        self.credentials = credentials
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSuperSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.clientSuperSocket.connect((host, 7998))
        address = json.loads(self.clientSuperSocket.recv(1024).decode())[
                             'server']
        print(address)  # testing
        self.clientsocket.connect((host, address))
        self.clientsocket.sendall(json.dumps(
            {'name': credentials[0]}).encode())
        self.sendThread = threading.Thread(target=self.send, args=())
        self.recvThread = threading.Thread(target=self.recv, args=())
        self.sendThread.start()
        self.recvThread.start()

    def auth(self):
        found = False
        while not found:
            cmd = int(input("press 1 for Login else 0 for SignUp:"))
            if cmd == 1:
                username = input("Username:")
                password = getpass("Password:")
                cursor.execute(
                    '''SELECT password FROM auth WHERE username = %s''', (username,))
                output = cursor.fetchall()
                print(output)  # testing
                if len(output) == 0:
                    print('Such Credentials does not exist')
                elif output[0][0] == password:
                    found = True
                    self.print_all_msgs(username)
                    return (username, password)
            elif cmd == 0:
                username = input("Username:").strip(' ')
                password = getpass("Password:")
                co_password = getpass("Confirm Password:")
                if co_password == password:
                    cursor.execute(
                        '''SELECT password FROM auth WHERE username = %s ;''', (username,))
                    output = cursor.fetchall()
                    # print(output)
                    if len(output) == 0:
                        cursor.execute(
                            '''INSERT INTO auth(username,password) VALUES(%s,%s) ;''', (username, password))
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
            print("sender:" + x[0])
            print("time:" + x[3].strftime("%Y-%m-%d %H:%M:%S"))
            print("msg:" + x[2])

    def send(self):
        i = 0
        while i >= 0:

            name = input('To:').strip(' ')
            cursor.execute(
                '''SELECT * FROM auth WHERE username = %s''', (name,))
            output = cursor.fetchall()
            if len(output) == 0:
                print('such user doesn\'t exist')
                continue
            print("Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
            check = int(input())
            if check == 0:
                    # msg = input('Msg:')
                    # msgdict = {'id':id,'msg':msg}
                    # print(msgdict)
                    # self.clientsocket.send(json.dumps(msgdict).encode())
                    msg = ''
                    while msg == '':
                        msg = input('Msg:')
                        if msg == '':
                            print('Can\'t send a empty message')
                    msgdict = {'sender': self.credentials[0], 'reciever': name, 'msg': msg, 'time': datetime.now(
                    ).strftime("%Y-%m-%d %H:%M:%S")}
                    print(msgdict)  # testing
                    cursor.execute(
                        '''INSERT INTO message(sender,reciever,message,time) VALUES(%s,%s,%s,(SELECT CURRENT_TIMESTAMP))''', (self.credentials[0], name, msg,))
                    conn.commit()
                    self.clientsocket.send(json.dumps(msgdict).encode())
            else:
                msg = ""
                msgdict = {
                    'sender': self.credentials[0], 'reciever': name, 'msg': msg}
                self.clientsocket.send(json.dumps(msgdict).encode())
                imagename = input('imagename:')
                myfile = open(imagename, 'rb')
                imagedata = myfile.read(2048)
                while imagedata:
                    self.clientsocket.send(imagedata)
                    imagedata = myfile.read(2048)
            # i += 1

    def recv(self):

        while True:
            # print(1000)
            msgdict = self.clientsocket.recv(1024)
            today = datetime.now()
            basename = "recvimg"+str(today)+".jpg"
            # print(type(msgdict))
            if is_json(msgdict):
                # msgDict = json.loads(msgdict)
                # if msgDict['msg'] != "":
                #     print(msgDict['msg'])
                # msgdict  = self.clientsocket.recv(1024)
                msgdict = json.loads(msgdict.decode())
                if msgdict['msg'] != "":
                    print("sender:" + msgdict['sender'])
                    print("time:" + msgdict['time'])
                    print("msg:" + msgdict['msg'])
            else:
                while msgdict and is_json(msgdict) is not True:
                    with open(basename, 'ab') as myfile:
                        myfile.write(msgdict)
                    msgdict = self.clientsocket.recv(1024)
                # noofimages += 1
                if is_json(msgdict) is True:
                    msgdict = json.loads(msgdict)
                    if msgdict['msg'] != "":
                        print("sender:" + msgdict['sender'])
                        print("time:" + msgdict['time'])
                        print("msg:" + msgdict['msg'])
                myfile.close()
            # i += 1

    # def recv(self):        
    #     while True :
    #         msgdict  = self.clientsocket.recv(1024)
    #         msgdict = json.loads(msgdict.decode())
    #         print("sender:" + msgdict['sender'])
    #         print("time:" + msgdict['time'])
    #         print("msg:" + msgdict['msg'])


if __name__ == '__main__':
    Client  = client('127.0.0.1')
