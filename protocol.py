from enum import Enum, unique


def decode(arg):
    packet = arg.decode().split(" ")
    if packet[0] == Opcode.KEEP_ALIVE.__str__():
        packet = Packet(Opcode.KEEP_ALIVE, Status.OK)

    elif packet[0] == Opcode.CONNECT.__str__():
        packet = decode_connect(packet)

    elif packet[0] == Opcode.DISCONNECT.__str__():
        packet = decode_type1(packet, Disconnect)

    elif packet[0] == Opcode.CREATE.__str__():
        packet = decode_type1(packet, Create)

    elif packet[0] == Opcode.DESTROY.__str__():
        packet = decode_type1(packet, Destroy)

    elif packet[0] == Opcode.JOIN.__str__():
        packet = decode_type2(packet, Join)

    elif packet[0] == Opcode.LEAVE.__str__():
        packet = decode_type2(packet, Leave)

    elif packet[0] == Opcode.LIST.__str__():
        packet = decode_list(packet)

    elif packet[0] == Opcode.MSG.__str__():
        packet = decode_type3(packet, Message)

    elif packet[0] == Opcode.PRIVATE_MSG.__str__():
        packet = decode_type3(packet, PrivateMessage)

    elif packet[0] == Opcode.BROADCAST_MSG.__str__():
        # packet = decode_type3(packet, Broadcast)
        pass

    return packet


def decode_type1(packet, protocol_type):
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


def decode_type2(packet, protocol_type):
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


def decode_list(packet):
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


def decode_type3(packet, protocol_type):
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


def decode_connect(packet):
    username = packet[1]
    configs = to_dict(packet[2])
    if packet[3] == "OK":
        packet = Connect(username, configs, status=Status.OK)
    elif packet[3] == "ERR":
        packet = Connect(username, configs, status=Status.ERR, err=' '.join(packet[4:]))
    else:
        packet = Connect(username, configs)
    return packet


def to_dict(string):
    if string == '{}':
        return {}
    l = string.replace('{', '').replace('}', '').replace('\'', '').split(', ')
    d = {}
    for kv in l:
        k, v = kv.split(': ')
        d[k] = v
    return d


class Status(Enum):
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
    FILE_TRANSFER = 11

    def __str__(self):
        return self.name


class Packet(object):
    """generic packet class - used as a keep-alive message as well"""

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
        self.length = len(message)
        self.message = message
        self.rooms = rooms


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
