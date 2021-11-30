"""
There is a file to send
1. split file data into small pieces, and stored in a buffer.
2. add head for every pieces, and make them packages.
3. send data to receiver.
"""


MSS = 576
HEADER_SIZE = 20


class TCP_header:
    '''
    This is a class to create a datagram with a piece of data split from a file.
    '''
    def __init__(self, sp, dp, seqn, ackn, ws, cs):

        self.source_port = sp
        self.destination_port = dp
        self.seq_num = seqn
        self.ack_num = ackn
        self.window_size = ws
        self.check_sum = cs
        self.urgent_pointer = 0b00000000
