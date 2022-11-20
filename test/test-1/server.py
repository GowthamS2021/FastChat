import socket
import threading


host = '127.0.0.1'
port = 5000

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host,port))
s.listen()
connection ,address = s.accept()

msg = input()
while msg : 
    if (msg == '-1'):
        break
    connection.send(msg.encode())
    st = connection.recv(1024)
    print(st.decode())
    msg = input()
    


