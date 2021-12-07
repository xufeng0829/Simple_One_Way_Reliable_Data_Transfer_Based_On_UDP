"""
This is the receiver in this project.
receiver has the following interface:
    python Receiver.py
"""

from socket import *
import socket
import sys
import struct
import os
import TCPpacket


unsigned_short = struct.Struct('>H')  # unsigned short takes 2 bytes, 16 bits
unsigned_int = struct.Struct('>I')  # unsigned int takes 4 bytes, 32 bits,
MSS = 576
HEADER_SIZE = 20


def main():
    print('TCP client running...')
    args = input().split(" ")
    if len(args) != 5:
        print('illegal input! input should look like: \n '
              'tcpserver <file> <listening port> <address for acks> <port for acks>')
        return

    '''
    get all input information, and check validation.
    '''
    filepath = args[1]
    file = open(filepath, 'wb')  # use byte write mode.
    listening_port = int(args[2])
    address_for_acks = args[3]
    port_for_acks = int(args[4])

    receiver_socket = socket.socket(AF_INET, SOCK_DGRAM)
    ACKSocket = socket.socket(AF_INET, SOCK_DGRAM)

    expect_ack = 0
    while True:
        segment = receiver_socket.recv(2048)
        if TCPpacket.uncorrupted(segment):
            if unsigned_int.unpack(segment[4:8]) == expect_ack:
                 # TODO: update cumulative ack, and send ack packet
                expect_ack = unsigned_int.unpack(segment[8:12])
            else:
                # TODO: send ack packet
                pass
        else:
            # TODO: send ack packet
            pass
        pass

    print(args)


if __name__ == '__main__':
    pass
