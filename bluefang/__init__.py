# -*- coding: utf-8 -*-

import bluetooth
import dbus
import dbus.mainloop.glib
from gi.repository import GObject as gobject
import sys
import time
import collections

from bluefang import agents
from bluefang import servicerecords
from bluefang import profile
from bluefang import l2cap

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1"
BLUEZ_AGENT_MANAGER = BLUEZ_SERVICE + ".AgentManager1"
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1"
BLUEZ_PROFILE_MANAGER = BLUEZ_SERVICE + ".ProfileManager1"

HID_UUID = "00001124-0000-1000-8000-00805f9b34fb"
HID_CONTROL_PSM = 17
HID_INTERRUPT_PSM = 19

BluetoothDevice = collections.namedtuple('BluetoothDevice', 'name alias address bluetooth_class is_connected is_paired path')

class Bluefang():
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.agent = agents.BluefangAgent()
        self.devices = []
        self.mainloop = gobject.MainLoop()
    
    def info(self):
        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        print("TEST")
        print(manager.GetManagedObjects())
        managed_objects = manager.GetManagedObjects()

        if '/org/bluez/hci0' not in managed_objects:
            raise Exception("Unable to find Bluetooth device")

        device = managed_objects['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
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

        dbus.SystemBus().add_signal_receiver(
            self._connection_established,
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            arg0="org.bluez.Device1"
        )

        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        #device = manager.GetManagedObjects()['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
        theDevice = next((x for x in self.devices if x.address == deviceAddress), None)
        if theDevice is None:
            raise Exception("Unable to find device %s. Try scanning first." % deviceAddress)

        device = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, theDevice.path), BLUEZ_DEVICE)
        #device.ConnectProfile(HID_UUID)
        #print("finished connect")
        #self.mainloop.run()
        control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        control_socket.connect((deviceAddress, HID_CONTROL_PSM))
        print("Connected! Spawning control thread")
        control_connection = l2cap.L2CAPServerThread(control_socket, deviceAddress)
        control_connection.daemon = True
        control_connection.start()

        interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        interrupt_socket.connect((deviceAddress, HID_INTERRUPT_PSM))
        print("Connected! Spawning interrupt thread")
        interrupt_connection = l2cap.L2CAPClientThread(interrupt_socket, deviceAddress)
        interrupt_connection.daemon = True
        interrupt_connection.start()
        # Device Connect
        #devicePath = '/org/bluez/hci0/dev_' + deviceAddress.replace(':', '_')
        #device = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, devicePath), BLUEZ_DEVICE)
        #device.Connect()

    def _connection_established(self, changed, invalidated, path):
        print("CONNECTION HAS BEEN ESTABLISHED")
        print(changed)
        print(invalidated)
        print(path)

    def start_server(self):

        """connection = BluetoothConnection(
            control_socket_psm=HID_CONTROL_PSM,
            interrupt_socket_psm=HID_INTERRUPT_PSM,
            mtu=64
        )
        connection.connect()"""

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

        control = l2cap.L2CAPServerThread(control_socket, control_address)
        control.daemon = True
        control.start()

        interrupt = l2cap.L2CAPClientThread(interrupt_socket, interrupt_address)
        interrupt.daemon = True
        interrupt.start()

    def poll_commands(self):
        while 1:
            command = input("Enter a command: ")
            self.send_command(command)

    def send_command(self, command):
        l2cap.q.put(command)

    def disconnect(self, blah):
        print("DISCONNECT %s" % blah) #TODO implement this later

    def discoverable(self, state):
        deviceManager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), 'org.freedesktop.DBus.Properties')
        if state == "on":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        elif state == "off":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        else:
            raise Exception("Unsupported state %s. Supported states: on, off" % state)

    def pair(self, timeout_in_ms=30000):
        #self.agent.start()
        self.agent.pair()
        gobject.timeout_add(timeout_in_ms, self._pair_timeout)
        self.mainloop.run()

    def _pair_timeout(self):
        print("Pair time out")
        self.mainloop.quit()
        print("Quit main loop")

    def scan(self, timeout_in_ms=30000):
        adapter = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)

        # Retrieve existing known devices
        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")

        adapter.StartDiscovery()

        gobject.timeout_add(timeout_in_ms, self._scan_timeout)

        self.mainloop.run()
        return self.devices

    def _scan_timeout(self):
        print("Device scan time out")
        adapter = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)
        try:
            adapter.StopDiscovery()
        except:
            print("Failed to stop discovery")

        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        managed_objects = manager.GetManagedObjects()
        print("objects!!")
        for path in managed_objects:
            print(path)
            properties = managed_objects[path]
            if BLUEZ_DEVICE in properties:
                device_properties = properties[BLUEZ_DEVICE]
                print('properties')
                print(device_properties)
                device = BluetoothDevice(
                    name=str(device_properties.get('Name')),
                    alias=str(device_properties['Alias']),
                    address=str(device_properties['Address']),
                    bluetooth_class=str(device_properties['Class']) if 'Class' in device_properties else 'Unknown',
                    is_connected=bool(device_properties['Connected']),
                    is_paired=bool(device_properties['Paired']),
                    path=str(path)
                )
                print("Adding device with name %s at path %s" % (device.name, device.path))
                self.devices.append(device)

        self.mainloop.quit()
        print("Quit the main loop")

    def register_profile(self, profile_path):
        print("REGISTER %s" % profile_path)
        profile_manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        the_profile = profile.Profile(dbus.SystemBus(), profile_path)
        profile_manager.RegisterProfile(
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

    def unregister_profile(self, profilePath):
        print("UNREGISTER %s" % profilePath)
        profileManager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        profileManager.UnregisterProfile(profilePath)
        #TODO handle the 'does not exist' error more gracefully?
