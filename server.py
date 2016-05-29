import socketserver
import logging
import protocol
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


class Disconnection(Exception):
    """
    This exception is used to handle disconnects
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class IRCHandler(socketserver.StreamRequestHandler):
    """This is the IRC handler class used by the Threaded socket-server to handle requests"""
    def handle(self):
        """ handling request main logic """
        try:
            # read data from socket
            self.data = self.rfile.readline().strip()

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
            self.connection.close()
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

        return protocol.Packet(Opcode.KEEP_ALIVE, Status.OK)

    def _handle_connection(self, connect):
        """

        :param connect:
        :return:
        """
        if connect.username not in USERS:
            # create new user and add to USERS dictionary
            new_user = User(connect.username, self.connection)
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

    def _handle_create(self, create):
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

    def _handle_destroy(self, destroy):
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
    print("[*] server is now running on {} : {}".format(HOST, PORT))
    server.serve_forever()
