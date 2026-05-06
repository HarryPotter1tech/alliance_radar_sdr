import socket
import threading
import time
from parser.gnuradio_frame_parser import (
    GnuRadioFrameParser,
    RoboMaster_Signal_Info,
    RoboMaster_Noise_Key,
)
from parser.datacenter_package_parser import DataCenterPackageParser, RadarMarkProcess


def _update_dataclass_inplace(target, source) -> bool:
    if source is None:
        return False
    target.__dict__.update(source.__dict__)
    return True


def tcp_gnuradio_signal_receiver(
    robomaster_signal_info: RoboMaster_Signal_Info, lock: threading.Lock
):
    server_address = ("127.0.0.1", 2000)
    frameparser = GnuRadioFrameParser("signal")
    _robomaster_signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    while True:
        print("Connecting to gnu radio receiver server…")
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_socket.connect(server_address)
            print("Connected to gnu radio receiver server.")
            buffer: bytes = b""
            while True:
                try:
                    chunk = tcp_socket.recv(1024)
                except socket.error as e:
                    print("Error receiving data, reconnecting: ", e)
                    break
                if not chunk:
                    print("Connection closed, reconnecting...")
                    break
                buffer += chunk
                if len(buffer) >= 400:
                    with lock:
                        parsed = frameparser.payload_parse(buffer)
                        _update_dataclass_inplace(robomaster_signal_info, parsed)
                    if robomaster_signal_info == _robomaster_signal_info:
                        print("Parsed signal data failed")
                    else:
                        print(
                            "Parse message package complete, RoboMaster_signal_info: ",
                            robomaster_signal_info,
                        )
                    buffer = b""
        except socket.error as e:
            print("Error connecting to gnu radio receiver server: ", e)
        finally:
            tcp_socket.close()


def tcp_gnuradio_noise_key_receiver(
    robomaster_noise_key: RoboMaster_Noise_Key, lock: threading.Lock
):
    server_address = ("127.0.0.1", 2500)

    frameparser = GnuRadioFrameParser("noise")
    _robomaster_noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()
    while True:
        print("Connecting to gnu radio receiver server…")
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_socket.connect(server_address)
            print("Connected to gnu radio receiver server.")
            buffer: bytes = b""
            while True:
                try:
                    chunk = tcp_socket.recv(1024)
                except socket.error as e:
                    print("Error receiving data, reconnecting: ", e)
                    break
                if not chunk:
                    print("Connection closed, reconnecting...")
                    break
                buffer += chunk
                if len(buffer) >= 200:
                    with lock:
                        parsed = frameparser.payload_parse(buffer)
                        _update_dataclass_inplace(robomaster_noise_key, parsed)
                    if robomaster_noise_key == _robomaster_noise_key:
                        print("Parsed noise key data failed")
                    else:
                        print(
                            "Parse message package complete, robomaster_noise_key: ",
                            robomaster_noise_key,
                        )
                    buffer = b""
        except socket.error as e:
            print("Error connecting to gnu radio receiver server: ", e)
        finally:
            tcp_socket.close()


def tcp_datacenter_receiver(radar_mark_process: RadarMarkProcess, lock: threading.Lock):
    print("Initializing sdr server…")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("192.168.1.10", 1500)
    packageparser = DataCenterPackageParser()
    while True:
        try:
            tcp_socket.connect(server_address)
            print("Connected to sdr server.")
            buffer: bytes = b""
            while True:
                try:
                    chunk = tcp_socket.recv(1024)
                except socket.error as e:
                    print("Error receiving data, reconnecting: ", e)
                    break
                if not chunk:
                    print("Connection closed, reconnecting...")
                    break
                buffer += chunk
                if len(buffer) >= 14:
                    with lock:
                        parsed = packageparser.package_parse(buffer)
                        _update_dataclass_inplace(radar_mark_process, parsed)
                    print(
                        "Parse message package complete, RadarMarkProcess: ",
                        radar_mark_process,
                    )
                    buffer = b""
        except socket.error as e:
            print("Error to initialize sdr server: ", e)


def tcp_datacenter_transmitter(
    signal_info: RoboMaster_Signal_Info,
    noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
):
    print("Initializing sdr server…")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("192.168.1.10", 1000)
    while True:
        try:
            tcp_socket.bind(server_address)
            print("Initialized sdr server, waiting for unity client to connect…")
            break
        except socket.error as e:
            print("Error to initialize sdr server: ", e)
    # this loop try to bind a port until success, then wait for unity client to connect, once connected, send data to unity client, if connection is closed or error occurs, close the connection and wait for next connection.
    while True:
        tcp_socket.listen(1)
        connection, client_address = tcp_socket.accept()
        print("Unity client connected: ", client_address)
        try:
            with lock:
                data: bytes = (
                    0xA5.to_bytes(2, byteorder="big")
                    + signal_info.hero_position.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + signal_info.engineer_position.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + signal_info.infentry_position_1.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + signal_info.infentry_position_2.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + signal_info.drone_position.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + signal_info.sentinel_position.to_bytes(
                        4, byteorder="big", signed=True
                    )
                    + noise_key.sdr_behavior.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_1.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_2.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_3.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_4.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_5.to_bytes(1, byteorder="big")
                    + noise_key.sdr_key_6.to_bytes(1, byteorder="big")
                )
            print("Sending data to unity client: ", data)
            print("Data length: ", len(data))
            connection.sendall(data)
            print("Sent data to unity client: ", data)
            time.sleep(10)
            data = b""
        except socket.error as e:
            print("Error sending data to unity client: ", e)
        # this loop will keep transmitting data to unity client


# here I choose diffenetly designed because for gnuradio
# signal /noise key these tcp messages are more link the
# message stream through i call them package but exactly
# they are the message stream, so I design the tcp_signal
# receiver and tcp_noise_key_receiver keep connecting all
# the time and receive the message stream, then parse the
# message stream to get the signal info and noise key

# but for datacenter package, I think the tcp connection
# between unity and sdr is more like small talk,we dont
# need to transmit a lot of data ,and every package is
# independent, and closure,this is really package that not
# message stream, so I design the tcp_datacenter_receiver
# to receive and transmit package in a const frequency ,
# just like what the robomaster gameserver do,which transmit
# or receive data in 10hz,or 1hz
# but whatever the unity client or sdr client,they keep connecting
# to the relative server ,and receive data negatively.the
# right that control frenquency is deciside by server,in my
# design concept:who send data,who set rule,thats all
