# Bluefang
Bluetooth and HID utilities for Python 3

# Installation
- Local development: `./scripts/install`
- As a package: `python setup.py install`
- If you prefer pip: `pip3 install -r requirements.txt --process-dependency-links`

# Other Commands
- Update Dependencies - `./scripts/update-dependencies`
- Run Tests - `./scripts/test`

# Examples

## Discovering and pairing with device
```python
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
import bluefang
bluetooth = bluefang.Bluefang()
bluetooth.register_profile("/omnihub/profile")
bluetooth.discoverable("on")
bluetooth.start_server()
```

## Connecting to trusted device
```python
import bluefang
bluetooth = bluefang.Bluefang()
bluetooth.register_profile("/omnihub/profile")
bluetooth.scan(5000)
bluetooth.connect("D0:03:4B:24:57:84")
```