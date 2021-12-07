"""
TCP Client is our sender in this project.
client has the following interface:
    python Sender.py
"""

from socket import *
import socket
import sys
import struct
import os
import TCPpacket
import time

unsigned_short = struct.Struct('>H')  # unsigned short takes 2 bytes, 16 bits
unsigned_int = struct.Struct('>I')  # unsigned int takes 4 bytes, 32 bits,
MSS = 576
HEADER_SIZE = 20
CLIENT_SOURCE_PORT = unsigned_short.pack(12000)  # set client source port as 12000


def main():
    print('TCP client running...')
    args = input().split(" ")
    if len(args) != 6:
        print('illegal input! input should look like: \n '
              'tcpclient <file> <address of udpl> <port number of udpl> <window size> <ack port number>')
        return

    """
    Settings of the file to send
    """
    filepath = args[1]
    if not os.path.exists(filepath):  # check if file exists
        print('Cannot open file: ' + args[1])
        print('Check file path!')
        return
    file_to_send = open(filepath, 'rb')
    file_size = os.path.getsize(filepath)

    """
    Settings of the socket to send data
    """
    clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
    source_port = 12000  # this is set as default and cannot change, should be mentioned in readme file.
    clientSocket.bind('', source_port)
    port_udpl = unsigned_short.pack(int(args[3]))
    address_udpl = args[2]
    """
    Settings of acks listening socket
    """
    ack_port_number = int(args[5])
    ACKSocket = socket.socket(AF_INET, SOCK_DGRAM)
    ACKSocket.setblocking(False)
    ACKSocket.bind('', ack_port_number)
    print(args)

    """
    Some status parameters initialization
    """
    timer_status = False  # timer status set false at first. false means timer is off, true means timer is on.
    timer_start = 0
    timeout_value = 2  # default timeout is 2 seconds
    window_size = int(args[4])
    send_base = 0
    next_seq_num = 0

    while True:
        if next_seq_num - send_base < window_size:  # if there is still space in the sliding window
            if next_seq_num < file_size:  # if the file is not finished reading
                msg = bytes(file_to_send.read(MSS - HEADER_SIZE))
                if next_seq_num + MSS - HEADER_SIZE >= file_size:  # if this is the last message to read
                    pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, next_seq_num, window_size, fin=1)
                else:
                    pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, next_seq_num, window_size)
                next_seq_num += len(pkt - HEADER_SIZE)
                clientSocket.sendto(pkt, (address_udpl, port_udpl))
                if timer_status == False:
                    timer_start = time.time()
                    timer_status = True
            else:
                pass

        if time.time() - timer_start >= timeout_value:
            file_to_send.seek(send_base)  # return to the place with smallest seq number, which is the base of window.
            timer_start = time.time()  # reset the timer.

        try:
            rcv_pkt = ACKSocket.recv(2048)
            ack_number_from_rcvr = unsigned_int.unpack(rcv_pkt[8:12])[0]
            if ack_number_from_rcvr > send_base:  # this means some acks are lost, and move the window towards.
                send_base = ack_number_from_rcvr
                if send_base < next_seq_num:
                    timer_start = time.time()
        except BlockingIOError as e:
            pass


if __name__ == '__main__':
    # main()
    i = 12345
    i1 = unsigned_int.pack(i)
    print(unsigned_int.unpack(i1))

