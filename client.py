import socketserver
import logging
import socket
import protocol
import queue
import threading
import os
from protocol import Status
from protocol import Opcode


target_host = '0.0.0.0'
target_port = 9999

# set up logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger("server-log")
logger.setLevel(logging.DEBUG)

# rooms client is in w/ messages
USERNAME = "player1"
ROOMS = []
msg_q = queue.Queue()


class IRCClient(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            # read data from socket
            self.data = self.rfile.readline().strip()
            logger.debug(self.data)
            # decode packet
            packet = protocol.decode(self.data)
            logger.debug("{} sent packet {}".format(self.client_address[0], packet.encode()))
            # stick packet on msg_q
            if packet.opcode == Opcode.PRIVATE_MSG:
                msg_q.put("*" + packet.username + ": " + packet.message)
            elif packet.opcode == Opcode.BROADCAST_MSG:
                msg_q.put("BROADCAST|" + packet.username + ": " + packet.message)
            elif packet.opcode == Opcode.MSG:
                msg_q.put(packet.username + "(" + packet.room + ")" + ": " + packet.message)
            elif packet.opcode == Opcode.DISCONNECT:
                logger.info("{}".format(packet.err))
                os._exit(1) # Handle Server Disconnect
        except SystemError:
            os._exit(1)


def send(packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_host, target_port))
    s.send(packet.encode())
    for res in s.makefile('r'):
        res = res.encode()
        res = protocol.decode(res)
        if res.status == protocol.Status.OK:
            s.close()
            return res
        elif res.status == protocol.Status.ERR:
            print(res.err)
            s.close()
            return res


def bsend(packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_host, target_port))
    s.send(packet.encode())
    s.close()


def display():
    while True:
        if msg_q.empty():
            return
        msg = msg_q.get(timeout=1)
        if msg is None:
            return
        print(msg)
        msg_q.task_done()


def message(cmd):
    s = cmd.split(' ')
    room = s[0]
    msg = ' '.join(s[1:])
    send(protocol.Message(USERNAME, msg, room))


def pm(cmd):
    s = cmd.split(" ")
    send_to = s[0]
    msg = " ".join(s[1:])
    send(protocol.PrivateMessage(USERNAME, msg, send_to))


def _list(cmd):
    if cmd == '':

        res = send_list(protocol.List())
        if res.status == Status.OK:
            print("Rooms Available:")
            for r in res.response:
                print(r)
        else:
            logger.info(res.err)
        return

    rooms = cmd.split(" ")
    res = []
    for room in rooms:
        res.append(send_list(protocol.List(room)))

    for r in res:
        if r.status == Status.OK:
            print("users in room: " + r.room)
            for user in r.response:
                print(user)
        else:
            logger.info(r.err)


def send_list(packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_host, target_port))
    s.send(packet.encode())
    for res in s.makefile('r'):
        res = res.encode()
        s.close()
        return protocol.decode(res)


def join(cmd):
    rooms = cmd.split(" ")
    for room in rooms:
        send_join(room)


def send_join(room):
    res = send(protocol.Join(USERNAME, room))
    if res.status == Status.OK:
        ROOMS.append(room)


def leave(cmd):
    rooms = cmd.split(" ")
    for room in rooms:
        send_leave(room)


def send_leave(room):
    res = send(protocol.Leave(USERNAME, room))
    if res.status == Status.OK and res.room in ROOMS:
        ROOMS.remove(room)


def broadcast(cmd):
    rooms = cmd.split(" ")
    msg = input("Broadcast message>")
    send_broadcast(msg, rooms)


def send_broadcast(msg, rooms):
    bsend(protocol.Broadcast(USERNAME, msg, rooms))


def create_room(cmd):
    rooms = cmd.split(" ")
    for room in rooms:
        send_create(room)


def send_create(room):
    res = send(protocol.Create(room))
    if res == Status.OK:
        if send(protocol.Join(USERNAME, room)) == Status.OK:
            ROOMS.append(room)


def destroy_room(cmd):
    rooms = cmd.split(" ")
    for room in rooms:
        send_destroy(room)


def send_destroy(room):
    res = send(protocol.Destroy(room))
    if res == Status.OK and res.room in ROOMS:
        ROOMS.remove(room)


def client():
    while True:
        cmd = input(USERNAME + " :")
        # /msg room message
        # /pm person message
        # /destroy rooms
        # /create rooms
        # /display room
        # /display
        # /list
        # /list room
        # /join room
        # /leave room
        # /broadcast room1 room2 room3 room4 room5

        if cmd == "/quit":
            send(protocol.Disconnect(USERNAME))
            break

        elif cmd.find("/display") != -1:
            display()

        elif cmd.find("/msg") != -1:
            message(cmd.strip("/msg").strip(" "))

        elif cmd.find("/pm") != -1:
            pm(cmd.strip("/pm").strip(" "))

        elif cmd.find("/create") != -1:
            create_room(cmd.strip("/create").strip(" "))

        elif cmd.find("/destroy") != -1:
            destroy_room(cmd.strip("/destroy").strip(" "))

        elif cmd.find("/list") != -1:
            _list(cmd.strip("/list").strip(" "))

        elif cmd.find("/join") != -1:
            join(cmd.strip("/join").strip(" "))

        elif cmd.find("/leave") != -1:
            leave(cmd.strip("/leave").strip(" "))

        elif cmd.find("/broadcast") != -1:
            broadcast(cmd.strip("/broadcast").strip(" "))

        else:
            print(cmd, " not a valid command")


def start_client(addr):
    client_server = socketserver.ThreadingTCPServer((addr[0], addr[1] + 100), IRCClient)
    logger.debug("[*] client is now running on {} : {}".format(addr[0], addr[1]))

    client_thread = threading.Thread(target=client_server.serve_forever)
    client_thread.daemon = True
    client_thread.start()

    client()


if __name__ == '__main__':
    try:
        # setup initial connection

        # select username
        USERNAME = input("enter username> ")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((target_host, target_port))
        # get address to be used for later
        address = s.getsockname()

        s.send(protocol.Connect(USERNAME, {}).encode())

        # if response is ok, start client's server, else print error
        for response in s.makefile('r'):
            response = response.encode()
            if protocol.decode(response).status == protocol.Status.OK:
                s.close()
                start_client(address)
            elif protocol.decode(response).status == protocol.Status.ERR:
                print(protocol.decode(response).err)
        s.close()
    except socket.error as serr:
        if serr.errno != 111:
            raise serr
        else:
            logger.error("could not contact server - server is probably down")

