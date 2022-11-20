import socket
import json
import threading

class client:
    def __init__(self,host,port):
        self.clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                self.clientsocket.connect((host,port))
                connected = True
            except Exception:
                connected = False
        self.sendThread = threading.Thread(target=self.send,args=())
        self.recvThread = threading.Thread(target=self.recv,args=())
        self.sendThread.start()
        self.recvThread.start()


    def send(self):
        i = 0
        while i != 10:
            id = int(input('To:'))
            msg = input('Msg:')
            msgdict = {'id':id,'msg':msg}
            print(msgdict)
            self.clientsocket.send(json.dumps(msgdict).encode())
            i+=1

    def recv(self):        
        i = 0
        while True :
            # print(1000) 
            msg  = self.clientsocket.recv(1024)
            # print(1000)
            # msg = json.loads(msg.decode())
            print(msg.decode())
            i+=1

if __name__ == '__main__':
    Client  = client('127.0.0.1',8000)
