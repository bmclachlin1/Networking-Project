#############################################################################
# Authors: Blake McLachlin, Kevin Baffo, Soloman Fayemi, Mahfooz Azeez
# Last Date Revised: December 3rd, 2019
# Program Name: client.py
# Program purpose: UDP client with connection establishment and timeout for
# sending packets. Has 2 threads running. 1 thread is for sending and 1 
# thread is for receiving.
#############################################################################

from timer import Timer
import time, socket, threading, sys, errno
from collections import deque

# This function does connection establishment between client and server via 3-way-handshake
def connection_establishment():
    #PACKET [ left 4 digits for req & right 4 digits for ack ]
    dataFrame = "00010000"
    dataFrame2 = "00000002"
    bytesToSend = str.encode(dataFrame)
    bytesToSend2 = str.encode(dataFrame2)

    try:
        s.sendto(bytesToSend, (sys.argv[1], PORT))
        print("Sending CR(req={}, ack={}) to server".format(dataFrame[:4], dataFrame[4:]))
    except OSError as err:
        print("Cannot send: {} to server".format(err.strerror))

    while(True):
        try:
            message, address = s.recvfrom(bufflen) #returns an pair of values (message, address)
            print("Received ack(req={}, ack={}) from server at IP address {}".format(message[:4], message[4:], address))
            s.sendto(bytesToSend2, (sys.argv[1], PORT))
            print("Sending CR(req={}, ack={}) to server".format(dataFrame2[:4], dataFrame2[4:]))
            print("Connection established successfully!!! \n")
            time.sleep(2)
            break
        except:
            print("Cannot receive message from server. Trying again...")

# This function makes the packets to be sent for the program.
# Returns array of byte encoded packets to be sent.
# Packets are sent where the first 8 bits are the packet data,
# the next 4 bits are the seq# for request, and the next 4 bits
# are the seq# for acknowledgment
def make_packets():
    # Open the file
    filename = "test.txt"
    try:
      file = open(filename, 'r')
    except IOError:
      print('Unable to open')

    packets = []
    # While data in file, read data from file, 8 characters at a time
    while True:
        data = file.read(8)
        if not data:
            break
        packets.append(data)

    encoded_array = deque([])
    start_req_number = 3

    # encode packets and add sequence number for req and ack 
    for p in packets:
        encoded_file = str.encode(p)
        to_insert = "{}0000".format(start_req_number)
        if(len(to_insert) < 8):
            offset = 8 - len(to_insert)
            for i in range(offset):
                to_insert = "0" + to_insert
        to_insert = str.encode(to_insert)
        encoded_file = encoded_file + to_insert
        encoded_array.append(encoded_file)
        start_req_number += 1

    file.close()

    return encoded_array

#function for sending data.
def sender():
    global timer
    global next_flag
    global waiting_for
    timer = Timer(5)
    timer.start()
    print("Sender thread started \n")
    while(True):
        if(next_flag == True):
            # queue first packet to send
            try:
                dataFrame = packets.popleft()
            except:
                print("No more packets left to send... exiting program...")
                sys.exit(1)
            # Keep track of acknowledgment you're waiting for
            # we are waiting for the req we just sent, but as an acknowledgment
            waiting_for = dataFrame[12:16] + dataFrame[8:12]

            #try sending data to server
            try:
                s.sendto(dataFrame, (sys.argv[1], PORT))
                print("sending {} to server".format(dataFrame))
            except:
                print("could not send {} to server".format(dataFrame))
            # Set next_flag to false. We don't want to send again until receiving thread
            # sets next_flag back to True once it receives an acknowledgment
            next_flag = False

        if(timer.timeout()):
            # restart the timer
            print("Didn't receive acknowledgment after 5 seconds. Restarting timer for 5 seconds \n")
            timer.stop()
            timer.start()
            # Send again, as we didn't receive an acknowledgment
            try:
                s.sendto(dataFrame, (sys.argv[1], PORT))
                print("sending {} to server".format(dataFrame))
            except:
                print("could not send {} to server".format(dataFrame))



# function for receiving data
def receiver():
    global timer
    global next_flag
    global waiting_for
    print("Receiver thread started")
    while(True):
        try:
            msg, addr = s.recvfrom(bufflen)
            if (msg == waiting_for):
                print("Received ack from server: {} \n".format(msg))
                #once we receive an acknowledgment, we notify the sender
                # by setting next_flag to True
                next_flag = True
                # we also need to cancel and restart the timer in sender thread
                timer.stop()
                timer.start()
            else:
                print("Wrong acknowledgment received")
        except:
            print("Could not receive from server")

bufflen = 1024
PORT = 55000

# try creating socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
    print("Could not open socket on client side.")
    sys.exit(1)

# call connection establishment on client side
connection_establishment()

# Make packets to send
packets = make_packets()

# True if sender can send
# False if still waiting for acknowledgment, sender can't send
next_flag = True

try:
    # make receiving thread
    receiver_thread = threading.Thread(target=receiver, args=())
    # start the receiving thread
    receiver_thread.start()
    # make sender_thread
    # daemon thread means it will stop execution once receiver_thread stops execution
    sender_thread = threading.Thread(target=sender, args=(), daemon=True)
    # start the sender thread
    sender_thread.start()
except:
    print("Error starting threads")
