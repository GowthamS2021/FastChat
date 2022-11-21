import socket
import json
import threading
import re


from datetime import datetime





def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

  
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
        while i >= 0:
            

            id = int(input('To:'))
            
            print("Would you like to send image or text message:\n Press 0 for text message \n, Press anything else for image ")
            check = int(input())
            if check == 0:

                    msg = input('Msg:')

                   
                    msgdict = {'id':id,'msg':msg}
                    print(msgdict)
                    self.clientsocket.send(json.dumps(msgdict).encode())
            else:

                msg = ""
                msgdict = {'id' : id, 'msg' : msg}
                self.clientsocket.send(json.dumps(msgdict).encode())
                imagename = input('imagename:')
                myfile = open(imagename,'rb')
                imagedata = myfile.read(2048)

                while imagedata :
                    
                    
                    
                    self.clientsocket.send(imagedata)
                    
                    imagedata = myfile.read(2048)
                    

                    
                
                
                

                


            i+=1

    def recv(self):        
        i = 0
        noofimages = 0
        a = True
        

        while True :
            # print(1000) 
            msgdict  = self.clientsocket.recv(1024)
            today = datetime.now()

            basename = "recvimg"+str(today)+".PNG"
            # print(type(msgdict))
            if is_json(msgdict):

                msgDict = json.loads(msgdict)
                if msgDict['msg'] != "":
                


                
                    print(msgDict['msg'])
            

           
                
            else :
                a = False
                while msgdict and is_json(msgdict) is not True:
                    with open(basename,'ab') as myfile:
                        myfile.write(msgdict)
                    msgdict  = self.clientsocket.recv(1024)
                noofimages += 1
                
                if is_json(msgdict) is True:
                    msgDict = json.loads(msgdict)
                    if msgDict['msg'] != "":
                        print(msgDict['msg'])

               
                

                
                myfile.close()

            
            i+=1

if __name__ == '__main__':
    Client  = client('127.0.0.1',8000)
