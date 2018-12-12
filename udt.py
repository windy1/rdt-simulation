from sock_exp import sock_265


class udt:

    def __init__(self, packet_loss=0, reorder=0, bind_args=None, timeout=None):
        """
        packet_loss : probability of a packet being lost. 0 ≤ pl ≤ 1
        reorder     : probability of packets being reordered. 0 ≤ r ≤ 1
        bind_args   : the tuple (self IP, self port)
        """
        self.sock = sock_265(packet_loss, reorder)
        if timeout != None:
            self.sock.settimeout(timeout)
        self.bind_args = bind_args
        if bind_args:
            self.sock.bind(bind_args)

    def udt_send(self, seg_num, ack_num, body, address):
        """
        seg_num : segment number (int)
        ack_num : num of segment being acked (int) if not an ack, use -1 as a placeholder
        body    : message being sent (String)
        address : tuple (dest IP, dest port)
        """
        message = str(seg_num) + "⧺" + str(ack_num) + "⧺" + body
        self.sock.sendto(message.encode(), address)
        
    def udt_recv(self, buff):
        """
        buff : size of buffer in bits. Likes powers of 2, (int)

        RETURN:
        seg_num , ack_num, body
        """
        if not self.bind_args:
            raise Exception("Socket cannot receive without bind_args")
        message , address = self.sock.recvfrom(buff)
        ml = message.decode().split("⧺")
        return int(ml[0]), int(ml[1]), ml[2], address
