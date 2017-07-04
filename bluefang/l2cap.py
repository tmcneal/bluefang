# -*- coding: utf-8 -*-

import logging
from queue import *
from threading import Thread

q = Queue()

class L2CAPClientThread(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.socket = socket
        self.address = address

    def run(self):
        logging.info("Sending on address: {0}".format(self.address))
        while True:
            command = q.get()
            self.process_command(command)
            q.task_done()
    
    def process_command(self, command):
        logging.info("Received command: " + command)
        if command == "left":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == "right":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x4F, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == "up":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x52, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == "down":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x51, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == "enter":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        elif command == "cancel":
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00, 0x00))))
            self.socket.send(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
        else:
            logging.warning("Unknown command: " + command)


class L2CAPServerThread(Thread):
    SIZE = 500

    def __init__(self, socket, address):
        Thread.__init__(self)
        self.socket = socket
        self.address = address
    
    def run(self):
        logging.info("Receiving on address: {0}".format(self.address))
        while 1:
            data = self.socket.recv(L2CAPServerThread.SIZE)
            if data:
                self.process(data)
    
    def process(self, data):
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
