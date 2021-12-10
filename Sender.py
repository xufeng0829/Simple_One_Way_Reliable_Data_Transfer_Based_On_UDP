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
    args = input('tcpclient <file> <address of udpl> <port number of udpl> <window size> <ack port number>\n').split(
        " ")
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
    clientSocket.bind(('', source_port))
    port_udpl = int(args[3])
    address_udpl = args[2]

    """
    Settings of acks listening socket
    """
    ack_port_number = int(args[5])
    ACKSocket = socket.socket(AF_INET, SOCK_DGRAM)
    ACKSocket.setblocking(False)
    ACKSocket.bind(('', ack_port_number))
    # print(args)

    """
    Some status parameters initialization
    """
    timer_status = False  # timer status set false at first. false means timer is off, true means timer is on.
    timer_start = 0
    timeout_interval = 1  # default timeout is 1 second
    window_size = int(args[4])
    if window_size < MSS - HEADER_SIZE:
        print('window size should larger than 1000.')
        return
    send_base = 0
    next_seq_num = 0
    fin = '0'

    """
    RTT measurement parameters
    """
    RTT_measure = False  # this is the status to check if the timer is valid for RTT measurement.
    RTT_number = 0  # this is the number of corresponding ack to measure RTT
    estimate_RTT = 1
    dev_RTT = 0
    RTT_timer = time.time()  # timer for measuring sample RTT. Only one normally sending packet is measured while
                             # sending. Never measuring retransmitted packet.

    print('start sending %s to %s:%s, window size = %s bytes' %(args[1], args[2], args[3], args[4]))
    print('-'*50)

    while fin == '0':
        if next_seq_num - send_base < window_size:  # if there is still space in the sliding window
            if next_seq_num < file_size:  # if the file is not finished reading
                file_to_send.seek(next_seq_num)  # seek the correct position to read file.
                msg = bytes(file_to_send.read(MSS - HEADER_SIZE))
                if next_seq_num + MSS - HEADER_SIZE >= file_size:  # if this is the last message to read
                    pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, next_seq_num, 0, window_size, fin=1)
                    print('final packet, ', end='')
                else:
                    pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, next_seq_num, 0, window_size)
                print('sending ' + str(next_seq_num) + ' byte...')
                next_seq_num += len(pkt) - HEADER_SIZE
                clientSocket.sendto(pkt, (address_udpl, port_udpl))
                if timer_status == False:
                    timer_start = time.time()
                    timer_status = True
                if not RTT_measure:  # if there is no measure of RTT, a measurement is needed.
                    RTT_measure = True
                    RTT_number = next_seq_num
                    RTT_timer = time.time()
            else:
                pass

        if time.time() - timer_start >= timeout_interval and timer_status == True:
            next_seq_num = send_base
            file_to_send.seek(send_base)  # return to the place with smallest seq number, which is the base of window.
            msg = bytes(file_to_send.read(MSS - HEADER_SIZE))  # retransmit the smallest seqn packet.
            if send_base + MSS - HEADER_SIZE >= file_size:  # if this is the last message to read
                pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, send_base, 0, window_size, fin=1)
            else:
                pkt = TCPpacket.make_pkt(msg, source_port, port_udpl, send_base, 0, window_size)
            clientSocket.sendto(pkt, (address_udpl, port_udpl))
            print('timeout, ' + 'retransmitting ' + str(send_base) + ' byte...')
            timeout_interval = timeout_interval * 2
            print('timeout interval is %fms' % (timeout_interval * 1000))
            timer_start = time.time()  # reset the timer.
            RTT_measure = False  # never measure RTT with a retransmission

        try:
            rcv_pkt = ACKSocket.recv(2048)
        except BlockingIOError as e:
            pass
        else:
            ack_number_from_rcvr = unsigned_int.unpack(rcv_pkt[8:12])[0]
            fin = bin(unsigned_short.unpack(rcv_pkt[12:14])[0])[16]
            # print(fin)
            # print(ack_number_from_rcvr)
            if ack_number_from_rcvr > send_base:  # this means packets are received, and move the window towards.
                send_base = ack_number_from_rcvr
                if ack_number_from_rcvr == RTT_number and RTT_measure:
                    # calculate the timeout interval
                    sample_RTT = time.time() - RTT_timer
                    # print('sample RTT is %f with %d packet.' %(sample_RTT, RTT_number))
                    if estimate_RTT == 1:
                        estimate_RTT = sample_RTT
                    else:
                        estimate_RTT = 0.875 * estimate_RTT + 0.125 * sample_RTT
                    # print('estimate RTT is %f' % estimate_RTT)
                    dev_RTT = 0.75 * dev_RTT + 0.25 * abs(sample_RTT - estimate_RTT)
                    # print('Dev RTT is %f' % dev_RTT)
                    timeout_interval = estimate_RTT + 4 * dev_RTT
                    print('timeout interval is %fms' % (timeout_interval * 1000))
                    RTT_measure = False  # set RTT_measure to false.
                if send_base < next_seq_num:  # if current window still has unacked packets
                    timer_start = time.time()
                    RTT_measure = False
                else:  # move to next window, stop the timer.
                    # Timer will be restart after the first packet of next window is sent.
                    timer_status = False
                    RTT_measure = False
        # print('timeout interval %f' % timeout_interval)

    print('file transmission complete.')
    file_to_send.close()


if __name__ == '__main__':
    main()
