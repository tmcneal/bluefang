# -*- coding: utf-8 -*-

import dbus # type: ignore
import bluetooth # type: ignore
from queue import *
from bluefang.constants import *
from typing import Any, List
import logging
from bluefang import l2cap


class BluefangConnection:
    def __init__(self, device_address: str, devices: List[Any]) -> None: # TODO don't pass devices in here
        self.device_address = device_address # type: str
        self.q = Queue() # type: Queue
        self.devices = devices
        self.is_connected = False
    
    def connect(self) -> None:

        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        #device = manager.GetManagedObjects()['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
        the_device = next((x for x in self.devices if x.address == self.device_address), None)
        if the_device is None:
            raise Exception("Unable to find device %s. Try scanning first." % self.device_address)

        device = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, the_device.path), BLUEZ_DEVICE)
        control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_socket.connect((self.device_address, HID_CONTROL_PSM))
        logging.info("Connected! Spawning control thread")
        control_connection = l2cap.L2CAPServerThread(control_socket, self.device_address)
        control_connection.daemon = True
        control_connection.start()

        interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_socket.connect((self.device_address, HID_INTERRUPT_PSM))
        logging.info("Connected! Spawning interrupt thread")
        interrupt_connection = l2cap.L2CAPClientThread(interrupt_socket, self.device_address, self.q)
        interrupt_connection.daemon = True
        interrupt_connection.start()

        self.is_connected = True

    def poll_commands(self) -> None:
        if not self.is_connected:
            raise Exception("Connection must first be established")

        while 1:
            command = input("Enter a command: ")
            self.send_command(command)

    def send_command(self, command: Any) -> None:
        if not self.is_connected:
            raise Exception("Connection must first be established")

        self.q.put(command)

    def disconnect(self, blah: Any) -> None:
        raise Exception("TODO Implement this")
