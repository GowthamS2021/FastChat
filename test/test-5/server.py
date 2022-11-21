import socket
import json
import socketserver
import threading

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

idnow = -1

class server():
    def __init__(self,host,port):
        self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serversocket.bind((host,port))
        self.serversocket.listen()
        self.clients = {}
        self.threads = {}

    def accept(self):
        connection,address = self.serversocket.accept()
        id = len(self.clients)
        self.clients[id] = (connection,address)
        recvThread = threading.Thread(target=self.handle_recv,args=(connection,))
        self.threads[id] = recvThread
        recvThread.start()

    def handle_recv(self,connection):
        # count = 0 
        # icount = count       
        while True:
            msgdict = connection.recv(1024)
            if is_json(msgdict):
                
                msgDict = json.loads(msgdict,strict=False)
                if msgDict['msg'] == "" :

                    idnow = msgDict['id']
                    c = self.clients[msgDict['id']][0]
                    c.send(msgdict)
                    # count += 1 
                    # if count == 1:
                    #     icount = count
                else:
                    # if count != 0:

                    print(msgdict)
                    c = self.clients[msgDict['id']][0]
                    c.send(msgdict)
                    count = 0
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
    Server = server('127.0.0.1',8000)
    while True:
        Server.accept()