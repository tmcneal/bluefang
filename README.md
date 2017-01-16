# Bluefang
Bluetooth and HID utilities for Python 3

# Examples

## Discovering and pairing with device
```python
from bluefang import connection
bluetooth = connection.Bluefang()
bluetooth.registerProfile("/omnihub/profile")
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
You will be prompted to enter pin code after this.  This is successful but since an L2CAP socket isn't active, an
error will shown.  If you run the snippet below and reconnect it will complete the pairing process.

```python
from bluefang import connection
bluetooth = connection.Bluefang()
bluetooth.registerProfile("/omnihub/profile")
bluetooth.discoverable("on")
bluetooth.start_server()
```

## Connecting to trusted device (WIP)
```python
from bluefang import connection
bluetooth = connection.Bluefang()
bluetooth.registerProfile("/omnihub/profile")
bluetooth.connect("D0:03:4B:24:57:84")
```