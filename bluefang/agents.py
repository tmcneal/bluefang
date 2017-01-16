# -*- coding: utf-8 -*-

import dbus
import dbus.service

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1"
BLUEZ_AGENT = BLUEZ_SERVICE + ".Agent1"
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1"
AGENT_PATH = "/omnihub/agent"
CAPABILITY = "DisplayOnly"

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
        dbus.service.Object.__init__(self, dbus.SystemBus(), AGENT_PATH)
        self.pin_code = "0000"
    
        print("Starting Bluefang agent")
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode invoked")
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey invoked")
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("Pairing with device [{}]".format(device))
        self.pin_code = input("Please enter the pin code: ")
        print("Trying with pin code: [{}]".format(self.pin_code))
        self.trustDevice(device)
        return self.pin_code
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """Always confirm"""
        print("Pairing with device [{}]".format(device))
        self.trustDevice(device)
        return
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        """Always authorize"""
        print("AuthorizeService method invoked")
        return
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey returns 0")
        return dbus.UInt32(0)
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        """Always authorize"""
        print("Authorizing device [{}]".format(self.device))
        return
    
    @dbus.service.method(BLUEZ_AGENT, in_signature="", out_signature="")
    def Cancel(self):
        print("Pairing request canceled from device [{}]".format(self.device))
    
    def trustDevice(self, path):
        print("Called trust device")
        bus = dbus.SystemBus()
        device_properties = dbus.Interface(bus.get_object(BLUEZ_SERVICE, path), "org.freedesktop.DBus.Properties")
        device_properties.Set(BLUEZ_DEVICE, "Trusted", True)
    
    def registerAsDefault(self):
        print("Called register as default")
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent(AGENT_PATH, CAPABILITY)
        manager.RequestDefaultAgent(AGENT_PATH)
    
    def unregister(self):
        print("Calling unregister")
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, "/org/bluez"), "org.bluez.AgentManager1")
        manager.UnregisterAgent(AGENT_PATH)
    
    def startPairing(self):
        print("Called start pairing")
        bus = dbus.SystemBus()
        adapter_path = findAdapter().object_path
        adapter = dbus.Interface(bus.get_object(BLUEZ_SERVICE, adapter_path), "org.freedesktop.DBus.Properties")
        adapter.Set(BLUEZ_ADAPTER, "Discoverable", True)
        
        print("Waiting to pair with device")
        