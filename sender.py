from udt import udt

# Reliable data sending
destination = ("127.0.0.1", 12001)
sock = udt(0, 0)
sock.udt_send(-1, 0, "No loss or reorder:\n", destination)
for i in range(10):
    sock.udt_send(i, 1, str(i), destination)

sock.udt_send(-1, 0, "50% loss, no reorder:\n", destination)

sock = udt(.5, 0)
for i in range(10):
    sock.udt_send(i, 1, str(i), destination)

sock = udt(0, 0)
sock.udt_send(-1, 0, "No loss, 50% reorder, note that there is some loss:\n", destination)

sock = udt(0, .5)

for i in range(10):
    sock.udt_send(i, 1, str(i), destination)

sock = udt(0, 0)
sock.udt_send(-1, 0, "Chaos: \n", destination)

sock = udt(.5, 1)
for i in range(10):
    sock.udt_send(i, 1, str(i), destination)
