# -*- coding: utf-8 -*-

import dbus
import dbusmock
import bluefang
import subprocess
import pytest

adapter_name = 'hci0'
system_name = 'my-device'
address = '11:22:33:44:55:66'
alias = 'My Device'


class ClientDBusTestCase(dbusmock.DBusTestCase):

    @classmethod
    def setUpClass(klass):
        klass.start_system_bus()
        klass.dbus_con = klass.get_dbus(True)
        (klass.p_mock, klass.obj_bluez) = klass.spawn_server_template('bluez5', {}, stdout=subprocess.PIPE)

    def setUp(self):
        try:
            self.obj_bluez.Reset()
        except:
            pass # fuggedaboutit
        self.dbusmock = dbus.Interface(self.obj_bluez, dbusmock.MOCK_IFACE)
        self.dbusmock_bluez = dbus.Interface(self.obj_bluez, 'org.bluez.Mock')

    def test_info_without_device(self):
        with pytest.raises(Exception) as e:
            connection = bluefang.Bluefang()
            connection.info()

        assert str(e.value) == 'Unable to find Bluetooth device'

    def test_info(self):

        self.dbusmock_bluez.AddAdapter(adapter_name, system_name)
        self.dbusmock_bluez.AddDevice(adapter_name, address, alias)

        connection = bluefang.Bluefang()
        adapter = connection.info()

        assert(adapter['Name'] == system_name)
        assert(adapter['Discoverable'])
        assert(adapter['Class'] == 268)

    def test_scan_without_adapter_or_device(self):
        with pytest.raises(dbus.exceptions.DBusException) as e:
            connection = bluefang.Bluefang()
            connection.scan(timeout_in_ms=1)

        err_msg = 'Method "StartDiscovery" with signature "" on interface "org.bluez.Adapter1" doesn\'t exist'
        assert err_msg in str(e.value)

    def test_scan_without_device(self):
        self.dbusmock_bluez.AddAdapter(adapter_name, system_name)

        connection = bluefang.Bluefang()
        devices = connection.scan(timeout_in_ms=1)

        assert(len(devices) == 0)

    def test_scan(self):

        adapter_name = 'hci0'
        address = '11:22:33:44:55:66'
        alias = 'My Device'

        self.dbusmock_bluez.AddAdapter(adapter_name, system_name)
        self.dbusmock_bluez.AddDevice(adapter_name, address, alias)

        connection = bluefang.Bluefang()
        devices = connection.scan(timeout_in_ms=1)

        assert(len(devices) == 1)
        assert(devices == [
            bluefang.BluetoothDevice(
                name=alias,
                alias=alias,
                address=address,
                bluetooth_class='Unknown',
                is_connected=False,
                is_paired=False,
                path='/org/bluez/%s/dev_%s' % (adapter_name, address.replace(":", "_"))
            )
        ])

    def test_connect_to_unconnected_device(self):
        with pytest.raises(Exception) as e:
            connection = bluefang.Bluefang()
            connection.connect('0E:0E:0E:0E:0E')

        assert str(e.value) == "Unable to find device 0E:0E:0E:0E:0E. Try scanning first."

    def test_trust_device(self):
        adapter_name = 'hci9'
        address = '55:22:33:44:66:77'
        alias = 'My Device'

        self.dbusmock_bluez.AddAdapter(adapter_name, system_name)
        self.dbusmock_bluez.AddDevice(adapter_name, address, alias)

        connection = bluefang.Bluefang()

        connection.agent.trust_device('/org/bluez/hci9/dev_55_22_33_44_66_77')

        adapter = dbus.Interface(dbus.SystemBus().get_object("org.bluez", '/org/bluez/hci9/dev_55_22_33_44_66_77'), "org.freedesktop.DBus.Properties")
        assert(adapter.Get("org.bluez.Device1", "Trusted") == True)

    def test_agent_without_adapter(self):
        connection = bluefang.Bluefang()

        with pytest.raises(Exception) as e:
            connection.agent.start()
            try:
                connection.pair(timeout_in_ms=1)
            finally:
                connection.agent.stop()

    def test_agent(self):
        connection = bluefang.Bluefang()
        connection.agent.start()

        adapter_name = 'hci0'
        self.dbusmock_bluez.AddAdapter(adapter_name, system_name)

        connection.pair(timeout_in_ms=1)
        connection.agent.stop()
        
        adapter = dbus.Interface(dbus.SystemBus().get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")
        assert(adapter.Get("org.bluez.Adapter1", "Discoverable") == True)


    def test_register_profile_invalid_path(self):
        with pytest.raises(ValueError) as e:
            connection = bluefang.Bluefang()
            connection.register_profile('somepath')

        err_msg = "Invalid object path 'somepath': does not start with '/'"
        assert err_msg in str(e.value)
