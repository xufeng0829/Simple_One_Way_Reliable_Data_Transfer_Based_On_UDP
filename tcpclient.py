"""
TCP Client is our sender in this project.
client has the following interface:
    python tcpclient.py <file> <address of udpl> <port number of udpl> <window size> <ack port number>
"""

from socket import *
import socket
import sys
import struct
import os


unsigned_short = struct.Struct('>H')  # unsigned short takes 2 bytes, 16 bits
unsigned_int = struct.Struct('>I')  # unsigned int takes 4 bytes, 32 bits,
MSS = 576
HEADER_SIZE = 20
CLIENT_SOURCE_PORT = unsigned_short.pack(12000)  # set client source port as 12000


def make_pkt_buffer(args) -> list:
    '''

    :param args: user's input of information needed for building buffer of datagrams
    :return: a buffer of datagrams which is built with specific files and header.
    '''
    filepath = args[1]
    data_buffer = []
    file = open(filepath, 'rb')
    size_cnt = 1
    file_size = os.path.getsize(filepath)
    while size_cnt <= file_size:
        data_buffer.append(bytes(file.read(MSS - HEADER_SIZE)))
        size_cnt += MSS - HEADER_SIZE
    file.close()
    return data_buffer


def main():
    print('TCP client running...')
    args = input().split(" ")
    if len(args) != 6:
        print('illegal input! input should look like: \n '
              'tcpclient <file> <address of udpl> <port number of udpl> <window size> <ack port number>')
        return

    '''
    get all input information, and check validation.
    '''
    filepath = args[1]
    if not os.path.exists(filepath):  # check if file exists
        print('Cannot open file: ' + args[1])
        print('Check file path!')
        return
    port_udpl = unsigned_short.pack(args[3])
    port_address = args[2]
    pkt_buffer = make_pkt_buffer(args)

    clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
    ACKSocket = socket.socket(AF_INET, SOCK_DGRAM)

    print(args)


def add_header(segment, dest_port, seqn, window, ack=0, fin=0):
    source_port = CLIENT_SOURCE_PORT
    ackn = unsigned_int.pack(seqn + MSS - HEADER_SIZE)
    winsize = unsigned_short.pack(window)
    if ack==0 and fin==0:  # 20bytes head, so the head length should be 5.
        flags = unsigned_short.pack(int('0101000000000000', 2))
    elif ack==1 and fin==0:
        flags = unsigned_short.pack(int('0101000000100000', 2))
    elif ack==0 and fin==1:
        flags = unsigned_short.pack(int('0101000000000001', 2))
    elif ack==1 and fin==1:
        flags = unsigned_short.pack(int('0101000000100001', 2))
    urgent = unsigned_short.pack(0)
    checksum = unsigned_short.pack(0)
    segment =   source_port + dest_port\
              + unsigned_int.pack(seqn) \
              + ackn \
              + flags + winsize\
              + checksum + urgent\
              + segment
    return segment


if __name__ == '__main__':
    a = unsigned_short.pack(20480)
    b = unsigned_short.pack(0)
    c = unsigned_short.pack(int('0101000000000000', 2))
    print(bin(a[0]), bin(a[1]))
    print(a)
    print(unsigned_short.unpack(c))
