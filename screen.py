import curses
import time
import threading
import queue
from curses.textpad import Textbox
USERNAME = 'lisa'

ROOMS = {
    "server": ["hello, welcome to IRC program"],
    "room": ["Hi", "hello", "are you still there?", "i cant hear you!"]
}

msg_queue = queue.Queue()


def set_up_windows():
    wind = curses.newwin(curses.LINES - 3, curses.COLS - 20)
    text_box = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
    rooms_wind = curses.newwin(curses.LINES - 3,20, 0, curses.COLS-20)
    rooms_wind.border()
    rooms_wind.refresh()
    text_box.border()
    text_box.addstr(1,1, USERNAME + ": ")
    wind.border()
    text_box.refresh()
    wind.refresh()
    return (wind,text_box,rooms_wind)


def refresh_box(box):
    box.clear()
    box.border()
    box.addstr(1,1, USERNAME + ": ")
    box.refresh()


def print_to_window(wind):
    i = 1
    while True:
        while msg_queue.not_empty:
            wind.addstr(i, 1, USERNAME + ": " + msg_queue.get())
            wind.refresh()
            if i % (curses.LINES - 5) == 0:
                wind.clear()
                wind.move(1, 1)
                wind.border()
            i += 1
        time.sleep(0.1)


def main(stdscr):
    curses.curs_set(1)
    # wind = curses.newwin(curses.LINES - 3, curses.COLS - 20)
    # text_box = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
    # rooms_wind = curses.newwin(curses.LINES - 3,20, 0, curses.COLS-20)
    wind, inp, rooms = set_up_windows()

    i = 1
    for k in ROOMS.keys():
        rooms.addstr(i, 1, k)
        i += 1
        rooms.refresh()

    text = threading.Thread(target=print_to_window, args=(wind,))
    text.daemon = True
    text.start()

    with open('log', 'w') as wfile:
        while True:
            box = Textbox(inp)
            box.edit()
            message = box.gather()
            wfile.write(message)
            msg_queue.put(str(message).strip())
            refresh_box(inp)
            wind.addstr(0,0, message)
            wind.refresh()

    # # inp.nodelay(True)
    # while True:
    #     s = inp.getstr(5, 0, 40)
    # # x = ''
    # # s = ''
    # # while x != '\n':
    # #     x = inp.getch()
    # #     if x != -1:
    # #         s += str(x)
    #
    #
    #     wind.addstr(0,0, s)
    #     wind.refresh()
    #
    #     inp.refresh()

curses.wrapper(main)
