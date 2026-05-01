import socket
import threading
from parser.gnuradio_frame_parser import (
    FrameParser,
    RoboMaster_Signal_Info,
    RoboMaster_Noise_Key,
)
from parser.datacenter_package_parser import PackageParser, RadarMarkProcess


def _update_dataclass_inplace(target, source) -> bool:
    if source is None:
        return False
    target.__dict__.update(source.__dict__)
    return True


def tcp_gnuradio_signal_receiver(
    robomaster_signal_info: RoboMaster_Signal_Info, lock: threading.Lock
):
    server_address = ("127.0.0.1", 2000)
    frameparser = FrameParser()
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
                    print("Received data: ", buffer)
                    with lock:
                        parsed = frameparser.payload_parse(buffer)
                        _update_dataclass_inplace(robomaster_signal_info, parsed)
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
    server_address = ("127.0.0.1", 3000)
    frameparser = FrameParser()
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
                    print("Received data: ", buffer)
                    with lock:
                        parsed = frameparser.payload_parse(buffer)
                        _update_dataclass_inplace(robomaster_noise_key, parsed)
                        # if parsed is None _update_dataclass_inplace will return False and robomaster_noise_key will not be updated
                        # if parsed is not None, robomaster_noise_key will be updated and the new value will be printed
                        # so this can maintain the old value of robomaster_noise_key when the new data is invalid, and only update it when the new data is valid
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
    server_address = ("192.168.1.10", 2000)
    packageparser = PackageParser()
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
                if len(buffer) >= 100:
                    print("Received data: ", buffer)
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
    server_address = ("192.168.1.10", 3000)
    while True:
        try:
            tcp_socket.bind(server_address)
            print("Initialized sdr server, waiting for unity client to connect…")
            break
        except socket.error as e:
            print("Error to initialize sdr server: ", e)
    while True:
        tcp_socket.listen(1)
        connection, client_address = tcp_socket.accept()
        print("Unity client connected: ", client_address)
        try:
            with lock:
                signal_info_data: bytes = signal_info.to_bytes(102, byteorder="big")
                noise_key_data: bytes = noise_key.to_bytes(7, byteorder="big")
            data = signal_info_data + noise_key_data
            print("Sending data to unity client: ", data)
            print("Data length: ", len(data))
            connection.sendall(data)
            print("Sent data to unity client: ", data)
        except socket.error as e:
            print("Error sending data to unity client: ", e)
        finally:
            connection.close()
