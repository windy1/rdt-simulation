from rdt import rdt

r = rdt(
    packet_loss=0,
    reorder=0,
    seg_size=16,
    wind=10,
    src_addr=("127.0.0.1", 12001),
    dest_addr=("127.0.0.1", 12000),
    server=True
)
print(r.recv_all())
