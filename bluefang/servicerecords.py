# -*- coding: utf-8 -*-

def hid_description() -> str:
    """
    The HID descriptor that is exposed via our SDP record.  We support both Keyboard and Consumer Control reports.

    TODO: Fast forward and Rewind are not working on Apple TV
    TODO: All consumer control reports are not working on PS3

    HID Descriptor parser: http://eleccelerator.com/usbdescreqparser/
    Apple Keyboard HID Descriptor: http://www.avernus.com/~gadams/hardware/keyboard/apple-built-in-keyboard-usb-probe.txt
    PS2/3/4 HID Descriptor: https://github.com/torvalds/linux/blob/master/drivers/hid/hid-sony.c
    """
    descriptor_bytes = [
        0x05, 0x01,        # Usage Page (Generic Desktop Ctrls)
        0x09, 0x06,        # Usage (Keyboard)
        0xA1, 0x01,        # Collection (Application)
        0x85, 0x01,        #   Report ID (1)
        0x75, 0x01,        #   Report Size (1)
        0x95, 0x08,        #   Report Count (8)
        0x05, 0x07,        #   Usage Page (Kbrd/Keypad)
        0x19, 0xE0,        #   Usage Minimum (0xE0)
        0x29, 0xE7,        #   Usage Maximum (0xE7)
        0x15, 0x00,        #   Logical Minimum (0)
        0x25, 0x01,        #   Logical Maximum (1)
        0x81, 0x02,        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0x95, 0x01,        #   Report Count (1)
        0x75, 0x08,        #   Report Size (8)
        0x81, 0x03,        #   Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0x95, 0x05,        #   Report Count (5)
        0x75, 0x01,        #   Report Size (1)
        0x05, 0x08,        #   Usage Page (LEDs)
        0x19, 0x01,        #   Usage Minimum (Num Lock)
        0x29, 0x05,        #   Usage Maximum (Kana)
        0x91, 0x02,        #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
        0x95, 0x01,        #   Report Count (1)
        0x75, 0x03,        #   Report Size (3)
        0x91, 0x03,        #   Output (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
        0x95, 0x06,        #   Report Count (6)
        0x75, 0x08,        #   Report Size (8)
        0x15, 0x00,        #   Logical Minimum (0)
        0x26, 0xFF, 0x00,  #   Logical Maximum (255)
        0x05, 0x07,        #   Usage Page (Kbrd/Keypad)
        0x19, 0x00,        #   Usage Minimum (0x00)
        0x29, 0xFF,        #   Usage Maximum (0xFF)
        0x81, 0x00,        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0xC0,              # End Collection
        0x05, 0x0C,        # Usage Page (Consumer)
        0x09, 0x01,        # Usage (Consumer Control)
        0xA1, 0x01,        # Collection (Application)
        0x85, 0x03,        #   Report ID (3)
        0x15, 0x00,        #   Logical Minimum (0)
        0x25, 0x01,        #   Logical Maximum (1)
        0x09, 0xB4,        #   Usage (Rewind)
        0x09, 0xB3,        #   Usage (Fast Forward)
        0x81, 0x22,        #   Input (Data,Var,Abs,No Wrap,Linear,No Preferred State,No Null Position)
        0x95, 0x02,        #   Report Count (2)
        0x75, 0x01,        #   Report Size (1)
        0x0A, 0x23, 0x02,  #   Usage (AC Home)
        0x09, 0xB8,        #   Usage (Eject)
        0x09, 0xB6,        #   Usage (Scan Previous Track)
        0x09, 0xCD,        #   Usage (Play/Pause)
        0x09, 0xB5,        #   Usage (Scan Next Track)
        0x09, 0xE2,        #   Usage (Mute)
        0x09, 0xEA,        #   Usage (Volume Decrement)
        0x09, 0xE9,        #   Usage (Volume Increment)
        0x09, 0x30,        #   Usage (Power)
        0x09, 0xB0,        #   Usage (Play)
        0x09, 0xB1,        #   Usage (Pause)
        0x81, 0x02,        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0x95, 0x01,        #   Report Count (1)
        0x75, 0x0B,        #   Report Size (11)
        0x81, 0x03,        #   Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0xC0,              # End Collection
    ]

    return "".join("{:02x}".format(i) for i in descriptor_bytes)


HID_PROFILE = """
<?xml version="1.0" encoding="UTF-8" ?>

<record>
  <attribute id="0x0001"> <!-- ServiceClassIDList -->
    <sequence>
      <uuid value="0x1124" />
    </sequence>
  </attribute>
  <attribute id="0x0004"> <!-- ProtocolDescriptorList -->
    <sequence>
      <sequence>
        <uuid value="0x0100" /> <!-- L2CAP -->
        <uint16 value="0x0011" />
      </sequence>
      <sequence>
        <uuid value="0x0011" />
      </sequence>
    </sequence>
  </attribute>
  <attribute id="0x0005"> <!-- BrowseGroupList -->
    <sequence>
      <uuid value="0x1002" />
    </sequence>
  </attribute>
  <attribute id="0x0006"> <!-- LanguageBaseAttributeIDList -->
    <sequence>
      <uint16 value="0x656e" /> <!-- en- (English) -->
      <uint16 value="0x006a" /> <!-- UTF-8 encoding -->
      <uint16 value="0x0100" /> <!-- PrimaryLanguageBaseId = 0 -->
    </sequence>
  </attribute>
  <attribute id="0x0009"> <!-- Bluetooth Profile Descriptor List -->
    <sequence>
      <sequence>
        <uuid value="0x1124" /> <!-- HID Profile -->
        <uint16 value="0x0100" /> <!-- L2CAP -->
      </sequence>
    </sequence>
  </attribute>
  <attribute id="0x000d"> <!-- AdditionalProtocolDescriptorLists -->
    <sequence>
      <sequence>
        <sequence>
          <uuid value="0x0100" /> <!-- L2CAP -->
          <uint16 value="0x0013" /> <!-- PSM for HID Interrupt -->
        </sequence>
        <sequence>
          <uuid value="0x0011" />
        </sequence>
      </sequence>
    </sequence>
  </attribute>
  <attribute id="0x0100">
    <text value="Omnihub Device" />
  </attribute>
  <attribute id="0x0101">
    <text value="Remote control proxy" />
  </attribute>
  <attribute id="0x0102">
    <text value="Omnihub" />
  </attribute>
  <attribute id="0x0200"> <!-- HIDDeviceReleaseNumber (Deprecated) -->
    <uint16 value="0x0100" />
  </attribute>
  <attribute id="0x0201"> <!-- HIDParserVersion -->
    <uint16 value="0x0111" /> 
  </attribute>
  <attribute id="0x0202"> <!-- HIDDeviceSubclass -->
    <uint8 value="0x4c" /> <!-- TODO Should be remote control 0x0b? https://www.silabs.com/documents/login/application-notes/AN1032-HID-BT.pdf -->
  </attribute>
  <attribute id="0x0203"> <!-- HIDCountryCode -->
    <uint8 value="0x00" />
  </attribute>
  <attribute id="0x0204"> <!-- HIDVirtualCable -->
    <boolean value="true" />
  </attribute>
  <attribute id="0x0205"> <!-- HIDRecoonectInitiate -->
    <boolean value="true" />
  </attribute>
  <attribute id="0x0206"> <!-- HIDDescriptorList -->
    <sequence>
      <sequence>
        <uint8 value="0x22" />
        <text encoding="hex" value="{}" />
      </sequence>
    </sequence>
  </attribute>
  <attribute id="0x0207"> <!-- HIDLANGIDBaseList -->
    <sequence>
      <sequence>
        <uint16 value="0x0409" />
        <uint16 value="0x0100" />
      </sequence>
    </sequence>
  </attribute>
  <attribute id="0x0208"> <!-- HIDSDPDisable (Deprecated) -->
    <boolean value="true" />
  </attribute>
  <attribute id="0x0209"> <!-- HIDBatteryPower -->
    <boolean value="false" />
  </attribute>
  <attribute id="0x020a"> <!-- HIDRemoteWake -->
    <boolean value="true" />
  </attribute>
  <attribute id="0x020b"> <!-- HIDProfileVersion -->
    <uint16 value="0x1124" />
  </attribute>
  <attribute id="0x020c"> <!-- HIDSupervisionTimeout -->
    <uint16 value="0x0c80" />
  </attribute>
  <attribute id="0x020d"> <!-- HIDNormallyConnectable -->
    <boolean value="false" />
  </attribute>
  <attribute id="0x020e"> <!-- HIDBootDevice -->
    <boolean value="true" />
  </attribute>
  <attribute id="0x020f"> <!-- HIDSSRHostMaxLatency -->
    <uint16 value="0x0640" />
  </attribute>
  <attribute id="0x0210"> <!-- HIDSSRHostMinTimeout -->
    <uint16 value="0x0320" />
  </attribute>
</record>
""".format(hid_description())
