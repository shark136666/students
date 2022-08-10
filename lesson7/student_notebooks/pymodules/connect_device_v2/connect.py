import socket

import pyvisa as visa


class Device:
    producer: str = 'None'
    model: str = 'None'
    serial_number: str = 'None'
    version: str = 'None'
    connection: visa.ResourceManager

    def __init__(self, producer, model, serial_number, version, connection):
        self.producer = producer
        self.model = model
        self.serial_number = serial_number
        self.version = version
        self.connection = connection


def find_device() -> list():
    port_range = [5020, 5039]
    host = socket.gethostname()
    device_dict = {}
    for port in range(port_range[0], port_range[1]):

        try:
            device = connect_to_device(host, port)
            device_dict[f'{device.model}:{device.serial_number}'] = device


        except:
            continue
    return device_dict


def connect_to_device(addr, port):
    open_timeout = 10
    rm = visa.ResourceManager('@py')
    try:
        connection = rm.open_resource(f'TCPIP0::{addr}::{port}::SOCKET', open_timeout=open_timeout)
        connection.write_termination = '\n'
        connection.read_termination = '\n'
        connection.timeout = 5000
        reddy = int(connection.query("SYSTem:READy?"))

        if reddy == 1:
            device = device_identification(connection)
            return device
    except:
        pass


def device_identification(connection):
    device_info = connection.query("*IDN?")
    device_info = device_info.split(',')
    device = Device(producer=device_info[0],
                    model=device_info[1],
                    serial_number=device_info[2],
                    version=device_info[2],
                    connection=connection)
    # producer, model, serial_number, version = device_info.split(',')
    # return producer, model, serial_number, version, connection
    return device


