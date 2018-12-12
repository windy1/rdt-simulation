"""
CS 265 programming assignment 2.

Name: Walker J. Crouse
Date: December 2018

In this assigment, you will implement a reliable data transfer protocol over an unreliable channel. Your solution should
protect against packet loss and packet reorder. Corruption protection is not required. The protocol you implement should
be pipelined and work many different window sizes.

implementing the constructor, send_all, and recv_all functions of this file using the unreliable channel supported by
udt.py. An example of how to use the udt.py functions, run receiver.py, then simultaneously run sender.py.

All the code necessary for submission should be included in this file, and this should be the only file you submit.
Please do not change the name of the file, but add your name and date in the lines above.

You do not need to support full duplex communication with this assignment. It will be tested with a sender and receiver
process that transmit a message from one to the other. Both the sender and the receiver will use this module.
"""
import time
import socket
from threading import Thread

from udt import udt


class rdt:

    handshake_code = -0xDEADBEEF

    def __init__(self, packet_loss=0, reorder=0, seg_size=16, wind=10, src_addr=None, dest_addr=None, server=False,
                 timeout=1, buffer_size=1024):
        """
        Initialize the reliable data connection in this function. Suggested udt functions: __init__, udt_send, udt_recv.
        
        INARGS:
        packet_loss : probability of a packet being lost. 0 ≤ pl ≤ 1
        reorder     : probability of packets being reordered. 0 ≤ r ≤ 1
        seg_size    : max body size of a segment in chars. We will test your code on a segment size of 16
        wind        : window size. 
        src_addr    : the tuple (self IP, self port) that identifies this socket
        dest_addr   : the tuple (IP, port) that identifies the receiving socket
        server      : true if the process will not begin the handshake (should already be on)

        RETURN:
        nothing - this is a void function
        """
        self.buffer_size = buffer_size
        self.wind = wind
        self.packet_loss = packet_loss
        self.reorder = reorder
        self.dest_addr = dest_addr
        self.src_addr = src_addr
        self.timeout = timeout
        self.seg_size = seg_size
        self.is_server = server
        self.base_seg = 0
        self.seg_num = -1
        self.segments = None
        if self.is_server:
            self.bound_sock = udt(bind_args=self.src_addr)
            self.last_ack_out = -1
        else:
            self.dest_sock = udt(self.packet_loss, self.reorder, self.src_addr, self.timeout)
            self.base_send_time = None

    ###########################################################################
    #                                                                         #
    #                               == Client ==                              #
    #                                                                         #
    ###########################################################################

    def send_all(self, string):
        """
        Given a large string (think hundreds or thousands of bytes) segment it into segments of seg_size, and reliably
        send them. This function should account for both packet loss and reorder. Suggested udt functions: udt_send,
        udt_recv

        INARGS:
        s : large string to be sent to a receiver

        RETURN:
        nothing - this is a void function
        """
        print('[client] sending string of size %d' % len(string))
        # perform handshake
        if not self._client_handshake(len(string)):
            return

        # begin listening for server acks
        ack_thread = Thread(target=self._ack_listener)
        ack_thread.start()

        # begin sending segments
        self.segments = list(self._segment_string(string))
        while self.base_seg < len(self.segments):
            self._rewind(self.base_seg)

        print('[client] all segments sent')

        ack_thread.join()

    def _client_handshake(self, size):
        print('[client] sending handshake')
        try:
            self.dest_sock.udt_send(self.handshake_code, -1, 'size=%d' % size, self.dest_addr)
            seg_num, ack, body, addr = self.dest_sock.udt_recv(self.buffer_size)
        except socket.timeout:
            print('[client] ** handshake timed out **')
            return False
        if ack != self.handshake_code:
            print('[client] ** received invalid handshake code %d **' % ack)
            return False
        return True

    def _ack_listener(self):
        timeouts = 0
        while self.base_seg < len(self.segments):
            try:
                self._recv_server_ack()
                timeouts = 0
            except socket.timeout:
                timeouts += 1
                print('[client] ** timed-out waiting for ack (#%d) **' % timeouts)

    def _recv_server_ack(self):
        # retrieve an incoming ack from the server
        seg_num, ack, body, addr = self.dest_sock.udt_recv(self.buffer_size)
        self.base_seg = ack + 1
        if self.base_seg == self.seg_num:
            self.base_send_time = None
        else:
            self.base_send_time = time.time()
        print('[client] received ack #%d' % ack)

    def _rewind(self, seg_num):
        print('[client] rewind => seg #%d' % seg_num)
        self.seg_num = seg_num
        while self.seg_num < len(self.segments):
            if self._can_send_seg(self.seg_num):
                self.seg_num = self._send_seg(self.segments, self.seg_num)
            if self._has_timed_out():
                self.seg_num = self._timeout()

    def _can_send_seg(self, seg_num):
        return seg_num < self.base_seg + self.wind

    def _send_seg(self, segments, seg_num, retry=0):
        # the segment is within the window and ready to be sent
        seg = segments[seg_num]
        print('[client] seg #%d => %s:%d (size = %d)'
              % (seg_num, self.dest_addr[0], self.dest_addr[1], len(seg)))
        try:
            self.dest_sock.udt_send(seg_num, -1, seg, self.dest_addr)
        except socket.timeout:
            print('[client] send of seg #%d timed-out (retry #%d)' % retry)
            return self._send_seg(segments, seg_num, retry + 1)
        # reset the timer if a "base" segment was just sent
        if seg_num == self.base_seg:
            self.base_send_time = time.time()
        return seg_num + 1

    def _has_timed_out(self):
        return self.base_send_time is not None and time.time() - self.base_send_time > self.timeout

    def _timeout(self):
        print('[client] base seg #%d has timed out' % self.base_seg)
        self.base_send_time = time.time()
        return self.base_seg

    ###########################################################################
    #                                                                         #
    #                               == Server ==                              #
    #                                                                         #
    ###########################################################################

    def recv_all(self):
        """
        Receives a large string from a sender that calls s. When called, this function should wait until it receives all
        of s in order, then return all of s.
        Suggested udt functions: udt_recv, udt_send. 

        INARGS:
        none

        RETURN:
        s : the large string received from a sender
        """
        size = self._server_handshake()
        if size is None:
            return None

        string = ''
        while len(string) < size:
            string += self._recv_client_seg()
        return string

    def _server_handshake(self):
        # receive the incoming handshake
        seg_num, ack, body, addr = self.bound_sock.udt_recv(self.buffer_size)
        if seg_num != self.handshake_code:
            print('[server] ** received invalid handshake code %d **' % seg_num)
            return None

        # parse the body of the message
        header = body.split('=')
        if len(header) != 2:
            print('[server] ** received invalid header **')
            return None
        try:
            size = int(header[1])
        except ValueError:
            print('[server] ** invalid size parameter in header **')
            return None

        # acknowledge the handshake
        try:
            udt().udt_send(-1, self.handshake_code, '', addr)
        except socket.timeout:
            print('[server] ** handshake ack timed-out **')
            return None

        return size

    def _recv_client_seg(self):
        # retrieve segment from the client
        seg_num, ack, body, addr = self.bound_sock.udt_recv(self.buffer_size)
        ack_out = seg_num

        # check the validity of the segment
        if ack_out != self.last_ack_out + 1:
            print('[server] ** received out-of-order segment %d **' % seg_num)
            ack_out = self.last_ack_out
            result = ''
        else:
            result = body

        # send back ack
        print('[server] received seg #%d, sending ack #%d' % (seg_num, ack_out))

        try:
            udt().udt_send(-1, ack_out, '', addr)
        except socket.timeout:
            print('[server] ack #%d timed-out' % ack_out)
            # just allow the ack to be lost...

        self.last_ack_out = ack_out

        return result

    def _segment_string(self, string):
        for i in range(0, len(string), self.seg_size):
            yield string[i:i + self.seg_size]
