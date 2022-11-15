import socket
import sys
import threading

host = '127.0.0.1'
port1 = int(sys.argv[1])
port2 = int(sys.argv[2])
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
    msg  = s1.recv(1024)
    while msg : 
        print(msg.decode())
        msg = s1.recv(1024)
    s1.close()

    
def thread2():
    s2.bind((host,port2))
    s2.listen()
    c,addr = s2.accept()
    msg = input()
    c.send(msg.encode())
    while msg : 
        if (msg == '-1'):
            break
        c.send(msg.encode())
        msg = input()

send = threading.Thread(target=thread1,args=())
recieve = threading.Thread(target=thread2,args=())
send.start()
recieve.start()
send.join()
recieve.join()