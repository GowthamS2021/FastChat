import socket
import json
import socketserver
import threading

    
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
        while True:
            msgdict = connection.recv(1024)
            msgdict = json.loads(msgdict)
            print(msgdict)
            c = self.clients[msgdict['id']][0]
            c.send(msgdict['msg'].encode())

if __name__ == '__main__':
    Server = server('127.0.0.1',8000)
    while True:
        Server.accept()