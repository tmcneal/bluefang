# -*- coding: utf-8 -*-

import bluetooth # type: ignore
import dbus # type: ignore
import dbus.mainloop.glib # type: ignore
from gi.repository import GObject as gobject # type: ignore
import logging
from queue import *
import sys
import time # type: ignore
import collections
from typing import Any, List, Optional

from bluefang import agents
from bluefang.connection import BluefangConnection
from bluefang import servicerecords
from bluefang import profile
from bluefang import l2cap
from bluefang.constants import *

BluetoothDevice = collections.namedtuple('BluetoothDevice', 'name alias address bluetooth_class is_connected is_paired path')


class Bluefang():
    def __init__(self) -> None:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.agent = agents.BluefangAgent() # type: Any
        self.devices = [] # type: List[Any]
        self.mainloop = gobject.MainLoop() # type: Any
    
    def info(self) -> Any:
        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        managed_objects = manager.GetManagedObjects()

        if '/org/bluez/hci0' not in managed_objects:
            raise Exception("Unable to find Bluetooth device")

        device = managed_objects['/org/bluez/hci0'] # Requires correct permissions in /etc/dbus-1/system-local.conf
        #TODO Pull device name dynamically
        adapter = device[BLUEZ_ADAPTER]

        return adapter

    def connect(self, device_address: str) -> Optional[BluefangConnection]:
        """
        Attempt to connect to the given Device.
        """

        #TODO verify agent has been started prior to connecting
        try:
            self.agent.start()
        except KeyError:
            logging.exception("Agent has already been started. Skipping...")

        dbus.SystemBus().add_signal_receiver(
            self._connection_established,
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            arg0="org.bluez.Device1"
        )

        connection = BluefangConnection(device_address, self.devices)
        connection.connect()

        return connection

    def _connection_established(self, changed: Any, invalidated: Any, path: Any) -> None:
        logging.info("Connection has been established")

    def start_server(self) -> None:

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

        logging.info("Listening on both PSMs")

        control_socket, control_address = control_server_socket.accept()
        interrupt_socket, interrupt_address = interrupt_server_socket.accept()

        logging.info("Spawned control and interrupt connection threads")

        control = l2cap.L2CAPServerThread(control_socket, control_address)
        control.daemon = True
        control.start()

        interrupt = l2cap.L2CAPClientThread(interrupt_socket, interrupt_address, Queue())
        interrupt.daemon = True
        interrupt.start()

    def discoverable(self, state: str) -> None:
        deviceManager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), 'org.freedesktop.DBus.Properties')
        if state == "on":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        elif state == "off":
            deviceManager.Set(BLUEZ_ADAPTER, 'Discoverable', True)
        else:
            raise Exception("Unsupported state %s. Supported states: on, off" % state)

    def pair(self, timeout_in_ms: int=30000) -> None:
        #self.agent.start()
        self.agent.pair()
        gobject.timeout_add(timeout_in_ms, self._pair_timeout)
        self.mainloop.run()

    def _pair_timeout(self) -> None:
        logging.info("Pair time out")
        self._quit_mainloop()

    def scan(self, timeout_in_ms: int=30000) -> List[Any]:
        adapter = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)

        # Retrieve existing known devices
        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")

        adapter.StartDiscovery()

        gobject.timeout_add(timeout_in_ms, self._scan_timeout)

        self.mainloop.run()
        return self.devices

    def _scan_timeout(self) -> None:
        logging.info("Device scan time out")
        adapter = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez/hci0"), BLUEZ_ADAPTER)
        try:
            adapter.StopDiscovery()
        except:
            logging.exception("Failed to stop discovery")

        manager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
        managed_objects = manager.GetManagedObjects()
        for path in managed_objects:
            properties = managed_objects[path]
            if BLUEZ_DEVICE in properties:
                device_properties = properties[BLUEZ_DEVICE]
                logging.debug('properties')
                logging.debug(device_properties)
                device = BluetoothDevice(
                    name=str(device_properties.get('Name')),
                    alias=str(device_properties['Alias']),
                    address=str(device_properties['Address']),
                    bluetooth_class=str(device_properties['Class']) if 'Class' in device_properties else 'Unknown',
                    is_connected=bool(device_properties['Connected']),
                    is_paired=bool(device_properties['Paired']),
                    path=str(path)
                )
                logging.info("Adding device with name %s at path %s" % (device.name, device.path))
                self.devices.append(device)

        self._quit_mainloop()

    def register_profile(self, profile_path: str) -> None:
        logging.info("Registering %s" % profile_path)
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
        #TODO this doesn't register from CLI because the profile is unregistered when program exits

    def unregister_profile(self, profilePath: str) -> None:
        logging.info("Unregister %s" % profilePath)
        profileManager = dbus.Interface(dbus.SystemBus().get_object(BLUEZ_SERVICE, "/org/bluez"), BLUEZ_PROFILE_MANAGER)
        profileManager.UnregisterProfile(profilePath)
        #TODO handle the 'does not exist' error more gracefully?

    def _quit_mainloop(self) -> None:
        logging.info("Pair time out")
        self.mainloop.quit()
