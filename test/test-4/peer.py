import socket
import sys
import json
import threading
import asyncio

host = '127.0.0.1'
port = int(sys.argv[1])
socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


async def thread1 ():
    connected = False
    loop = asyncio.get_event_loop()    
    loop.sock_connect(s1,port1)
    # msg  = s1.recv(1024)
    # while msg : 
    #     msg = json.loads(msg.decode())
    #     print(msg['msg'])
    #     msg = s1.recv(1024)
    # s1.close()
    msg = loop.sock_recv(s1,1024)
    print(msg)
    return msg

async def handle_client(c):
    msg = input()

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



async def thread2():
    s2.bind((host,port2))
    s2.listen()
    s2.setblocking(False)
    loop = asyncio.get_event_loop()
    c,addr = await loop.sock_accept(s1)
    while True:
        loop.create_task(handle_client(c))
    
        

# send = threading.Thread(target=thread1,args=())
# recieve = threading.Thread(target=thread2,args=())
# send.start()
# recieve.start()
# send.join()
# recieve.join()

async def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        thread1(),
        thread2()
    ))


if __name__ == '__main__':
    asyncio.run(main())