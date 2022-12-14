import socket
import json
from getpass import getpass
import psycopg2
import threading
import re
from datetime import datetime

conn = psycopg2.connect(
    database='fastchatdb',
    user='superserver',
    password='superserver@123',
    host = 'localhost',
    port = '5432'
)
conn.autocommit = True
cursor = conn.cursor()

globrecv = ""

def is_json(myjson):
  """ Checks if a particular object is a valid json string

    :param myjson: parameter to check
    :type myjson: string,byte

  """
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True



class superServer:
    """This is the super-server class, using this , we do the load-balancing
    in case of multiple servers
    
    :param supersocket: accepts connections from the server
    :type supersocket: socket
    :param clientsocket: accepts connections from the clients
    :type clientsocket: socket
    :param server: list of connections to the server
    :type server: list
    :param client: list of connections to the client
    :type client: list
    """
    def __init__(self,host):
        """ Constructor method, initializes everything

        :param host: address of the host
        :type host: string
        """
        self.supersocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.supersocket.bind((host,7999))
        self.clientsocket.bind((host,7998))
        self.supersocket.listen()
        self.clientsocket.listen()
        self.server = []
        self.threads = []

    def accept_server(self):
        """Accepts connections from the servers and receives and sends messages to servers
        """
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
        """Accepts connections from the clients and connects them to the server which 
        is connected to the least number of clients(round-robin) doing the load balancing
        """
        while True:
            connection,address = self.clientsocket.accept()
            servers = sorted(self.server,key=(lambda x: x[2]))
            connection.send(json.dumps({'server':servers[0][3]}).encode())
            connection.close() # doubt

    def handle_recv(self,connection,id):
        """Receives and sends messages to servers
        
        :param connection: The connection from which it receives this message
        :type connection: socket
        :param id: The server id from which it received the message
        :type id: int
        """
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
                    if msgdict.get('Privatekeys') == False:
                        cursor.execute('''SELECT * FROM privateKeyTable WHERE username = %s''',(msgdict['name'],))
                        output = cursor.fetchall()
                        # print(msgdict)
                        # print(output)
                        connection.sendall(json.dumps({'reciever':msgdict['name'],'privateKeyn':output[0][1],'privateKeye':output[0][2],'privateKeyd':output[0][3],'privateKeyp':output[0][4],'privateKeyq':output[0][5]}).encode())
                    continue
                elif msgdict.get('isClientAdded') == False:
                    self.server[id][2] -= 1
                    continue                

                if msgdict['msg'] == '' :
                    globrecv = msgdict['reciever']                 
                    
                    
                cursor.execute('''SELECT serverid FROM server WHERE clientid = %s ;''',(msgdict['reciever'],))
                output = cursor.fetchall()
                print(output)# testing
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
