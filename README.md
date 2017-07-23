# Bluefang
Bluetooth and HID utilities for Python 3

# Installation
```
pip install bluefang
```

# Install from source
- Local development: `./scripts/install-linux`
- As a package: `python setup.py install`
- If you prefer pip: `pip3 install -r requirements.txt --process-dependency-links`

# Other Commands
- Update Dependencies - `./scripts/update-dependencies`
- Run Tests - `./scripts/test`

# Examples

## Discovering and pairing with device
```python
# Enable logging
import logging
import sys
log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)

import bluefang
bluetooth = bluefang.Bluefang()
bluetooth.register_profile("/omnihub/profile")
bluetooth.agent.start()
bluetooth.discoverable("on")

from threading import Thread
class L2CAPServer(Thread):
    def __init__(self, bluetooth):
        Thread.__init__(self)
        self.bluetooth = bluetooth
    def run(self):
        bluetooth.start_server()

server_thread = L2CAPServer(bluetooth)
server_thread.daemon = True
server_thread.start()

bluetooth.pair()
```
You will be prompted to enter a pin code after this.  This should succeed, but since an L2CAP socket isn't active, an
error will shown.  If you run the snippet below and reconnect it will complete the pairing process.

```python
#Enable logging
import logging
import sys
log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)

import bluefang
bluetooth = bluefang.Bluefang()
bluetooth.register_profile("/omnihub/profile")
bluetooth.discoverable("on")
bluetooth.start_server()
```

## Connecting to trusted device
```python
#Enable logging
import logging
import sys
log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)

import bluefang
bluetooth = bluefang.Bluefang()
bluetooth.register_profile("/omnihub/profile")
bluetooth.scan(5000)
bluetooth.connect("D0:03:4B:24:57:84")
```

# HID Descriptor
```
// 78 bytes
0x05, 0x01,        // Usage Page (Generic Desktop Ctrls)  
0x09, 0x06,        // Usage (Keyboard)  
0xA1, 0x01,        // Collection (Application)  
0x85, 0x01,        //   Report ID (1)  
0x05, 0x07,        //   Usage Page (Kbrd/Keypad)  
0x75, 0x01,        //   Report Size (1)  
0x95, 0x08,        //   Report Count (8)  
0x19, 0xE0,        //   Usage Minimum (0xE0)  
0x29, 0xE7,        //   Usage Maximum (0xE7)  
0x15, 0x00,        //   Logical Minimum (0)  
0x25, 0x01,        //   Logical Maximum (1)  
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)  
0x95, 0x03,        //   Report Count (1)  
0x75, 0x08,        //   Report Size (8)  
0x15, 0x00,        //   Logical Minimum (0)  
0x25, 0x64,        //   Logical Maximum (100)  
0x05, 0x07,        //   Usage Page (Kbrd/Keypad)  
0x19, 0x00,        //   Usage Minimum (0x00)  
0x29, 0x65,        //   Usage Maximum (0x65)  
0x81, 0x00,        //   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)  
0xC0,              // End Collection  
0x05, 0x0C,        // Usage Page (Consumer)  
0x09, 0x01,        // Usage (Consumer Control)  
0xA1, 0x01,        // Collection (Application)  
0x85, 0x03,        //   Report ID (3)  
0x05, 0x0C,        //   Usage Page (Consumer)  
0x15, 0x00,        //   Logical Minimum (0)  
0x25, 0x01,        //   Logical Maximum (1)  
0x75, 0x01,        //   Report Size (1)  
0x95, 0x07,        //   Report Count (7)  
0x09, 0xb8, // Usage (Eject)
0x09, 0xb6, // Usage (Scan Previous Track)
0x09, 0xcd, // Usage (Play/Pause)
0x09, 0xb5, // Usage (Scan Next Track)
0x09, 0xe2, // Usage (Mute)
0x09, 0xea, // Usage (Volume Decrement)
0x09, 0xe9, // Usage (Volume Increment)
0x09, 0x30, // Usage (Power)
0x09, 0xB0, // Usage (Play)
0x09, 0xB1, // Usage (Pause)
0xC0,              // End Collection
```