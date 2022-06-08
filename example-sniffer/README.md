# Example Sniffer

An example of a TCP client-server socket created using Python's socket and threading library. 

The **sniffer** uses instances of a ChatServer class and individual threads to listen to incoming data. 
It sniffs the connection and saves it's content into a SQLite3 database.

The **test/server.py** and the **test/client.py** are for the testing purpose. The communication between the **server** and the **client** is duplex (they receive and send messages). 

How to use?
===========

Call the following:
```bash
python -m sniffer 8000 127.0.0.1 8080
```
