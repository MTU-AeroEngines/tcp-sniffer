# tcp-sniffer
A TCP sniffer that sniffs that relays the connection further and stores it's contents into a SQLite3 database


How to use?
===========

Just call the following:
```bash
python -m sniffer 8000 10.3.4.5 8080
```

This will fire up a local sniffer to sniff at port 8000, while handling off the connection to 10.3.4.5 port 8080.
