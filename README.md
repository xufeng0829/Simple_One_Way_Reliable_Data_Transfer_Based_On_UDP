# CSEE4119 Program Assignment 2
# A Simplex TCP 
&emsp;
Feng Xu (fx2174)
12/10/2021
&emsp;
## Files and Descriptions

- **`TCPpacket.py`**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TCPpacket contains functions of adding headers to a chunk of data, calculate checksum of a packet, and check if a packet is corrupted.

- **`Sender.py`**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sender is the client in this project, it can read a text file and build packets, send packets through a silde window (with size given by user) to server, measure dynamic timeout interval, listen to ack sent from receiver and close automatically when transmission complete or connection is highly possible lost.

- **`Receiver.py`**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Receiver is the server in this project. It can receive data from sender, decode the packet and write data in to the file with a path given by user. Plus, receiver can check if packet is corrupted, out of order or redundant. Receiver also has a buffer window to store out-of-order packet. Receiver can send proper ack to the sender, and close automatically when transmission is complete. However, Receiver can not shut down itself when connection is lost.



## Commands Needed for Running 

- **Sender**
```sh
python3 Sender.py
# There should be a printed guidance for input:
# TCP client running...
# tcpclient <file> <address of udpl> <port number of udpl> <window size> <ack port number>
# Here is a sample input:
tcpclient test.txt localhost 41192 2000 15000
```
- **Receiver**
```sh
python3 Receiver.py
# There should be a printed guidance for input:
# TCP server running...
# tcpserver <file> <listening port> <address for acks> <port for acks>
# Here is a sample input:
tcpserver receive.txt 14000 localhost 15000
```

## FEATURES ( important! )

**Here are some features needed to know before running the programs, otherwise may cause bugs.**
&emsp;
***Test enviroment: python 3.5, Ubuntu 16.04.7 LTS***
> Port number of sender's socket for sending data is binded with 12000

> Port number of receiver's socket for sending ack is binded with 16000

> <ack port number> and <port for acks> should be same value, e.g. 15000

- Keep avoid these these port number when running udp emulator and assigning port number for acks.
- It may be better to run receiver first to avoid meaningless increment of timeout interval.
- Window size should be larger than 576, while it is okay to use a number smaller than that.

No severe bug detected. However, I only test programs on localhost, which means sender, receiver and udp emulator all run on same machine.


