# TCP Sniffer

The **TCP sniffer** listens to the data sending between client and server. 
It sniffs the connection and saves it's content into a SQLite3 database.

It is basically used as a third party relay party, not too different from socat, if socat were to save
your communications to SQLite, so it can be used everywhere that you have the freedom to configure the 
ports that you'll connect to.

The **test-server.py** and the **test-client.py** are for the testing purpose. The communication between the **server** and the **client** is duplex (they receive and send messages). 

How to use?
===========

Call the following:
```bash
python -m sniffer 8000 127.0.0.1 8080
```

This will fire up a local sniffer to sniff at port 8000, while handling off the connection to 127.0.0.1 port 8080.
