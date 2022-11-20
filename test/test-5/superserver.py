import socket
import threading
import json
import psycopg2

class superServer:
    def __init__(self,host,port):
        self.supersocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.supersocket.bind((host,port))
        self.supersocket.listen()
        self.server = {}
        self.threads = {}

    def accept(self):
        connection,address = self.supersocket.accept()
        id = len(self.server)
        self.server[id] = (connection,address)
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
    sserver = superServer('127.0.0.1',8000)
    while True:
        sserver.accept()