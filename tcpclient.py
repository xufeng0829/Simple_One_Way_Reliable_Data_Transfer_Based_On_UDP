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

serverName = socket.gethostname()
serverPort = 13000
clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
unsigned_short = struct.Struct('>H')  # unsigned short takes 2 bytes, 16 bits
unsigned_int = struct.Struct('>I')  # unsigned int takes 4 bytes, 32 bits,
MSS = 576
HEADER_SIZE = 20


def make_pkt_buffer(args) -> list:
    '''

    :param args: user's input of information needed for building buffer of datagrams
    :return: a buffer of datagrams which is built with specific files and header.
    '''
    filepath = args[1]
    addr_udpl = args[2]
    port_udpl = args[3]
    window_size = args[4]
    port_ack = args[5]
    data_buffer = []
    file = open(filepath, 'rb')
    size_cnt = 1
    file_size = os.path.getsize(filepath)
    while size_cnt <= file_size:
        data_buffer.append(bytearray(file.read(MSS - HEADER_SIZE)))
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
    pkt_buffer = make_pkt_buffer(args)
    print(args)


if __name__ == '__main__':
    print(make_pkt_buffer(['a', 'test.txt', 'a', 'a','a','a']))
