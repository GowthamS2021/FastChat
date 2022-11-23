                             FASTCHAT
TEAM MEMBERS:

GOWTHAM S(210050059)
KANISHK GARG(210050080)
SONI NAMAN NIRMAL(210050151)

Till now , we have implemented multiclient - multiserver connections , sending images from one client to another ,Postgre-SQL for
storing messages and images in the database ,authentication, end-to-end encryption for messages , we have started groups just now and 
end-to-end encryption for images is left out.

Working and implementation of our code :

We have used the threading library for implementing multiclient-multiserver connections , used Postgre-SQL for 
database and RSA for end-to-end encryption and for we have used round-robin load-balancing 

We have 3 files superserver.py, server.py and client.py , superserver.py is the server where all the servers are
connected to . It has a database in which every message and image is stored , and used when needed , it has two sockets
ClientSocket and SuperSockets into which server and clients connect .
 
Both server and clients have access to database and send messages to database first and then to their respective clients/servers .

We used Postgre SQL for authentication . 




