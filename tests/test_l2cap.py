from mock import MagicMock
from bluefang import l2cap
import socket


def test_l2cap_client():
    mock_socket = MagicMock(name='socket', spec=socket.socket)
    worker = l2cap.L2CAPClientThread(mock_socket, 'bogus_address')

    worker.process_command("left")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("right")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x4F, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("up")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x52, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("down")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x51, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("enter")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("cancel")
    mock_socket.send.assert_any_call(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x29, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.send.assert_called_with(bytes(bytearray((0xA1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))))
    mock_socket.reset_mock()

    worker.process_command("blah")
    mock_socket.assert_not_called()

def test_l2cap_server():
    mock_socket = MagicMock(name='socket', spec=socket.socket)
    worker = l2cap.L2CAPServerThread(mock_socket, 'bogus_address')

    worker.process([0x71])
    mock_socket.send.assert_any_call(chr(0x00))
    mock_socket.send.assert_called_with(chr(0xA1) + chr(0x04))
    mock_socket.reset_mock()

    worker.process([0x77]) # meaningless byte
    mock_socket.assert_not_called()
