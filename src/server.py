##################################################################################
# Program Name: server.py
# Program purpose: UDP server with connection establishment and probability "p"
# of losing packets
##################################################################################

from timer import Timer
from random import randrange
import time, socket, threading, sys, random, errno
from collections import deque

# This function does connection establishment between client and server via 3-way-handshake
def connection_establishment():
    dataFrame = "00020001"
    bytesToSend = str.encode(dataFrame)
    while(True):
        message, address = s.recvfrom(bufflen) #returns an array [message, address]
        print("Received CR(req={}, ack={}) from client at IP address {}".format(message[:4], message[4:], address))
        if(message == b"00010000"):
            s.sendto(bytesToSend, address)
            print("Sending Ack(req={}, ack={}) to client".format(dataFrame[:4], dataFrame[4:]))
        elif(message == b"00000002"):
            print("Connection established successfully!!! \n")
            time.sleep(2)
            break

bufflen = 1024
PORT = 55000

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
    print("Could not create socket on client side.")
    sys.exit(1)

#Bind to address and ip
try:
    s.bind(('', PORT))
    print("UDP Server is connected!")
except:
    print("Cannot bind to port {}".format(PORT))
    sys.exit(1)

#call connection establishment on server side
connection_establishment()

#Receive messages
while(True):
    try:
        msg, addr = s.recvfrom(bufflen)
        f = open("./output.txt","a+")
        f.write("{}\n".format(msg.decode('utf-8')[:8]))
        f.close()
        print("Received data from client: {}".format(msg))
    except:
        print("could not receive message from client")
    if(msg and addr):
        probability = randrange(10)
        # 7/10 = 70% chance of sending ack to client
        # 3/10 = 30% chance of dropping packets
        if (probability <= 6 and probability >= 0):
            send_back = msg[12:16] + msg[8:12]
            try:
                s.sendto(send_back, addr)
                print("sending ack to client: {} \n".format(send_back))
            except:
                print("could not send back message to client")
        else:
            print("Oops, Server dropped packet! \n")
            msg = None
            addr = None
        #sleep 2 second to prevent rapid sending of packages
        time.sleep(2)