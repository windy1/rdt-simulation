from rdt import rdt

s = """==============
UVMPM Protocol
==============

Christian Skalka (ceskalka), 9/18/18

The UVMPM protocol supports personal messaging applications. It is a
client-server protocol and is intended to run over TCP.

The client and server engage in 3 protocol phases that must occur in
order-- 1. Handshake, 2. Authentication, and 3. Request-Response. In the
following description, we will write:

  C: m

to denote that a client C sends a message m, and:

  S: m

to denote that the server sends a message m.

1. Handshake: To negotiate the handshake phase, a client C and server
S must exchange the following messages in order:

  C: HELLO
  S: HELLO

After the client receives HELLO, S is guaranteed to be ready for
Authentication.
  
2. Authentication: To initiate authentication on the server S, the
client C must send the following <username>, <password> combo:

  C:  AUTH:<username>:<password>

If <username>, <password> is successfully authenticated, S will
respond with the following two messages indicating successful
authentication and signin:

  S: AUTHYES
  S: SIGNIN:<username>

The server will also send the following message to all other currently
signed-in user instances indicating signin by <username>:

  S: SIGNIN:<username>
  
If <username>, <password> fails to be authenticated on S, S will
respond with the following two message:

  S: AUTHNO

The server will tolerate an unlimited number of failed signin
attempts, but will close the connection if there is a syntax error in
authentication request.  After successful signin, the client C can
submit commands to S in the Request-Response phase.

3. Request-Response

Commands and message formats are supported to list currently signed-in
users, to send messages between users, and to sign off.

 - Listing users: To list users currently signed in, the client
   submits the LIST command:

  C: LIST

The server will response with a comma-delimited list of currently
signed-in users:

  S: <user1>, ..., <usern>

 - Sending messages: To send <text> to <user>, the client submits
 a message in the following format:

  C: To:<user>:<text>

Once the message is received, the server S will send a copy of <text>
to <user> in the following format:

  S: From:<user>:<text>

Note that this message will be sent to *every* signed in instance of
<user>.


 - Signing off: To sign off, the client submits a message in the
 following format:

  C: BYE

Following sign off by <user>, the server will send an alert to all
signed-in user instances in the following format:

  S: SIGNOFF:<user>

and then the server will close the connection with the user."""

r = rdt(
    packet_loss=0.5,
    reorder=0,
    seg_size=32,
    wind=100,
    src_addr=("127.0.0.1", 12000),
    dest_addr=("127.0.0.1", 12001)
)
r.send_all(s)
