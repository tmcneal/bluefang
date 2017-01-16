# -*- coding: utf-8 -*-

class Bluetooth():
    def __init__(self):
        pass
    
    def connect(self, blah):
        print("CONNECT %s" % blah)

    def disconnect(self, blah):
        print("DISCONNECT %s" % blah)

    def registerProfile(self, blah, blah2):
        print("REGISTER %s %s" % (blah, blah2))
    
    def unregisterProfile(self, blah):
        print("UNREGISTER %s" % blah)
    
    def sendHIDMessage(self, msg):
        print("SEND MESSAGE %s" % msg)
    
    def isConnectionEstablished(self):
        print("Connection established?")
        return True
