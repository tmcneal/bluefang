# -*- coding: utf-8 -*-

import dbus
import dbus.service
import time

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1"
BLUEZ_AGENT = BLUEZ_SERVICE + ".Agent1"
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1"
AGENT_PATH = "/omnihub/agent"
#CAPABILITY = "DisplayYesNo" # This works when pairing with PS3
#CAPABILITY = "KeyboardOnly" # Doesn't work with Apple TV
#CAPABILITY = "" # Doesn't work with Apple TV
#CAPABILITY = "NoInputNoOutput" # Doesn't work with Apple TV
#CAPABILITY = "KeyboardDisplay" # Doesn't work with Apple TV
CAPABILITY = "DisplayOnly" # This SHOULD work with Apple TV, according to git history

# For explanation of in and out signatures, see https://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html


def getManagedObjects():
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, "/"), "org.freedesktop.DBus.ObjectManager")
    return manager.GetManagedObjects()


def findAdapter():
    objects = getManagedObjects();
    bus = dbus.SystemBus()
    for path, ifaces in iter(objects.items()):
        adapter = ifaces.get(BLUEZ_ADAPTER)
        if adapter is None:
            continue
        obj = bus.get_object(BLUEZ_SERVICE, path)
        return dbus.Interface(obj, BLUEZ_ADAPTER)
    raise Exception("Bluetooth adapter not found")


class BluefangAgent(dbus.service.Object):
    pin_code = None

    def __init__(self):
        self.pin_code = "0000"

    def start(self):
        dbus.service.Object.__init__(self, dbus.SystemBus(), AGENT_PATH) #This will throw an error if an agent is already running
        print("Called register as default with capability %s" % CAPABILITY)
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent(AGENT_PATH, CAPABILITY)
        manager.RequestDefaultAgent(AGENT_PATH)
        print("Starting agent")

    def stop(self):
        print("Calling unregister")
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, "/org/bluez"), "org.bluez.AgentManager1")
        manager.UnregisterAgent(AGENT_PATH)
        if self._connection:
            self._connection._unregister_object_path(AGENT_PATH)

    @dbus.service.method(BLUEZ_AGENT, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode invoked")

    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("Pairing with device [{}]".format(device))
        self.pin_code = input("Please enter the pin code: ")
        print("Trying with pin code: [{}]".format(self.pin_code))
        self.trust_device(device)
        return self.pin_code

    @dbus.service.method("org.bluez.Agent", in_signature="ou", out_signature="")
    def DisplayPasskey(self, device, passkey):
        print("Passkey ({}, {:06d})".format(device, passkey))

    @dbus.service.method(BLUEZ_AGENT, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """Always confirm"""
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        time.sleep(2)
        print("Trusting device....")
        print(device)
        self.trust_device(device)
        return

    @dbus.service.method(BLUEZ_AGENT, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        """Always authorize"""
        print("AuthorizeService method invoked")
        return

    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey")
        passkey = input("Please enter pass key: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="")
    def RequestPairingConsent(self, device):
        print("RequestPairingConsent")
        return 

    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        """Always authorize"""
        print("Authorizing device [{}]".format(self.device))
        return

    @dbus.service.method(BLUEZ_AGENT, in_signature="", out_signature="")
    def Cancel(self):
        print("Pairing request canceled from device [{}]".format(self.device))

    def trust_device(self, path):
        print("Called trust device")
        bus = dbus.SystemBus()
        device_properties = dbus.Interface(bus.get_object(BLUEZ_SERVICE, path), "org.freedesktop.DBus.Properties")
        device_properties.Set(BLUEZ_DEVICE, "Trusted", True)

    def pair(self):
        print("Called start pairing")
        bus = dbus.SystemBus()
        adapter_path = findAdapter().object_path
        print("adapter")
        print(adapter_path)
        adapter = dbus.Interface(bus.get_object(BLUEZ_SERVICE, adapter_path), "org.freedesktop.DBus.Properties")
        adapter.Set(BLUEZ_ADAPTER, "Discoverable", True)

        print("Waiting to pair with device")
