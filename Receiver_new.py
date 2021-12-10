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
    print('TCP server running...')
    args = input('tcpserver <file> <listening port> <address for acks> <port for acks>\n').split(" ")
    if len(args) != 5:
        print('illegal input! input should look like: \n '
              'tcpserver <file> <listening port> <address for acks> <port for acks>')
        return

    '''
    get all input information, and check validation.
    '''
    filepath = args[1]
    file_to_receive = open(filepath, 'wb')  # use byte write mode.
    listening_port = int(args[2])
    address_for_acks = args[3]
    port_for_acks = int(args[4])

    '''
    Settings of socket receiving data
    '''
    receiver_socket = socket.socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', listening_port))  # the receiving socket port is hardcode as 14000
    '''
    Settings of socket sending acks to the sender.
    '''
    ACKSocket = socket.socket(AF_INET, SOCK_DGRAM)
    source_port = 16000
    ACKSocket.bind(('', source_port))  # the ack sending socket port is hardcode as 16000
    '''
    Settings of receiver window.
    '''
    rcvr_buffer = {}
    buffer_base = 0

    print('receiving file from %s, write into %s.' %(args[3], args[1]))
    print('-'*50)

    expect_ack = 0
    while True:
        segment = receiver_socket.recv(2048)
        window_size = unsigned_short.unpack(segment[14:16])[0]
        buffer_size = window_size
        if TCPpacket.uncorrupted(segment):
            if unsigned_int.unpack(segment[4:8])[0] == expect_ack:  # sequence number is equal to the expect ack.
                # update cumulative ack, and send ack packet
                # expect_ack = expect_ack + len(segment) - HEADER_SIZE
                print('RECEIVED:     packet start at %s byte correctly.' % unsigned_int.unpack(segment[4:8])[0])
                window_size = unsigned_short.unpack(segment[14:16])[0]
                # fin = unsigned_short.unpack(segment[12:14])[0]
                # file_to_receive.write(segment[20:len(segment)])  # write down the content of that pkt to the file.
                rcvr_buffer[unsigned_int.unpack(segment[4:8])[0]] = segment
                # check if we can also write down something in the buffer.
                while bool(rcvr_buffer):
                    try:
                        data = rcvr_buffer.pop(buffer_base)
                    except:
                        break
                    else:
                        print('WRITE:        data start at %s byte.' % unsigned_int.unpack(data[4:8])[0])
                        file_to_receive.write(data[20:len(data)])
                        fin = unsigned_short.unpack(data[12:14])[0]
                        # print(bin(fin))
                        buffer_base = unsigned_int.unpack(data[4:8])[0] + len(data) - HEADER_SIZE
                        expect_ack = unsigned_int.unpack(data[4:8])[0] + len(data) - HEADER_SIZE
                if bin(fin)[16] == '1':  # bin() returns a '0b' at first.
                    ack_pkt = TCPpacket.make_pkt(b'', source_port, port_for_acks, 1, expect_ack, window_size, ack=1, fin=1)
                    ACKSocket.sendto(ack_pkt, (address_for_acks, port_for_acks))
                    print('RECEIVED:     final packet')
                    file_to_receive.close()
                    break
                else:
                    ack_pkt = TCPpacket.make_pkt(b'', source_port, port_for_acks, 1, expect_ack, window_size, ack=1)
                    ACKSocket.sendto(ack_pkt, (address_for_acks, port_for_acks))

            elif unsigned_int.unpack(segment[4:8])[0] < expect_ack:  # some former pkt is received
                print('REDUNDANT:    packet start at %s byte' % str(unsigned_int.unpack(segment[4:8])[0]))
                ack_pkt = TCPpacket.make_pkt(b'', source_port, port_for_acks, 1, expect_ack, window_size, ack=1)
                ACKSocket.sendto(ack_pkt, (address_for_acks, port_for_acks))

            else:
                print('OUT OF ORDER: packet start at %s byte' % str(unsigned_int.unpack(segment[4:8])[0]))
                ack_pkt = TCPpacket.make_pkt(b'', source_port, port_for_acks, 1, expect_ack, window_size, ack=1)
                ACKSocket.sendto(ack_pkt, (address_for_acks, port_for_acks))
                # check if there is space to buffer the pkt
                if unsigned_int.unpack(segment[4:8])[0] - buffer_base < buffer_size:
                    if unsigned_int.unpack(segment[4:8])[0] not in rcvr_buffer:
                        print('BUFFERED:     packet start at %s byte' % str(unsigned_int.unpack(segment[4:8])[0]))
                        rcvr_buffer[unsigned_int.unpack(segment[4:8])[0]] = segment
                    else:
                        print('DROPPED:      packet start at %s byte(already in buffer)'
                              % str(unsigned_int.unpack(segment[4:8])[0]))
                else:
                    print('DROPPED:      packet start at %s byte(out of buffer size)'
                          % str(unsigned_int.unpack(segment[4:8])[0]))

        else:  # the pkt is corrupted.
            print('CORRUPTED:    packet start at %s byte' % str(expect_ack))
            ack_pkt = TCPpacket.make_pkt(b'', source_port, port_for_acks, 1, expect_ack, window_size, ack=1)
            ACKSocket.sendto(ack_pkt, (address_for_acks, port_for_acks))
    print('-' * 50)
    print('file received successfully.')
    file_to_receive.close()


if __name__ == '__main__':
    main()
