import socket
import json
from getpass import getpass
import psycopg2
import threading
import re
from datetime import datetime

conn = psycopg2.connect(
    database='fastchatdb',
    user='postgres',
    password='password',
    host = 'localhost',
    port = '5432'
)
conn.autocommit = True
cursor = conn.cursor()

globrecv = ""

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True



class superServer:
    def __init__(self,host):
        self.supersocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.supersocket.bind((host,7999))
        self.clientsocket.bind((host,7998))
        self.supersocket.listen()
        self.clientsocket.listen()
        self.server = []
        self.threads = []
        cursor.execute('''CREATE TABLE IF NOT EXISTS auth(
            username TEXT NOT NULL PRIMARY KEY,
            password TEXT NOT NULL ,
            salt TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS server(
            serverId integer NOT NULL ,
            clientId TEXT NOT NULL 
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS message(
            sender TEXT NOT NULL,
            reciever TEXT NOT NULL,
            message TEXT ,
            time TIMESTAMP
        )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS image(
            sender TEXT NOT NULL,
            reciever TEXT NOT NULL,
            img BYTEA,
            time TIMESTAMP,
            displayed BOOL,
            imagenames TEXT NOT NULL
        )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS g1roup(
            group_name TEXT NOT NULL,
            participant TEXT NOT NULL,
            is_admin BOOL,
            id integer NOT NULL
        )
        ''')
        conn.commit()

    def accept_server(self):
        while True:
            connection,address = self.supersocket.accept()
            id = len(self.server)            
            connection.send(json.dumps({'id':id}).encode())
            server_address = json.loads(connection.recv(1024).decode())['address']
            self.server.append([connection,address,0,server_address])
            recvThread = threading.Thread(target=self.handle_recv,args=(connection,id))
            self.threads.append(recvThread)
            recvThread.start()
            # print(self.server)# testing
    
    def accept_client(self):
        while True:
            connection,address = self.clientsocket.accept()
            servers = sorted(self.server,key=(lambda x: x[2]))
            connection.send(json.dumps({'server':servers[0][3]}).encode())
            connection.close() # doubt

    def handle_recv(self,connection,id):
        global globrecv
        while True:
            msg = connection.recv(1024)
            if is_json(msg):
                # if msg == 'True':
                #     self.server[id][2] += 1
                #     continue
                msgdict = json.loads(msg)
                if msgdict.get('isClientAdded') == True:
                    self.server[id][2] += 1
                    continue
                if msgdict['msg'] == '' :
                    globrecv = msgdict['reciever']
                    
                    
                    
                cursor.execute('''SELECT serverid FROM server WHERE clientid = %s ;''',(msgdict['reciever'],))
                output = cursor.fetchall()
                print(output[0][0])# testing
                print(self.server)# testing
                try:
                    if len(output) != 0:
                        self.server[output[0][0]][0].send(json.dumps(msgdict).encode())
                except IndexError:
                    continue     
            else:
                # if msg == 'True':
                #     self.server[id][2] += 1
                #     continue
                cursor.execute('''SELECT serverid FROM server WHERE clientid = %s ;''',(globrecv,))
                output = cursor.fetchall()
                # print(output[0][0])# testing
                # print(self.server)# testing
                try:
                    if len(output) != 0:
                        self.server[output[0][0]][0].send(msg)
                except IndexError:
                    continue 
                
                
                

if __name__ == '__main__':
    sserver = superServer('127.0.0.1')
    thread1 = threading.Thread(target=sserver.accept_server,args=())
    thread2 = threading.Thread(target=sserver.accept_client,args=())
    thread1.start()
    thread2.start()
