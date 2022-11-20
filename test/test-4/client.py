import socket
import sys
import json
import threading
import asyncio

host = '127.0.0.1'
port = 8000
socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
loop = asyncio.get_event_loop()

async def thread1 ():    
    msg = await loop.sock_recv(socket,1024)
    print(msg.decode())
    return msg

# async def handle_client(c):
#     msg = input()

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
    
        

# send = threading.Thread(target=thread1,args=())
# recieve = threading.Thread(target=thread2,args=())
# send.start()
# recieve.start()
# send.join()
# recieve.join()

async def main():
    await loop.sock_connect(socket,(host,port))
    # loop.create_task(thread1())
    # loop.run_forever()
    
    


if __name__ == '__main__':
    # asyncio.run(main())
    loop.run_until_complete(asyncio.gather(
        main()
    ))
    loop.create_task(thread1())
    loop.run_forever()