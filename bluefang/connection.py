# -*- coding: utf-8 -*-

import bluetooth
import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject
from threading import Thread

from bluefang import agents
from bluefang import servicerecords

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1"
BLUEZ_AGENT_MANAGER = BLUEZ_SERVICE + ".AgentManager1"
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1"
BLUEZ_PROFILE_MANAGER = BLUEZ_SERVICE + ".ProfileManager1"

HID_UUID = "00001124-0000-1000-8000-00805f9b34fb"
HID_CONTROL_PSM = 17
HID_INTERRUPT_PSM = 19

class Bluefang():
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.agent = agents.BluefangAgent()
    
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

        socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        print("Attempting to connect to device %s" % deviceAddress)
        socket.connect((deviceAddress, 0x1001))
        print("Connected! Spawning thread")
        connection = L2CAPWorker(socket, deviceAddress)
        connection.daemon = True
        connection.start()
        # Device Connect
        #devicePath = '/org/bluez/hci0/dev_' + deviceAddress.replace(':', '_')
        #device = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, devicePath), BLUEZ_DEVICE)
        #device.Connect()

    def start_server(self):
        control_server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_server_socket.bind(("", HID_CONTROL_PSM))
        control_server_socket.listen(1)

        interrupt_server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_server_socket.bind(("", HID_INTERRUPT_PSM))
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
        self.agent.registerAsDefault()
        self.agent.startPairing()
        mainloop = gobject.MainLoop()
        mainloop.run()

    def registerProfile(self, profilePath):
        print("REGISTER %s" % profilePath)
        profileManager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        profileManager.RegisterProfile(
            profilePath,
            HID_UUID,
            {
                "Name": "Omnihub HID",
                "AutoConnect": False,
                "ServiceRecord": servicerecords.HID_PROFILE
            }
        )
        #TODO this doesn't register from CLI because the profile is unregistered when program exits
    
    def unregisterProfile(self, profilePath):
        print("UNREGISTER %s" % profilePath)
        profileManager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        profileManager.UnregisterProfile(profilePath)
        #TODO handle the 'does not exist' error more gracefully?
    
    def sendHIDMessage(self, msg):
        print("SEND MESSAGE %s" % msg)
    
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
        size = 1
        try:
            while 1:
                if self.sendOrReceive == 'send':
                    print("Sending on address %s" % self.address)
                    client.send(input("Enter message: "))
                else:
                    print("Listening on address %s" % self.address)
                    data = client.recv(size)
                    if data:
                        print("PSM: " + data)
                        client.send(data)
                    else:
                        print("NO DATA")
        except:
            print("Closing socket")
            #client.close()
            self.socket.close()

"""
Every message should have the following:

L2CAP Length (2 bytes)
L2CAP CID (2 bytes)
HIDP Header (1 byte)
HID Payload (variable)
"""
