import struct

unsigned_short = struct.Struct('>H')  # unsigned short takes 2 bytes, 16 bits
unsigned_int = struct.Struct('>I')  # unsigned int takes 4 bytes, 32 bits,
MSS = 576
HEADER_SIZE = 20


def bitadd(a: int, b: int):
    """
    this is function to calculate bit addition when doing checksum.
    """
    c = a + b
    if c >= 2 ** 16:
        c = c - 2 ** 16 + 1
    # print(c)
    return c


def make_pkt(msg: bytes, source_port: int, dest_port: int, seqn: int, ackn: int, window: int, ack=0, fin=0):
    '''
        This is the function to add header to a piece of message.
        return a TCP datagram with correct header.
    '''

    ackn = unsigned_int.pack(ackn)
    window_size = unsigned_short.pack(window)
    if ack == 0 and fin == 0:  # 20 bytes head, so the head length should be 5.
        flags = unsigned_short.pack(int('0101000000000000', 2))
    elif ack == 1 and fin == 0:
        flags = unsigned_short.pack(int('0101000000100000', 2))
    elif ack == 0 and fin == 1:
        flags = unsigned_short.pack(int('0101000000000001', 2))
    elif ack == 1 and fin == 1:
        flags = unsigned_short.pack(int('0101000000100001', 2))
    # print(len(bin(unsigned_short.unpack(flags)[0])))
    urgent = unsigned_short.pack(0)
    '''
    calculate check sum.
    '''
    sum = 0
    sum = bitadd(sum, source_port)
    sum = bitadd(sum, dest_port)
    sum = bitadd(sum, seqn)
    sum = bitadd(sum, unsigned_short.unpack(ackn[0:2])[0])
    sum = bitadd(sum, unsigned_short.unpack(ackn[2:4])[0])
    sum = bitadd(sum, unsigned_short.unpack(flags)[0])
    sum = bitadd(sum, window)
    i = 0
    while i < len(msg):
        if i + 2 <= len(msg):
            byte_2 = msg[i:i + 2]
        else:
            byte_2 = msg[i:i + 1] + b' '
        # print('byte_2: ', end='')
        # print(unsigned_short.unpack(byte_2)[0])
        sum = bitadd(sum, unsigned_short.unpack(byte_2)[0])
        i = i + 2
    # reverse 0 1 in sum.
    sum = 2 ** 16 - 1 - sum
    # print('sum: ' + str(sum))
    checksum = unsigned_short.pack(sum)
    '''
    checksum calculation done.
    '''
    segment = unsigned_short.pack(source_port) + unsigned_short.pack(dest_port) \
            + unsigned_int.pack(seqn) \
            + ackn \
            + flags + window_size \
            + checksum + urgent \
            + msg
    return segment


def uncorrupted(segment):
    """
    check if the segment data is uncorrupted.
    """
    i = 0
    sum = 0
    while i < len(segment):
        if i + 2 <= len(segment):
            byte_2 = segment[i:i + 2]
        else:
            byte_2 = segment[i:i + 1] + b' '
        # print('byte_2: ', end='')
        # print(unsigned_short.unpack(byte_2)[0])
        sum = bitadd(sum, unsigned_short.unpack(byte_2)[0])
        i = i + 2
    # reverse 0 1 in sum.
    # print('sum: ' + str(sum))
    # print(sum)
    if sum == 2 ** 16 - 1:
        return True
    return False
