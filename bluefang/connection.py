# -*- coding: utf-8 -*-

import bluetooth
import bluetooth._bluetooth as bluez
import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject
from queue import *
import sys
import time
from threading import Thread
import collections

from bluefang import agents
from bluefang import servicerecords
from bluefang import profile

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1"
BLUEZ_AGENT_MANAGER = BLUEZ_SERVICE + ".AgentManager1"
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1"
BLUEZ_PROFILE_MANAGER = BLUEZ_SERVICE + ".ProfileManager1"

HID_UUID = "00001124-0000-1000-8000-00805f9b34fb"
HID_CONTROL_PSM = 17
HID_INTERRUPT_PSM = 19

q = Queue()

BluetoothDevice = collections.namedtuple('BluetoothDevice', 'name alias address bluetooth_class is_connected is_paired path')

class Bluefang():
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.agent = agents.BluefangAgent()
        self.devices = []
        self.mainloop = gobject.MainLoop()
    
    def info(self):
        manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        device = manager.GetManagedObjects()['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
        #TODO Pull device name dynamically
        adapter = device[BLUEZ_ADAPTER]

        print(adapter)
        return adapter

    def connect(self, deviceAddress):
        """
        Attempt to connect to the given Device.
        """

        #TODO verify agent has been started prior to connecting
        try:
            self.agent.start()
        except KeyError:
            print("Agent has already been started. Skipping...")
        
        self.bus.add_signal_receiver(self._connection_established,
            dbus_interface = "org.freedesktop.DBus.Properties",
            signal_name = "PropertiesChanged",
            arg0 = "org.bluez.Device1")
        
        manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        #device = manager.GetManagedObjects()['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
        print("test before connect")
        theDevice = next((x for x in self.devices if x.address == deviceAddress), None)
        if theDevice == None:
            raise Exception("Unable to find device %s. Try scanning first." % deviceAddress)
        
        device = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, theDevice.path), BLUEZ_DEVICE)
        print(device)
        #device.ConnectProfile(HID_UUID)
        #print("finished connect")
        #self.mainloop.run()
        control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_socket.connect((deviceAddress, HID_CONTROL_PSM))
        print("Connected! Spawning control thread")
        control_connection = L2CAPWorker(control_socket, deviceAddress, 'receive')
        control_connection.daemon = True
        control_connection.start()

        interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_socket.connect((deviceAddress, HID_INTERRUPT_PSM))
        print("Connected! Spawning interrupt thread")
        interrupt_connection = L2CAPWorker(interrupt_socket, deviceAddress, 'send')
        interrupt_connection.daemon = True
        interrupt_connection.start()
        # Device Connect
        #devicePath = '/org/bluez/hci0/dev_' + deviceAddress.replace(':', '_')
        #device = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, devicePath), BLUEZ_DEVICE)
        #device.Connect()

    def _connection_established(self, changed, invalidated, path):
        print("CONNECTION HAS BEEN ESTABLISHED")
        print(changed)
        print(invalidated)
        print(path)

    def start_server(self):
        control_server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_server_socket.bind(("", HID_CONTROL_PSM))
        bluetooth.set_l2cap_mtu(control_server_socket, 64)
        control_server_socket.listen(1)

        interrupt_server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_server_socket.bind(("", HID_INTERRUPT_PSM))
        bluetooth.set_l2cap_mtu(interrupt_server_socket, 64)
        interrupt_server_socket.listen(1)

        print("Listening on both PSMs")

        control_socket, control_address = control_server_socket.accept()
        interrupt_socket, interrupt_address = interrupt_server_socket.accept()

        print("Spawned control and interrupt connection threads")

        control = L2CAPWorker(control_socket, control_address, 'receive')
        control.daemon = True
        control.start()

        interrupt = L2CAPWorker(interrupt_socket, interrupt_address, 'send')
        interrupt.daemon = True
        interrupt.start()

    def poll_commands(self):
        while 1:
            command = input("Enter a command: ")
            self.send_command(command)

    def send_command(self, command):
        q.put(command)

    def disconnect(self, blah):
        print("DISCONNECT %s" % blah) #TODO implement this

    def discoverable(self, state):
        deviceManager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), 'org.freedesktop.DBus.Properties')
        if state == "on":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        elif state == "off":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        else:
            raise Error("Unsupported state %s. Supported states: on, off" % state)

    def pair(self):
        #self.agent.registerAsDefault()
        self.agent.startPairing()
        self.mainloop.run()

    def scan(self):
        adapter = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)

        # Retrieve existing known devices
        manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")

        adapter.StartDiscovery()

        gobject.timeout_add(5000, self._scan_timeout)

        self.mainloop.run()
        return self.devices

    def _scan_timeout(self):
        print("Device scan time out")
        adapter = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)
        try:
            adapter.StopDiscovery()
        except:
            print("Failed to stop discovery")

        manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        managed_objects = manager.GetManagedObjects()
        print("objects!!")
        for path in managed_objects:
            properties = managed_objects[path]
            if BLUEZ_DEVICE in properties:
                device_properties = properties[BLUEZ_DEVICE]
                print('properties')
                print(device_properties)
                device = BluetoothDevice(
                    name = device_properties.get('Name'),
                    alias = device_properties['Alias'],
                    address = device_properties['Address'],
                    bluetooth_class = device_properties['Class'] if 'Class' in device_properties else 'Unknown',
                    is_connected = device_properties['Connected'],
                    is_paired = device_properties['Paired'],
                    path = path
                )
                print("Adding device with name %s at path %s" % (device.name, device.path))
                self.devices.append(device)

        self.mainloop.quit()
        print("Quit the main loop")

    def registerProfile(self, profilePath):
        print("REGISTER %s" % profilePath)
        profileManager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        the_profile = profile.Profile(self.bus, profilePath)
        profileManager.RegisterProfile(
            the_profile,
            HID_UUID,
            {
                "Name": "Omnihub HID",
                "AutoConnect": True,
                "ServiceRecord": servicerecords.HID_PROFILE
            }
        )
        print("Finished registering profile")
        #TODO this doesn't register from CLI because the profile is unregistered when program exits
    
    def unregisterProfile(self, profilePath):
        print("UNREGISTER %s" % profilePath)
        profileManager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        profileManager.UnregisterProfile(profilePath)
        #TODO handle the 'does not exist' error more gracefully?
    
    def isConnectionEstablished(self):
        print("Connection established?")
        return True

class L2CAPWorker(Thread):
    def __init__(self, socket, address, sendOrReceive):
        Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.sendOrReceive = sendOrReceive

    def run(self):
        size = 500
        try:
            if self.sendOrReceive == 'send':
                print("Sending on address: {0}".format(self.address))
                while True:
                    command = q.get()
                    print("Received command: " + command)
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
                        print("Unknown command: " + command)
                    q.task_done()

                    #self.socket.send(chr(0xA1) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00))
                    #self.socket.send(chr(0xA1) + chr(0x54)) #up
                    #self.socket.send(chr(0xA1) + chr(0x55)) #right
                    #self.socket.send(chr(0xA1) + chr(0x56)) #down
                    #self.socket.send(chr(0xA1) + chr(0x57)) #left
            else:
                print("Receiving on address: {0}".format(self.address))
                while 1:
                    data = self.socket.recv(size)
                    if data:
                        print("Received data:")
                        print(':'.join(hex(x) for x in data))
                        if data[0] == 0x71:
                            print("Server wants to use Report Protocol Mode. Acknowledging.")
                            self.socket.send(chr(0x00)) # Acknowledge that we will use this protocol mode
                            self.socket.send(chr(0xA1) + chr(0x04))
        finally:
            print("Closing socket for address: ${0}".format(self.address))
            #client.close()
            self.socket.close()

"""
Every message should have the following:

L2CAP Length (2 bytes)
L2CAP CID (2 bytes)
HIDP Header (1 byte)
HID Payload (variable)
"""
