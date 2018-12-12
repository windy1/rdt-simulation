from udt import udt

sock = udt(0, 0, ('127.0.0.1', 12001))
    

print("Segment #, message")
while True:
    seg_num, ack, body, address = sock.udt_recv(2048)
    print(seg_num,", ",body)
