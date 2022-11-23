import sys
import socket
import selectors
import types
import json


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        msg = sock.recv(1024)  # Should be ready to read
        while msg : 
            msg = json.loads(msg.decode())
            print(msg['msg'])
            msg = s1.recv(1024)
            
        sel.unregister(sock)
        sock.close()

        
    if mask & selectors.EVENT_WRITE:
        sock.bind((host,port))
        sock.listen()
        c,addr = sock.accept()
        data.outb = input()
        
        id = str(port) + '-' + str(port) 
        data.outb = json.dumps({'id':id,'msg':data.outb})
        c.send(data.outb.encode())
        while data.outb : 
            if (data.outb == '-1'):
                break
            data.outb = input()
            id = str(port) + '-' + str(port) 
            data.outb = json.dumps({'id':id,'msg':data.outb})
            c.send(data.outb.encode())
            
            # sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

sel = selectors.DefaultSelector()

# ...

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()

lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

