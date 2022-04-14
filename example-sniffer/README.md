# Example Sniffer

An example of a TCP client/server socket created using Python's socket and threading library. 

The **sniffer** uses instances of a ChatServer class and individual threads to listen to incoming data from each client. 
It sniffs the connection and saves it's content into a SQLite3 database.

The **calypso_server** echoes whatever it receives from the **facs_client**. Only for the testing purpose.
