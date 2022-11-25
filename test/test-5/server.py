import socket
import json
import psycopg2
import sys
import threading
idnow = ""

conn = psycopg2.connect(
    database='fastchatdb',
    user='server',
    password='server@fastchat',
    host='localhost',
    port='5432'
)

cursor = conn.cursor()


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


class server():
    def __init__(self, host, port):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.supersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.listen()
        self.supersocket.connect((host, 7999))
        infodict = self.supersocket.recv(1024)
        self.supersocket.sendall(json.dumps({'address': port}).encode())
        self.server_id = json.loads(infodict.decode())['id']
        self.clients = {}
        self.threads = {}
        self.supersocketThread = threading.Thread(
            target=self.recv_supersocket, args=())
        self.supersocketThread.start()

    def accept(self):
        connection, address = self.serversocket.accept()
        # print('heyy')# testing
        infodict = json.loads(connection.recv(1024).decode())  # send the username
        client_id = infodict['name']
        infodict['isClientAdded'] = True
        self.supersocket.send(json.dumps(infodict).encode())
        # if not infodict['PrivateKeys']:            
        #     recv_dict = self.supersocket.recv(4096)
        #     connection.sendall(recv_dict)
        self.clients[client_id] = (connection, address)
        # print(self.clients)# testing
        recvThread = threading.Thread(
            target=self.handle_recv, args=(connection,))
        self.threads[client_id] = recvThread        
        cursor.execute("SELECT serverId FROM server WHERE clientId= \'" + client_id + "\' ;")
        # output = []
        # try:
        #     output = cursor.fetchall()
        # except:
        #     print('\''+client_id+'\'')
        #     output = []
        try :
            output = cursor.fetchall() 
        except:
            output = []
        print(output)
        if len(output) == 0:
            print('\''+client_id+'\'')
            cursor.execute(
                '''INSERT INTO server(serverId,clientId) VALUES(%s,%s) ;''', (self.server_id, client_id))
        else:
            cursor.execute(
                '''UPDATE server SET serverId = %s  WHERE clientId = %s ;''', (self.server_id, client_id))
        conn.commit()
        # self.supersocket.sendall(json.dumps(
        #     {'isClientAdded': True}).encode()) 
        recvThread.start()

    def recv_supersocket(self):
        while True:            
            msgdict = self.supersocket.recv(1024)
            if is_json(msgdict):
                

                msgDict = json.loads(msgdict, strict=False)
                # print(msgDict)# testing
                if msgDict.get('msg') == "":
                        idnow = msgDict['reciever']
                else:
                
                        try:
                            self.clients[msgDict['reciever']][0].sendall(
                                json.dumps(msgDict).encode())
                        except KeyError:
                            continue
# >>>>>>> 6cc16c7549a8db843ebcf86359fdf6716bdbf3c5
            else:
                if self.clients.get(idnow) != None:                    
                    try:
                        self.clients[idnow][0].send(msgdict)
                    except BrokenPipeError or KeyError:
                        continue

    def handle_recv(self, connection):
        global idnow
        while True:
            msgdict = connection.recv(1024)
            if is_json(msgdict):#msgdict.get('img') == None:
                msgDict = json.loads(msgdict, strict=False)
                # msgDict = msgdict
                if msgDict.get('msg') == "" :
                    idnow = msgDict['reciever']
                    while True:
                        try:
                            cursor.execute('''SELECT serverId FROM server WHERE clientId = %s ;''', (msgDict['reciever'],))
                            output = cursor.fetchone()
                            break
                        except:
                            continue
                    # print(output)# testing
                    # print(self.server_id)# testing
                    if len(output) == 0 or output[0] != self.server_id :
                        self.supersocket.sendall(json.dumps(msgDict).encode())
                    elif output[0] == -1:
                        continue
                    elif output[0] == self.server_id:
                        try:
                            self.clients[msgDict['reciever']][0].sendall(
                                json.dumps(msgDict).encode())
                        except:
                            continue
                # elif msgDict.get('key') != None:
                #     cursor.execute('''SELECT serverId FROM server WHERE clientId = %s ;''', (msgDict['reciever'],))
                #     output = cursor.fetchall()
                #     if len(output) == 0 or output[0][0] != self.server_id:
                #         # >>>>>>> remotes/origin/naman
                #         self.supersocket.sendall(json.dumps(msgDict).encode())
                #     elif output[0][0] == self.server_id:
                #         try:
                #             self.clients[msgDict['reciever']][0].sendall(
                #                 json.dumps(msgDict).encode())
                #         except:
                #             # print(msgDict)
                #             continue
                else:
                    # msgdict = json.loads(connection.recv(1024).decode())
                    # print(msgDict)# testing
                    if msgDict.get('Client-shutdown') != None and msgDict['Client-shutdown'] == True:
                        cursor.execute(
                            '''UPDATE server SET serverId = -1  WHERE clientId = %s ;''', (msgDict['client_id'],))
                        conn.commit()
                        self.supersocket.sendall(json.dumps({'isClientAdded': False}).encode())
                        continue
                    print(msgDict)
                    cursor.execute('''SELECT serverId FROM server WHERE clientId = %s ;''', (msgDict['reciever'],))
                    output = cursor.fetchall()
                    if len(output) == 0 or output[0][0] != self.server_id:
                        # >>>>>>> remotes/origin/naman
                        self.supersocket.sendall(json.dumps(msgDict).encode())
                    elif output[0][0] == self.server_id:
                        try:
                            self.clients[msgDict['reciever']][0].sendall(
                                json.dumps(msgDict).encode())
                        except:
                            print(msgDict)
                            continue
            else:
                # if icount != count:
                #     c = self.clients[idnow][0]
                #     msg1 = {'id':-1,'msg':""}
                #     # print(msgdict)
                #     self.clientsocket.send(json.dumps(msg1).encode())

                #     icount = count z

                #     icount = count
                cursor.execute(
                    '''SELECT serverId FROM server WHERE clientId = %s ;''', (idnow,))
                try:
                    output = cursor.fetchall()
                    # print(output)# testing
                    # print(self.server_id)# testing
                    if len(output) == 0 or output[0] != self.server_id:
                        self.supersocket.sendall(msgdict)
                    elif output[0] == self.server_id:

                        self.clients[idnow][0].sendall(msgdict)

                except:
                    continue
                # c = self.clients[idnow][0]
                # c.send(msgdict)


if __name__ == '__main__':
    Server = server('127.0.0.1', int(sys.argv[1]))
    while True:
        Server.accept()
