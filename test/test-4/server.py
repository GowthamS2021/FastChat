import asyncio
import json
import socket
import sys
import threading

host = '127.0.0.1'
port = 8000
socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
loop = asyncio.get_event_loop()
connection = None

# async def thread1 ():
#     connected = False
#     loop = asyncio.get_event_loop()    
#     loop.sock_connect(s1,port1)
#     # msg  = s1.recv(1024)
#     # while msg : 
#     #     msg = json.loads(msg.decode())
#     #     print(msg['msg'])
#     #     msg = s1.recv(1024)
#     # s1.close()
#     msg = loop.sock_recv(s1,1024)
#     print(msg)
#     return msg

async def handle_client(c):
    msg = input()
    await loop.sock_sendall(c,msg.encode())
    print(msg)
    return True
    # id = str(port1) + '-' + str(port2) 
    # msg = json.dumps({'id':id,'msg':msg})
    # c.send(msg.encode())
    # while msg : 
    #     if (msg == '-1'):
    #         break
    #     msg = input()
    #     id = str(port1) + '-' + str(port2) 
    #     msg = json.dumps({'id':id,'msg':msg})
    #     c.send(msg.encode())



async def create():
    global connection
    socket.bind((host,port))
    socket.listen()
    socket.setblocking(False)
    connection,_ = await loop.sock_accept(socket)
    # while True:
    # loop.create_task(handle_client(c))  
    # loop.run_forever()
        



if __name__ == '__main__':
    # asyncio.run(main())
    loop.run_until_complete(asyncio.gather(
        create()
    ))
    loop.create_task(handle_client(connection)) 
    loop.run_forever()
