import socketserver
import socket
import logging
import protocol
import signal
import sys
from protocol import Opcode
from protocol import Status
from User import User

# set up host and port
HOST, PORT = "0.0.0.0", 9999

# set up logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger("server-log")
logger.setLevel(logging.DEBUG)

# initialize USERS and ROOMS data structures
USERS = {}
ROOMS = []
SERVER_SOCKET = None

class Disconnection(Exception):
    """
    This exception is used to handle disconnects
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def disconnect(users):
    for nick, user in users.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(user.address)
        s.send(protocol.Disconnect(nick,
                                   status=Status.ERR,
                                   err="server shutting down").encode())
        s.close()


def signal_handler(signal, frame):
    """Function handles signal interrupt (CTRL-C)
    :param signal: signal caught
    :param frame: current stack frame
    """

    disconnect(USERS)

    logging.info('Server turning off')
    SERVER_SOCKET.close()

    sys.exit(0)


# initialize signal handler
signal.signal(signal.SIGINT, signal_handler)


def message(username, msg, room):
    # does user and room exist
    if username in USERS and room in ROOMS:
        # if user is in the room, then message room
        if room in USERS[username].rooms:
            logger.debug("{}".format(USERS))
            addresses = []
            for nick, user in USERS.items():
                if room in USERS[nick].rooms:
                    addresses.append(user.address)

            msg_packet = protocol.Message(username, msg, room, status=Status.OK)

            sockets = append_sockets(addresses)

            for s in sockets:
                with s.makefile('w') as wfile:
                    wfile.write(msg_packet.__str__())
                s.close()


def append_sockets(addresses):
    sockets = []
    for address in addresses:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        sockets.append(s)
    return sockets


def priv_message(username, msg, send_to):
    # does user and send_to user exist
    if username in USERS and send_to in USERS:
        msg_packet = protocol.PrivateMessage(username, msg, send_to, status=Status.OK)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(USERS[send_to].address)

        with s.makefile('w') as wfile:
            wfile.write(msg_packet.__str__())
        s.close()


def broadc_message(username, msg, rooms):
    users = []
    users = find_users_broadcast(rooms)

    bmsg_packet = protocol.Broadcast(username, msg, rooms, status=Status.OK)

    sockets = []
    for user in users:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(user.address)
        sockets.append(s)

    for s in sockets:
        with s.makefile("w") as wfile:
            wfile.write(bmsg_packet.__str__())
        s.close()


def find_users_broadcast(rooms):
    users = []
    for room in rooms:
        if room in ROOMS:
            for nick, user in USERS.items():
                append_user(room, user, users)
    return users


def append_user(room, user, users):
    if room in user.rooms and user not in users:
        users.append(user)


class IRCHandler(socketserver.StreamRequestHandler):
    """This is the IRC handler class used by the Threaded socket-server to handle requests"""

    def handle(self):
        """ handling request main logic """
        try:
            # read data from socket
            self.data = self.rfile.readline().strip()

            logger.debug(self.request.getpeername())

            # decode packet
            packet = protocol.decode(self.data)
            logger.debug("{} sent packet {}".format(self.client_address[0], packet.encode()))

            # handle packet
            response = self._handle_packet(packet)

            logger.debug("connected USERS - {}".format(USERS.__str__()))
            logger.debug("rooms available - {}".format(ROOMS.__str__()))

            # write response
            self.wfile.write(response.encode())
        except Disconnection:
            return

    def _handle_packet(self, packet):
        """

        :param packet:
        :return:
        """
        if packet.opcode == Opcode.CONNECT:
            return self._handle_connection(packet)
        elif packet.opcode == Opcode.DISCONNECT:
            return self._handle_disconnect(packet)
        elif packet.opcode == Opcode.CREATE:
            return self._handle_create(packet)
        elif packet.opcode == Opcode.DESTROY:
            return self._handle_destroy(packet)
        elif packet.opcode == Opcode.JOIN:
            return self._handle_join(packet)
        elif packet.opcode == Opcode.LEAVE:
            return self._handle_leave(packet)
        elif packet.opcode == Opcode.LIST:
            return self._handle_list(packet)
        elif packet.opcode == Opcode.MSG:
            return self._handle_message(packet)
        elif packet.opcode == Opcode.PRIVATE_MSG:
            return self._handle_private_message(packet)
        elif packet.opcode == Opcode.BROADCAST_MSG:
            return self._handle_broadcast_message(packet)

        return protocol.Packet(Opcode.KEEP_ALIVE, Status.OK)

    def _handle_connection(self, connect):
        """

        :param connect:
        :return:
        """
        if connect.username not in USERS:
            # create new user and add to USERS dictionary
            new_user = User(connect.username, self.connection.getpeername())
            port = new_user.address[1] + 100
            new_user.address = (new_user.address[0], port)
            logger.debug("{} {}".format(new_user.address[0], new_user.address[1]))
            USERS[new_user.nick] = new_user
            # log new user
            logger.info("new user {} has connected".format(new_user.nick))

            # set connect status to OK
            connect.status = Status.OK
            return connect
        else:
            return IRCHandler._error(connect,
                                     "user already exists. choose another name")

    def _handle_disconnect(self, disconnect):
        """

        :param disconnect:
        :return:
        """
        if disconnect.username in USERS:
            # send message of disconnect to rooms
            # remove from USERS
            USERS.pop(disconnect.username)
            logger.info("user {} has disconnected".format(disconnect.username))
            logger.debug("connected USERS - {}".format(USERS.__str__()))
            # send OK response
            disconnect.status = Status.OK
            self.wfile.write(disconnect.encode())

            raise Disconnection(disconnect)
        else:
            return IRCHandler._error(disconnect,
                                     "username specified does not exist in server.")

    @staticmethod
    def _handle_create(create):
        """

        :param create:
        :return:
        """
        if create.room not in ROOMS:
            # create the room
            ROOMS.append(create.room)

            # log room creation
            logger.info("room {} has now been created.".format(create.room))

            create.status = Status.OK
            return create
        else:
            return IRCHandler._error(create,
                                     "room already exists, use /join to join the room.")

    @staticmethod
    def _handle_destroy(destroy):
        """

        :param destroy:
        :return:
        """
        if destroy.room in ROOMS:
            # remove the room
            ROOMS.remove(destroy.room)

            # log room removal
            logger.info("room {} has now been removed.".format(destroy.room))

            destroy.status = Status.OK
            return destroy
        else:
            return IRCHandler._error(destroy,
                                     "the room specified does not exist")

    @staticmethod
    def _handle_join(join):
        if join.username in USERS and join.room in ROOMS:
            # join room in users group
            USERS[join.username].join_room(join.room)

            # log join
            logger.info("user {} has joined room {}"
                        .format(join.username, join.room))
            # message room that user joined
            message(join.username, "user {} has joined room {}".format(join.username, join.room), join.room)
            # return ok
            join.status = Status.OK
            return join
        else:
            return IRCHandler._error(join, "was not able to join the room")

    @staticmethod
    def _handle_leave(leave):
        if leave.username in USERS and leave.room in ROOMS:
            # leave room in users group
            USERS[leave.username].leave_room(leave.room)

            # log leave
            logger.info("user {} has left room {}"
                        .format(leave.username, leave.room))

            # message room that user joined
            message(leave.username, "user {} has left room {}"
                    .format(leave.username, leave.room), leave.room)
            # return ok
            leave.status = Status.OK
            return leave
        else:
            return IRCHandler._error(leave, "unable to leave room")

    @staticmethod
    def _handle_list(_list):
        if _list.room is None:
            _list.response = ' '.join(ROOMS)
            _list.length = len(ROOMS)
            _list.status = Status.OK
            return _list
        elif _list.room in ROOMS:
            logger.debug("here2")
            members = []
            for nick, user in USERS.items():
                if _list.room in user.rooms:
                    members.append(nick)
            _list.response = ' '.join(members)
            _list.length = len(members)
            _list.status = Status.OK
            return _list
        else:
            return IRCHandler._error(_list, "error with list")

    @staticmethod
    def _handle_message(msg):
        if msg.username in USERS and msg.room in ROOMS:
            message(msg.username, msg.message, msg.room)
            logger.info("{} sent message {} to room {}".format(
                msg.username, msg.message, msg.room,
            ))
            msg.status = Status.OK
            return msg
        else:
            return IRCHandler._error(msg, "could not send message")

    @staticmethod
    def _handle_private_message(private_message):
        pmsg = private_message
        if pmsg.username in USERS and pmsg.send_to in USERS:
            priv_message(pmsg.username, pmsg.message, pmsg.send_to)
            logger.info("{} sent message {} to user {}".format(
                pmsg.username, pmsg.message, pmsg.send_to,
            ))
            pmsg.status = Status.OK
            return pmsg
        else:
            return IRCHandler._error(pmsg, "could not send private smessage")

    def _handle_broadcast_message(self, broadcast_message):
        bmsg = broadcast_message
        if bmsg.username in USERS:
            broadc_message(bmsg.username, bmsg.message, bmsg.rooms.split(" "))
            logger.info(
                "{} send broadcast message {} to rooms {}".format(
                    bmsg.username,
                    bmsg.message,
                    bmsg.rooms)
            )
            bmsg.status = Status.OK
            return bmsg
        else:
            return IRCHandler._error(bmsg, "error with sending the broadcast message")

    @staticmethod
    def _error(packet, error_message):
        """
        This static method is used for returning messages to client

        :param packet: is the packet to set error status to
        :param error_message: the message passed along
        :return: the packet
        """
        packet.status = Status.ERR
        packet.err = error_message
        return packet


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer((HOST, PORT), IRCHandler)
    SERVER_SOCKET = server.socket
    print("[*] server is now running on {} : {}".format(HOST, PORT))
    server.serve_forever()

