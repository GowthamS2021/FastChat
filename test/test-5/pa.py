import subprocess
import threading
import time
import datetime

server_port = 8000
number_of_servers = 1

def superServer():
    print('superserver')
    subprocess.run(["python3", "superserver.py"],shell=False)

def server():
    print('server')
    time.sleep(2)
    subprocess.run(["python3","server.py" ,str(server_port-number_of_servers+1)],shell=False)

def client():
    print('client')
    time.sleep(2)
    p = subprocess.run(["python3","create_users.py"],shell = False,capture_output=True)
    time1 = datetime.datetime.now()
    subprocess.run(["python3","client.py"],shell = False,input=p.stdout)
    time2 = datetime.datetime.now()
    print(time2 -time1)
    print('client')

superServerThread = threading.Thread(target=superServer,args=())
superServerThread.start()

serverThreads = [threading.Thread(target=server,args=())]
serverThreads[0].start()

ClientThreads = []
for i in range(5):
    ClientThreads.append(threading.Thread(target=client,args=()))
    ClientThreads[i].start()
    # subprocess.run(["python3 client.py < python3 create_users.py"],shell = True)