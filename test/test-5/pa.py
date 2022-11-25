import subprocess
import threading
import time
import sys
import datetime
import string
import random
from random import randint

server_port = 6000
number_of_servers = 1
number_of_clients = 0
subprocess.run(['python3','database.py','postgres','password','postgres'],shell = False)
times = {}
names_of_clients = []
def superServer():
    print('superserver')
    subprocess.run(["python3", "superserver.py"],shell=False)

def server():
    print('server')
    time.sleep(2)
    subprocess.run(["python3","server.py" ,str(server_port-number_of_servers+1)],shell=False)

def client():
    # print('client')    
    global number_of_clients
    number_of_clients += 1
    client_id = number_of_clients
    out = open('input.txt','w+')
    input_file= open('input.txt','r')
    # names_of_clients.append(input_file.readlines()[1])
    p = subprocess.run(["python3","create_users.py"],stdout = out)
    time1 = datetime.datetime.now()
    process = subprocess.run(["python3","client.py"],stdin = input_file,capture_output=True)
    time2 = datetime.datetime.now()
    print(number_of_clients,time2 -time1)
    # time.sleep(2*sys.argv[2]) # for allowing the clients to connect / server-client delays
    # for i in range(sys.argv[2]):
    #     j = randint(0,sys.argv[2]-1)
    #     # process_1 = subprocess.run(["python3","create_dms.py"],capture_output=True)
    #     process.stdin(0)
    #     process.stdin(names_of_clients[j])
    #     process.stdin(0)
    #     process.stdin(''.join(random.choices(string.ascii_uppercase + string.digits, k=15)))
    #     process.stdin.flush()
    #     times[(client_id,j)] = (datetime.datetime.now(),)
    # print('client')

superServerThread = threading.Thread(target=superServer,args=())
superServerThread.start()

serverThreads = []
for i in range(int(sys.argv[1])):
    number_of_servers += 1
    serverThreads.append(threading.Thread(target=server,args=()))
    serverThreads[i].start()
    time.sleep(2) # server -server delays


time.sleep(2) # server-client delay
ClientThreads = []
for i in range(int(sys.argv[2])):
    ClientThreads.append(threading.Thread(target=client,args=()))
    ClientThreads[i].start()
    time.sleep(2) # server-client delay
    # subprocess.run(["python3 client.py < python3 create_users.py"],shell = True)

# for i in range()



superServerThread.join()
for x in serverThreads:
    x.join()
for x in ClientThreads:
    x.join()

exit(0)

