import sys
import bluetooth # type: ignore
from bluetooth import *
import dbus # type: ignore
import dbus.service # type: ignore
import logging
from typing import Any


class Profile(dbus.service.Object):
    fd = -1

    # dbus decorated methods can't have type annotations. See https://github.com/smurfix/flask-script/issues/169
    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        logging.info("Release")
        #mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        logging.info("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        logging.info("in new connection")
        self.fd = fd.take()
        logging.info("NewConnection(%s, %d)" % (path, self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                logging.info(" %s = 0x%04x" % (key, properties[key]))
            else:
                logging.info(" %s = %s" % (key, properties[key]))

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnect(self, path):
        logging.info("RequestDisconnection(%s)" % (path))

        if(self.fd > 0):
            #os.close(self.fd)
            self.fd = -1
