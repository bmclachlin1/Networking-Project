# Networking-Project

In this project, I developed client and server programs that implement the alternating bit protocol. The following list of things are supported.

1) Connection Establishment
2) Data transfer using alternating bit protocol
3) Error recovery
4) Writing message to an output file

The program sends encoded text eight characters at a time along with a sequence number representing request or acknowledgment. 

Instructions for running the Program: Always start the server program before starting the client program or the connection request will not work! You must have python3 installed on your computer! IP_ADDRESS_HERE is where you should put the server's IP address you are trying to connect to!

Terminal 1
python3 client.py IP_ADDRESS_HERE

Terminal 2
python3 server.py
