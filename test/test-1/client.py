import socket

host = '127.0.0.1'
port = 5000
s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.connect((host,port))
msg  = s1.recv(1024)
while msg : 
    print(msg.decode())
    msg = input()
    s1.sendall(msg.encode())
    msg = s1.recv(1024)
s1.close()