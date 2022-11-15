import threading
from getpass import getpass # for the hidden password
import json;
import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
r = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '127.0.0.1'
port_1 = 5000
port_2 = 8000


def send_msg(msg):  
    s.bind((host, port_1))  
    s.listen(1)
    c, addr = s.accept()
    c.send(msg.encode())

def recv_msg():
    r.connect(('127.0.0.1', port_2))
    msg = s.recv(1024)
    while msg:
        print('Received:' + msg.decode())
        msg = s.recv(1024)


#cmd = input('SignUp  / LogIn  \ntype to continue ')

#if cmd == 'SignUp' :
    # sign up request 
#id = input("Enter an ID:")
#password = getpass("Password:")
user_details = {
    'ID':'id',
    'password':'password'
}
_user_details = json.dumps(user_details);


receive = threading.Thread(target=recv_msg)
send = threading.Thread(target=send_msg,args=[_user_details])
send.run()
receive.run()

send.close()
receive.close()

#c.close()

#print(password)

    # ask id password confirm password
    # check if the same id has been used
#else :
#    pass # ask the id and password
