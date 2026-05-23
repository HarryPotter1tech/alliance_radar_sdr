import socket
import threading
import time
from parser.gnuradio_frame_parser import (
    GnuRadioFrameParser,
    RoboMaster_Signal_Info,
    RoboMaster_Noise_Key,
)
from parser.datacenter_package_parser import DataCenterPackageParser, RadarInfo
from parser.noise_window_tracker import NoiseKeyWindowTracker


from logs.event_logger import log, log_data, log_thread_start, log_thread_stop


def _update_dataclass_inplace(target, source) -> bool:
    if source is None:
        return False
    target.__dict__.update(source.__dict__)
    return True


def tcp_gnuradio_signal_receiver(
    robomaster_signal_info: RoboMaster_Signal_Info,
    lock: threading.Lock,
    stop_event: threading.Event | None = None,
    shared_state: dict | None = None,
):
    server_address = ("127.0.0.1", 2000)
    frameparser = GnuRadioFrameParser("signal")
    _robomaster_signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    thread_name = threading.current_thread().name
    log_thread_start("event", thread_name)
    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            log("event", "Connecting to gnu radio receiver server")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcp_socket.connect(server_address)
                log("event", "Connected to gnu radio signal server")
                buffer: bytes = b""
                while True:
                    if stop_event and stop_event.is_set():
                        break
                    try:
                        chunk = tcp_socket.recv(1024)
                    except socket.error as e:
                        log(
                            "event", f"Error connecting to gnu radio signal server: {e}"
                        )
                        break
                    if not chunk:
                        log("event", "Connection closed, reconnecting...")
                        break
                    buffer += chunk
                    if len(buffer) >= 400:
                        with lock:
                            parsed = frameparser.payload_parse(buffer)
                            _update_dataclass_inplace(robomaster_signal_info, parsed)
                            if parsed is not None:
                                log_data("parsed", "signal_info", parsed)
                                if shared_state is not None:
                                    shared_state["signal_payload"] = parsed
                        if robomaster_signal_info == _robomaster_signal_info:
                            log("event", "Parsed signal data failed")
                        else:
                            log_data(
                                "parsed", "signal_info_state", robomaster_signal_info
                            )
                        buffer = b""
            except socket.error as e:
                log("event", f"Error connecting to gnu radio signal server: {e}")
            finally:
                tcp_socket.close()
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.2)
    finally:
        log_thread_stop("event", thread_name)


def tcp_gnuradio_noise_key_receiver(
    robomaster_noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
    stop_event: threading.Event | None = None,
    tracker: NoiseKeyWindowTracker | None = None,
    shared_state: dict | None = None,
):
    server_address = ("127.0.0.1", 2500)

    frameparser = GnuRadioFrameParser("noise")
    _robomaster_noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()
    thread_name = threading.current_thread().name
    log_thread_start("event", thread_name)
    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            log("event", "Connecting to gnu radio noise key server")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcp_socket.connect(server_address)
                log("event", "Connected to gnu radio noise key server")
                buffer: bytes = b""
                while True:
                    if stop_event and stop_event.is_set():
                        break
                    try:
                        chunk = tcp_socket.recv(1024)
                    except socket.error as e:
                        log(
                            "event",
                            f"Error connecting to gnu radio noise key server: {e}",
                        )
                        break
                    if not chunk:
                        log("event", "Connection closed, reconnecting...")
                        break
                    buffer += chunk
                    if len(buffer) >= 200:
                        with lock:
                            parsed = frameparser.payload_parse(buffer)
                            _update_dataclass_inplace(robomaster_noise_key, parsed)
                            if parsed is not None:
                                log_data("parsed", "noise_key", parsed)
                            if tracker:
                                key_tuple = (
                                    robomaster_noise_key.sdr_key_1,
                                    robomaster_noise_key.sdr_key_2,
                                    robomaster_noise_key.sdr_key_3,
                                    robomaster_noise_key.sdr_key_4,
                                    robomaster_noise_key.sdr_key_5,
                                    robomaster_noise_key.sdr_key_6,
                                )
                                tracked = tracker.track(key_tuple)
                                if tracked.real_key is not None:
                                    robomaster_noise_key.sdr_behavior = 2
                                    (
                                        robomaster_noise_key.sdr_key_1,
                                        robomaster_noise_key.sdr_key_2,
                                        robomaster_noise_key.sdr_key_3,
                                        robomaster_noise_key.sdr_key_4,
                                        robomaster_noise_key.sdr_key_5,
                                        robomaster_noise_key.sdr_key_6,
                                    ) = tracked.real_key
                                    if shared_state is not None:
                                        if tracked.updated:
                                            shared_state["real_key"] = tracked.real_key
                                            shared_state["real_key_history"] = (
                                                tracker.real_key_history
                                            )
                                            log_data(
                                                "parsed", "real_key", tracked.real_key
                                            )
                        if robomaster_noise_key == _robomaster_noise_key:
                            log("event", "Parsed noise key data failed")
                        buffer = b""
            except socket.error as e:
                log("event", f"Error connecting to gnu radio noise key server: {e}")
            finally:
                tcp_socket.close()
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.2)
    finally:
        log_thread_stop("event", thread_name)


def tcp_datacenter_receiver(
    radar_info: RadarInfo,
    lock: threading.Lock,
    shared_state: dict | None = None,
):
    log_thread_start("event", threading.current_thread().name)
    try:
        log("event", "Initializing parser client")
        server_address = ("127.0.0.1", 1500)
        packageparser = DataCenterPackageParser()
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                try:
                    tcp_socket.connect(server_address)
                    log("event", "Connected to datacenter server")
                    buffer: bytes = b""
                    while True:
                        try:
                            chunk = tcp_socket.recv(1024)
                        except socket.error as e:
                            log("event", f"Error receiving data, reconnecting: {e}")
                            break
                        if not chunk:
                            log("event", "Connection closed, reconnecting...")
                            break
                        buffer += chunk
                        if len(buffer) >= 4:
                            with lock:
                                parsed = packageparser.package_parse(buffer)
                                _update_dataclass_inplace(radar_info, parsed)
                                if parsed is not None:
                                    log_data("parsed", "radar_info", parsed)
                                if shared_state is not None:
                                    rank = radar_info.radar_message_auto_decision_synchronization.EncryptionRank
                                    if shared_state.get("rank") != rank:
                                        shared_state["rank"] = rank
                                        if rank <= 1:
                                            shared_state["noise_grade"] = "noise_1"
                                        elif rank == 2:
                                            shared_state["noise_grade"] = "noise_2"
                                        else:
                                            shared_state["noise_grade"] = "noise_3"
                                        log_data(
                                            "event",
                                            "rank_update",
                                            {
                                                "rank": rank,
                                                "noise_grade": shared_state[
                                                    "noise_grade"
                                                ],
                                            },
                                        )
                            if parsed is not None:
                                raw_hex = buffer[:4].hex(" ")
                                rank = radar_info.radar_message_auto_decision_synchronization.EncryptionRank
                                is_modify = radar_info.radar_message_auto_decision_synchronization.IsModifierKeyAble
                                log_data(
                                    "unity_rx",
                                    "received_package",
                                    {
                                        "raw_hex": raw_hex,
                                        "rank": rank,
                                        "modify_key": int(is_modify),
                                        "radar_info": radar_info,
                                    },
                                    tag="[unity]",
                                )
                                log_data("parsed", "radar_info_state", radar_info)
                                buffer = b""
                except socket.error as e:
                    log("event", f"Error to initialize parser client: {e}")
            time.sleep(0.2)
    finally:
        log_thread_stop("event", threading.current_thread().name)


def tcp_datacenter_transmitter(
    signal_info: RoboMaster_Signal_Info,
    noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
):
    log_thread_start("event", threading.current_thread().name)
    try:
        log("event", "Initializing parser server")
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ("127.0.0.1", 1400)
        while True:
            try:
                tcp_socket.bind(server_address)
                log(
                    "event",
                    "Initialized parser server, waiting for unity client to connect",
                )
                break
            except socket.error as e:
                log("event", f"Error to initialize parser server: {e}")

        # this loop tries to bind a port until success, then wait for unity
        # client to connect; once connected, send data to unity client; if
        # connection is closed or error occurs, close the connection and
        # wait for next connection.
        while True:
            tcp_socket.listen(1)
            connection, client_address = tcp_socket.accept()
            log("event", f"Unity client connected: {client_address}")
            try:
                while True:
                    with lock:
                        data: bytes = (
                            0x0A06.to_bytes(2, byteorder="big")
                            + noise_key.sdr_behavior.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_1.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_2.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_3.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_4.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_5.to_bytes(1, byteorder="little")
                            + noise_key.sdr_key_6.to_bytes(1, byteorder="little")
                            + 0x0A07.to_bytes(2, byteorder="big")
                            + signal_info.hero_position[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.hero_position[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.engineer_position[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.engineer_position[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.infentry_position_1[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.infentry_position_1[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.infentry_position_2[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.infentry_position_2[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.drone_position[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.drone_position[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.sentinel_position[0].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.sentinel_position[1].to_bytes(
                                2, byteorder="little"
                            )
                            + signal_info.hero_blood.to_bytes(2, "little")
                            + signal_info.engineer_blood.to_bytes(2, "little")
                            + signal_info.infentry_blood_1.to_bytes(2, "little")
                            + signal_info.infentry_blood_2.to_bytes(2, "little")
                            + signal_info.sentinel_blood.to_bytes(2, "little")
                            + signal_info.econmic_remain.to_bytes(2, "little")
                        )
                    log_data("parsed", "noise_key_state", noise_key)
                    log_data("parsed", "signal_info_state", signal_info)
                    log("event", f"Data length: {len(data)}")
                    connection.sendall(data)
                    log_data("unity_tx", "sent_packet", data)
                    time.sleep(0.1)
            except socket.error as e:
                log("event", f"Error sending data to unity client: {e}")
            finally:
                connection.close()
            # loop continues to accept next client
    finally:
        log_thread_stop("event", threading.current_thread().name)
