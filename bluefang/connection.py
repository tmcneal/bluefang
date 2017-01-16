# -*- coding: utf-8 -*-

import bluetooth
import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject

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

        # Device Connect
        devicePath = '/org/bluez/hci0/dev_' + deviceAddress.replace(':', '_')
        device = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE, devicePath), BLUEZ_DEVICE)
        device.Connect()

    def start_server(self):
        control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_socket.bind(("", HID_CONTROL_PSM))
        control_socket.listen(1)
        interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_socket.bind(("", HID_INTERRUPT_PSM))
        interrupt_socket.listen(1)

        control_socket, control_info = control_socket.accept()
        interrupt_socket, interrupt_info = interrupt_socket.accept()

        print("L2CAP connection established")

  """
  Every message should have the following:

  L2CAP Length (2 bytes)
  L2CAP CID (2 bytes)
  HIDP Header (1 byte)
  HID Payload (variable)
  """

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
