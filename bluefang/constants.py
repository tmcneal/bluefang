
# -*- coding: utf-8 -*-

BLUEZ_SERVICE = "org.bluez" # type: str
BLUEZ_ADAPTER = BLUEZ_SERVICE + ".Adapter1" # type: str
BLUEZ_AGENT_MANAGER = BLUEZ_SERVICE + ".AgentManager1" # type: str
BLUEZ_DEVICE = BLUEZ_SERVICE + ".Device1" # type: str
BLUEZ_PROFILE_MANAGER = BLUEZ_SERVICE + ".ProfileManager1" # type: str

HID_UUID = "00001124-0000-1000-8000-00805f9b34fb" # type: str
HID_CONTROL_PSM = 17 # type: int
HID_INTERRUPT_PSM = 19 # type: int