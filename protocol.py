"""
Protocol module - Used to implement the IRC Protocol
according to the RFC documentation in this repository.
"""

from enum import Enum, unique

__author__ = "Lisa Gray"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Lisa Gray"
__email__ = "gray7@pdx.edu"
__status__ = "Functional"


class Status(Enum):
    """
    Status Enum used for packet OK or ERR statuses
    """
    OK = 0
    ERR = 1

    def __str__(self):
        return self.name


@unique
class Opcode(Enum):
    KEEP_ALIVE = 0
    CONNECT = 1
    DISCONNECT = 2
    MSG = 3
    PRIVATE_MSG = 4
    BROADCAST_MSG = 5
    LIST = 6
    JOIN = 7
    LEAVE = 8
    CREATE = 9
    DESTROY = 10
    # FILE_TRANSFER = 11 - to be implemented later

    def __str__(self):
        return self.name


class Packet(object):
    """generic packet class"""

    def __init__(self, opcode, status, err=None):
        self.opcode = opcode
        self.status = status
        self.err = err

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Connect(Packet):
    def __init__(self, username, config={}, status=None, err=None):
        super().__init__(Opcode.CONNECT, status, err)
        self.username = username
        self.config = config

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.config.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Disconnect(Packet):
    def __init__(self, username, status=None, err=None):
        super().__init__(Opcode.DISCONNECT, status, err)
        self.username = username

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Message(Packet):
    def __init__(self, username, message, room, status=None, err=None):
        super().__init__(Opcode.MSG, status, err)
        self.username = username
        self.length = len(message.split())
        self.message = message
        self.room = room

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()

    def __str__(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n")


class PrivateMessage(Packet):
    def __init__(self, username, message, send_to, status=None, err=None):
        super().__init__(Opcode.PRIVATE_MSG, status, err)
        self.username = username
        self.length = len(message.split())
        self.message = message
        self.send_to = send_to

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.send_to.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()

    def __str__(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.send_to.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n")


class Broadcast(Packet):
    def __init__(self, username, message, rooms=None, status=None, err=None):
        super().__init__(Opcode.BROADCAST_MSG, status, err)
        self.username = username
        self.length = len(message.split())
        self.message = message
        self.rooms = " ".join(rooms)
        self.num_of_rooms = len(rooms)

    def encode(self):
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.num_of_rooms.__str__() + " "
                + self.rooms.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__()).encode()

    def __str__(self):
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.length.__str__() + " "
                + self.message.__str__() + " "
                + self.num_of_rooms.__str__() + " "
                + self.rooms.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__())


class List(Packet):
    def __init__(self, room=None, response=None, status=None, err=None):
        super().__init__(Opcode.LIST, status, err)
        self.room = room
        self.length = 0 if response is None else len(response)
        self.response = response

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.room.__str__() + " "
                + self.length.__str__() + " "
                + self.response.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()

    def __str__(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.room.__str__() + " "
                + self.length.__str__() + " "
                + self.response.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n")


class Join(Packet):
    def __init__(self, username, room, status=None, err=None):
        super().__init__(Opcode.JOIN, status, err)
        self.username = username
        self.room = room

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Leave(Packet):
    def __init__(self, username, room, status=None, err=None):
        super().__init__(Opcode.LEAVE, status, err)
        self.username = username
        self.room = room

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Create(Packet):
    def __init__(self, room, status=None, err=None):
        super().__init__(Opcode.CREATE, status, err)
        self.room = room

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


class Destroy(Packet):
    def __init__(self, room, status=None, err=None):
        super().__init__(Opcode.DESTROY, status, err)
        self.room = room

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.room.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__() + "\n").encode()


def decode(arg):
    """
    decode the argument into a packet

    :param arg: a string representation of a packet
    :return: a packet class of Type
    """
    packet = arg.decode().split(" ")
    packet = decode_dictionary[packet[0]](packet)
    if packet is None:
        raise TypeError

    return packet


def decode_type1(protocol_type):
    """
    decode a type 1 packet which can be defined as a packet that only takes on variable

    :param protocol_type: The type of protocol to be constructed
    :return: a function that will build the type
    """
    def d1(packet):
        """
        Inner function used to actually construct the packet

        :param packet: the packet to be decoded
        :return: a derived Packet object
        """
        var = packet[1]
        status = packet[2]
        err = ' '.join(packet[3:])
        if status == "OK":
            packet = protocol_type(var, status=Status.OK)
        elif status == "ERR":
            packet = protocol_type(var, status=Status.ERR, err=err)
        else:
            packet = protocol_type(var)
        return packet

    return d1


def decode_type2(protocol_type):
    """
    decode a type 1 packet which can be defined as a packet that takes two variables

    :param protocol_type: the type of protocol to be constructed
    :return: a function that will build the type
    """
    def d2(packet):
        """
        Inner function used to actually construct the packet

        :param packet: the packet to be decoded
        :return: a derived Packet object
        """
        var1 = packet[1]
        var2 = packet[2]
        status = packet[3]
        err = ' '.join(packet[4:])
        if status == "OK":
            packet = protocol_type(var1, var2, status=Status.OK)
        elif status == "ERR":
            packet = protocol_type(var1, var2, status=Status.ERR, err=err)
        else:
            packet = protocol_type(var1, var2)
        return packet

    return d2


def decode_list(packet):
    """
    This function decodes the List packet in str format to the List object

    :param packet: the packet to be decoded
    :return: a List packet
    """
    room = packet[1]
    length = int(packet[2])

    if length == 0:
        response = packet[3]
        status = packet[4]
        err = packet[5:]
    else:
        response = packet[3:(3 + length)]
        status = packet[3 + length]
        err = ' '.join(packet[4 + length:])

    if status == "OK":
        if room != "None":
            packet = List(room=room, response=response, status=Status.OK)
        else:
            packet = List(response=response, status=Status.OK)

    elif status == "ERR":
        if room != "None":
            packet = List(room=room, status=Status.ERR, err=err)
        else:
            packet = List(status=Status.ERR, err=err)

    else:
        if room != "None":
            packet = List(room=room)
        else:
            packet = List()
    return packet


def decode_type3(protocol_type):
    """
    decode a type 3 packet which can be defined as a packet that takes three variables

    :param protocol_type: The type of protocol to be constructed
    :return: a function that will build the type
    """
    def d3(packet):
        """
        Inner function used to actually construct the packet

        :param packet: the packet to be decoded
        :return: a derived Packet object
        """
        var1 = packet[1]
        length = int(packet[2])
        var2 = ' '.join(packet[3:(3 + length)])
        var3 = packet[(3 + length)]
        status = packet[4 + length]
        err = ' '.join(packet[5 + length:])
        if status == "OK":
            packet = protocol_type(var1, var2, var3, status=Status.OK)
        elif status == "ERR":
            packet = protocol_type(var1, var2, var3, status=Status.ERR, err=err)
        else:
            packet = protocol_type(var1, var2, var3)
        return packet

    return d3


def decode_broadcast(packet):
    """
    decode a Broadcast packet

    :param packet: a string representing a broadcast packet
    :return: return a Broadcast packet
    """
    username = packet[1]
    msg_length = int(packet[2])
    ml = packet[3:(3 + msg_length)]
    message = " ".join(ml)
    num_of_rooms = int(packet[3 + msg_length])
    rooms = packet[4 + msg_length: 4 + msg_length + num_of_rooms]
    status = packet[5 + msg_length + num_of_rooms]
    err = packet[6 + msg_length + num_of_rooms:]

    if status == "OK":
        packet = Broadcast(username, message, rooms, status=Status.OK)
    elif status == "ERR":
        packet = Broadcast(username, message, rooms, status=Status.ERR, err=err)
    else:
        packet = Broadcast(username, message, rooms)
    return packet


def decode_connect(packet):
    """
    decode a Connect packet

    :param packet: a string representing a Connect packet
    :return: return a Connect packet object
    """
    username = packet[1]
    configs = to_dict(packet[2])
    if packet[3] == "OK":
        packet = Connect(username, configs, status=Status.OK)
    elif packet[3] == "ERR":
        packet = Connect(username, configs, status=Status.ERR, err=' '.join(packet[4:]))
    else:
        packet = Connect(username, configs)
    return packet


# (only works with {}, for now)
def to_dict(string):
    if string == '{}':
        return {}
    l = string.replace('{', '').replace('}', '').replace('\'', '').split(', ')
    d = {}
    for kv in l:
        k, v = kv.split(': ')
        d[k] = v
    return d

"""
dictionary used to determine the
type of packet and returns appropriate packet class
"""
decode_dictionary = {
    "KEEP_ALIVE": Packet(Opcode.KEEP_ALIVE, Status.OK),
    "CONNECT": decode_connect,
    "DISCONNECT": decode_type1(Disconnect),
    "MSG": decode_type3(Message),
    "PRIVATE_MSG": decode_type3(PrivateMessage),
    "BROADCAST_MSG": decode_broadcast,
    "LIST": decode_list,
    "JOIN": decode_type2(Join),
    "LEAVE": decode_type2(Leave),
    "CREATE": decode_type1(Create),
    "DESTROY": decode_type1(Destroy),
}
