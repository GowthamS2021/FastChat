# FastChat
Software Systems Lab Project

# TEAM MEMBERS:

* GOWTHAM S(210050059)
* KANISHK GARG(210050080)
* SONI NAMAN NIRMAL(210050151)

# Implementation so far
Till now , we have implemented 
* **multiclient - multiserver connections** 
* **sending images from one client to another** 
* **Postgre-SQL for storing messages and images in the database**
* **authentication**
* **end-to-end encryption for messages**
* Most of Load-Balancing with few error since we haven't handled the exception and errors

# TODO 

* Few Bug fixings
* groups 
* end-to-end encryption for images .

# Working and implementation of our code

* We have used the **threading** library for implementing **multiclient-multiserver** connections and used **Postgre-SQL** for 
database and RSA for **end-to-end** encryption we have used **round-robin load-balancing** 
* We have 3 files superserver.py, server.py and client.py. 
* superserver.py contains the code for load balancing server where all the servers are connected to 
* It has a database in which every message and image is stored, and used when needed.
* Superserver has two sockets - ClientSocket and SuperSockets into which server and clients connect. Clients connect to get the info on which server, it has to connect.
* Supersocket is socket to which servers connect. We store the connection objects and allocated different IDs.
* server.py is the file which has code for servers. It takes the port number as commandline argument.client.py
* It connects with Load balancing server and clients. It allows the clients to communicate. 
* Both server and clients have access to database and send messages to database first and then to their respective clients/servers .


# Links used

* [socket - programming](https://www.geeksforgeeks.org/python-program-that-sends-and-recieves-message-from-client/)
* [multiple connections](https://realpython.com/python-sockets/#handling-multiple-connections)
* [PostgreSQL](https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04)
* [PostgreSQL - examples](https://www.geeksforgeeks.org/python-postgresql-select-data/)
* [PostgreSQL - cheatsheet](https://www.postgresqltutorial.com/postgresql-cheat-sheet/)
* [keep track of clients](https://stackoverflow.com/questions/10605083/python-asyncore-keep-track-of-clients)
* [Images](https://stackoverflow.com/questions/42458475/sending-image-over-sockets-only-in-python-image-can-not-be-open)

