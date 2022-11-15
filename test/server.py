import socket
import threading

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#r = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '127.0.0.1'
port_1 = 8000
port_2 = 5000
s.bind((host, port_1))
#r.connect(('127.0.0.1', port_2))

def send_msg(msg):    
    s.listen(1)
    c, addr = s.accept()
    c.send(msg.encode())
    c.close()

def recv_msg():
    
    msg = s.recv(1024)
    while msg:
        print('Received:' + msg.decode())
        msg = s.recv(1024)


send = threading.Thread(target=send_msg,args=['Hey connected'])
send.run()

receive = threading.Thread(target=recv_msg)
receive.run()

send.close()
receive.close()

#c.close()
