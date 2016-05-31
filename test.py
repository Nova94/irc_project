"""
This file is used for testing each packet separately, and ensure that each
packet gets handled properly in various simple scenarios.

"""

from time import sleep
import protocol
import socket

target_host = '0.0.0.0'
target_port = 9999


def test_packet(packet):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect((target_host, target_port))
    s.send(packet.encode())
    for response in s.makefile('r'):
        response = response.encode()
        if protocol.decode(response).status == protocol.Status.OK:
            print(protocol.decode(response).status)
        elif protocol.decode(response).status == protocol.Status.ERR:
            print(protocol.decode(response).err)
    s.close()
    sleep(1)  # sleep 1 sec before testing next packet.


def test_multiple_packets(packets):
    for packet in packets:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((target_host, target_port))
        s.send(packet.encode())
        for response in s.makefile('r'):
            response = response.encode()

            if protocol.decode(response).status == protocol.Status.OK:
                print(protocol.decode(response).status)
            elif protocol.decode(response).status == protocol.Status.ERR:
                print(protocol.decode(response).err)
        s.close()
        sleep(1)


if __name__ == '__main__':

    # test connection should be OK
    test_packet(protocol.Connect('lisa', {}))

    # test connection should be ERR
    test_packet(protocol.Connect('lisa', {}))

    # test disconnection should be OK
    test_packet(protocol.Disconnect("lisa"))

    # test disconnection should be ERR
    test_packet(protocol.Disconnect("non-existent-user"))

    # test create room should be OK
    test_packet(protocol.Create("room"))

    # test create room should be ERR
    test_packet(protocol.Create("room"))

    # test destroy room should be OK
    test_packet(protocol.Destroy("room"))

    # test destroy room should be ERR
    test_packet(protocol.Destroy("room"))
