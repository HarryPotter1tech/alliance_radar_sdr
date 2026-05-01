import socket
from frame_parser.frame_parser import (
    FrameParser,
    RoboMaster_Signal_Info,
    RoboMaster_Noise_Key,
)


def tcp_gnuradio_signal_receiver():
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
                    RoboMaster_signal_info = frameparser.payload_parse(buffer)
                    print(
                        "Parse message package complete, RoboMaster_signal_info: ",
                        RoboMaster_signal_info,
                    )
                    buffer = b""
        except socket.error as e:
            print("Error connecting to gnu radio receiver server: ", e)
        finally:
            tcp_socket.close()


def tcp_gnuradio_noise_key_receiver():
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
                    robomaster_noise_key = frameparser.payload_parse(buffer)
                    print(
                        "Parse message package complete, robomaster_noise_key: ",
                        robomaster_noise_key,
                    )
                    buffer = b""
        except socket.error as e:
            print("Error connecting to gnu radio receiver server: ", e)
        finally:
            tcp_socket.close()


def tcp_datacenter_transmitter(
    signal_info: RoboMaster_Signal_Info, noise_key: RoboMaster_Noise_Key
):
    print("Initializing sdr server…")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("192.168.1.10", 4000)
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


def tcp_datacenter_receiver():
    print("Initializing sdr server…")
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("192.168.1.10", 4000)
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
        except socket.error as e:
            print("Error to initialize sdr server: ", e)
