

class User(object):
    """This class is used to describe a user which contains a nick, socket, and room list"""

    def __init__(self, nick, socket):
        self.nick = nick
        self.socket = socket
        self.rooms = [nick] # server is the help screen/list items

    def join_room(self, room):
        if self.rooms is None:
            self.rooms = [room]
        elif room not in self.rooms:
            self.rooms.append(room)

    def leave_room(self, room):
        if self.rooms is None:
            return
        elif room in self.rooms:
            self.rooms.remove(room)
