# -*- coding: utf-8 -*-

import logging
from queue import *
from threading import Thread
from bluefang import commands
from typing import Any


def binary(str: str) -> int:
    return int(str.replace(' ', ''), 2)


keyboard_keymap = {
    'a': 4,
    'b': 5,
    'c': 6,
    'd': 7,
    'e': 8,
    'f': 9,
    'g': 10,
    'h': 11,
    'i': 12,
    'j': 13,
    'k': 14,
    'l': 15,
    'm': 16,
    'n': 17,
    'o': 18,
    'p': 19,
    'q': 20,
    'r': 21,
    's': 22,
    't': 23,
    'u': 24,
    'v': 25,
    'w': 26,
    'x': 27,
    'y': 28,
    'z': 29,
    '1': 30,
    '2': 31,
    '3': 32,
    '4': 33,
    '5': 34,
    '6': 35,
    '7': 36,
    '8': 37,
    '9': 38,
    '0': 39
}

# This corresponds to the HID descriptor that is exposed via our SDP record.  The HID descriptor maps each supported
# command to a bit in a 5-byte HID consumer report.  See servicerecords.py for details.
# The values in the dict below correspond to 3rd and 4th byte in the 5-byte report.
consumer_keymap = {
    'next_track': (binary('0100 0000'), 0x00),
    'play_pause': (binary('0010 0000'), 0x00),
    'prev_track': (binary('0001 0000'), 0x00),
    'home': (binary('0000 0001'), 0x00),
    'pause': (0x00, binary('0001 0000')),
    'play': (0x00, binary('0000 1000'))
}

class L2CAPClientThread(Thread):
    def __init__(self, socket: Any, address: str, q: Queue) -> None:
        Thread.__init__(self)
        self.socket = socket # type: Any
        self.address = address # type: str
        self.q = q # type: Queue

    def run(self) -> None:
        logging.info("Sending on address: {0}".format(self.address))
        while True:
            command = self.q.get()
            self.process_command(command)
            #self.process_raw(command)
            self.q.task_done()
    
    def process_raw(self, command: Any) -> None:
        self.socket.send(bytes(bytearray(command)))

    def process_command(self, command: str) -> None:
        global consumer_keymap
        global keyboard_keymap
        logging.info("Received command: {}".format(command))
        # Keyboard Reports
        if command == commands.LEFT:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.RIGHT:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x4F, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.UP:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x52, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.DOWN:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x51, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.ENTER:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.CANCEL:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.MUTE_VOLUME:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.VOLUME_UP:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == commands.VOLUME_DOWN:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x81, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == 'delete':
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 42, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == 'space':
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 44, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == 'comma':
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 54, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == 'period':
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 55, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command in keyboard_keymap:
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, keyboard_keymap[command], 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        # Consumer Reports
        elif command in consumer_keymap:
            self.socket.send(bytes(bytearray((0xA1, 0x03, consumer_keymap[command][0], consumer_keymap[command][1], 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x03, 0x00, 0x00, 0x00))))
        else:
            logging.warning("Unknown command: {}".format(command))


class L2CAPServerThread(Thread):
    SIZE = 500

    def __init__(self, socket: Any, address: str) -> None:
        Thread.__init__(self)
        self.socket = socket
        self.address = address
    
    def run(self) -> None:
        logging.info("Receiving on address: {0}".format(self.address))
        while 1:
            data = self.socket.recv(L2CAPServerThread.SIZE)
            if data:
                self.process(data)
    
    def process(self, data: Any) -> None:
        logging.debug("Received data:")
        logging.debug(':'.join(hex(x) for x in data))
        if data[0] == 0x71:
            logging.info("Server wants to use Report Protocol Mode. Acknowledging.")
            self.socket.send(chr(0x00)) # Acknowledge that we will use this protocol mode
            self.socket.send(chr(0xA1) + chr(0x04))

"""
Every message should have the following:

L2CAP Length (2 bytes)
L2CAP CID (2 bytes)
HIDP Header (1 byte)
HID Payload (variable)
"""
