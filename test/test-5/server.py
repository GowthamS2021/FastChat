import socket
import json
import psycopg2
import sys
import threading



idnow = -1

conn = psycopg2.connect(
    database='fastchatdb',
    user='postgres',
    password='password',
    host = 'localhost',
    port = '5432'
)

cursor = conn.cursor()

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

class server():
    def __init__(self,host,port):
        self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.supersocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serversocket.bind((host,port))
        self.serversocket.listen()
        self.supersocket.connect((host,7999))
        infodict = self.supersocket.recv(1024)
        self.supersocket.sendall(json.dumps({'address':port}).encode())
        self.server_id = json.loads(infodict.decode())['id']
        self.clients = {}
        self.threads = {}
        self.supersocketThread = threading.Thread(target=self.recv_supersocket,args=())
        self.supersocketThread.start()

    def accept(self):
        connection,address = self.serversocket.accept()
        print('heyy')# testing
        infodict = connection.recv(1024) # send the username 
        client_id = json.loads(infodict.decode())['name']
        self.clients[client_id] = (connection,address)
        print(self.clients)# testing
        recvThread = threading.Thread(target=self.handle_recv,args=(connection,))
        self.threads[client_id] = recvThread
        cursor.execute('''SELECT serverId FROM server WHERE clientId = %s ;''',(client_id,))
        output = cursor.fetchall()
        if len(output) == 0:
            cursor.execute('''INSERT INTO server(serverId,clientId) VALUES(%s,%s)''',(self.server_id,client_id))
        else :
            cursor.execute('''UPDATE server SET serverId = %s  WHERE clientId = %s ''',(self.server_id,client_id))
        conn.commit()
        self.supersocket.sendall('True'.encode()) # have to change this
        recvThread.start()    
        

    def recv_supersocket(self):
        while True:
            msgdict = json.loads(self.supersocket.recv(1024).decode())
            print(msgdict)# testing
            # cursor.execute('''SELECT serverId FROM server WHERE clientId = %s''',(msgdict['reciever'],))
            # output = cursor.fetchall()
            # print(output)
            #if output[0] != self.server_id:
            #    self.supersocket.sendall(json.dumps(msgdict).encode())
            #else :
            try :
                self.clients[msgdict['reciever']][0].sendall(json.dumps(msgdict).encode())
            except KeyError:
                continue

    def handle_recv(self,connection):
        # count = 0 
        # icount = count       
        while True:
            msgdict = connection.recv(1024)
            if is_json(msgdict):        
                msgDict = json.loads(msgdict,strict=False)
                if msgDict['msg'] == "" :
                    idnow = msgDict['reciever']
                    c = self.clients[msgDict['reciever']][0]
                    c.send(msgdict)
                    # count += 1 
                    # if count == 1:
                    #     icount = count
                else:
                    # msgdict = json.loads(connection.recv(1024).decode())
                    print(msgDict)# testing
                    cursor.execute('''SELECT serverId FROM server WHERE clientId = %s ;''',(msgDict['reciever'],))
                    output = cursor.fetchall()
                    print(output)# testing
                    print(self.server_id)# testing
                    if len(output) == 0 or output[0]!=self.server_id:
                        self.supersocket.sendall(json.dumps(msgDict).encode())
                    elif output[0] == self.server_id :
                        try:
                            self.clients[msgdict['reciever']][0].sendall(json.dumps(msgDict).encode())
                        except :
                            continue
            else :
                # if icount != count:
                #     c = self.clients[idnow][0]
                #     msg1 = {'id':-1,'msg':""}
                #     # print(msgdict)
                #     self.clientsocket.send(json.dumps(msg1).encode())
                #     icount = count 
                c = self.clients[idnow][0]
                c.send(msgdict)

if __name__ == '__main__':
    Server = server('127.0.0.1',int(sys.argv[1]))
    while True:
        Server.accept()