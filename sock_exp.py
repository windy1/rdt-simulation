import socket
import random


class sock_265(socket.socket):

    def __init__(self, packet_loss=0, reorder=0, family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=0, fileno=None):
        """
        packet_loss: probability a packet is dropped [0-1]
        bit_errs: probability of some bit erros in a packet [0-1]
        reorder: probability a packet gets swapped with the next packet [0-1]
        
        """
        super().__init__(family=family, type=type, proto=proto, fileno=fileno)
        self.p_loss = packet_loss
        self.reorder = reorder
        self.rqueue = []
        self.count = 0

    def sendto(self, message, address):
        """
        send a message to a port

        message: the message you want to send
        address: (dest IP, dest port)
        """
        if random.random() < self.p_loss:
            return

        if len(self.rqueue) >=0  and .2*self.count > random.random():
            random.shuffle(self.rqueue)
            for m in self.rqueue:
                super().sendto(m, address)
            self.rqueue = []
            self.count = 0

        self.count += 1

        if self.reorder > random.random():
            self.rqueue.append(message)
        else:
            super().sendto(message, address)


            
