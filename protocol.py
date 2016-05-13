from enum import Enum, unique

def decode(arg):
    packet = arg.decode().split(" ")
    if packet[0] == Opcode.KEEP_ALIVE.__str__():
        packet = Packet('KEEP_ALIVE', Status.OK)
    elif packet[0] == Opcode.CONNECT.__str__():
        username = packet[1]
        configs = to_dict(packet[2])
        packet = Connect(username, configs, status=Status.OK)
    return packet

def to_dict(string):
    if string == '{}':
        return {}

    print(string)
    l = string.replace('{', '').replace('}', '').replace('\'', '').split(', ')
    print(l)
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
    def __init__(self, opcode, status, err):
        self.opcode = opcode
        self.status = status
        self.err = err

    def encode(self):
    """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
            + self.status.__str__() + " "
            + self.err.__str__()).encode()

class Connect(Packet):
    def __init__(self, username, config={}, status = None, err = None):
        super().__init__(Opcode.CONNECT, status, err)
        self.username = username
        self.config = config

    def encode(self):
        """encode the message into a string to be sent over TCP socket"""
        return (self.opcode.__str__() + " "
                + self.username.__str__() + " "
                + self.config.__str__() + " "
                + self.status.__str__() + " "
                + self.err.__str__()).encode()

class Disconnect(Packet):
    def __init__(self, username, status = None, err = None):
        super().__init__(Opcode.DISCONNECT, status, err)
        self.username = username


class Message(Packet):
    def __init__(self, username, message, room, status = None, err = None):
        super().__init__(Opcode.MSG, status, err)
        self.username = username
        self.message = message

class PrivateMessage(Packet):
    def __init__(self, username, message, send_to, status = None, err = None):
        super().__init__(Opcode.PRIVATE_MSG, status, err)
        self.username = username
        self.message = message
        self.send_to = send_to

class Broadcast(Packet):
    def __init__(self, username, message, rooms, status = None, err = None):
        super().__init__(Opcode.BROADCAST_MSG, status, err)
        self.username = username
        self.message = message
        self.rooms = rooms

class List(Packet):
    def __init__(self, room='', response = [], status = None, err = None):
        super().__init__(Opcode.LIST, status , err)
        self.room = room
        self.response = response

class Join(Packet):
    def __init__(self, username, room, status = None, err = None):
        super().__init__(Opcode.JOIN, status, err)
        self.username = username
        self.room = room

class Leave(Packet):
    def __init__(self, username, room, status = None, err = None):
        super().__init__(Opcode.LEAVE, status, err)
        self.username = username
        self.room = room

class Create(Packet):
    def __init__(self, room, status = None, err = None):
        super().__init__(Opcode.CREATE, status, err)
        self.room = room

class Destroy(Packet):
    def __init__(self, room, status = None, err = None):
        super().__init__(Opcode.DESTROY, status, err)
        self.room = room
