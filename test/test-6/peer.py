import socket
import sys
import json
import threading
import random

host = '127.0.0.1'
port1 = int(sys.argv[1])
port2 = int(sys.argv[2])
clientid1 = int(sys.argv[3])
clientid2 = int(sys.argv[4])




s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
def thread1 ():
    connected = False
    while not connected:
        try:
            s1.connect((host,port1))
            connected = True
        except Exception:
            connected = False
    # try:
        
    # except:
    #     print('client went')
    # if  msg == None:
    #     print('client went off')
    msg  = s1.recv(1024)
    while msg : 
        msg = json.loads(msg.decode())
        print(msg['msg'])
        msg  = s1.recv(1024)
        # try:
        #     msg  = s1.recv(1024)
        # except:
        #     print('client went')
        # if  msg == '':
        #     print('client went off')
    s1.close()

    
def thread2():
    s2.bind((host,port2))
    s2.listen()
    c,addr = s2.accept()
    msg = input()
    id = str(port1) + '-' + str(port2) 
    msg = json.dumps({'id':id,'msg':msg})
    try: 
        c.send(msg.encode())
    except:
        print('client mfiewf')
    while msg : 
        if (msg == '-1'):
            break
        msg = input()
        id = str(port1) + '-' + str(port2) 
        msg = json.dumps({'id':id,'msg':msg})        
        r = c.send(msg.encode())
        if r == 0:
            print('andfin')
        
        

send = threading.Thread(target=thread1,args=())
recieve = threading.Thread(target=thread2,args=())
send.start()
recieve.start()
send.join()
recieve.join()
