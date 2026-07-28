import socket
import threading
import time
from parser.gnuradio_frame_parser import GnuRadioFrameParser, RoboMaster_Noise_Key

from logs.event_logger import log, log_data, log_thread_start, log_thread_stop


def _update_dataclass_inplace(target, source) -> bool:
    if source is None:
        return False
    target.__dict__.update(source.__dict__)
    return True


def tcp_gnuradio_noise_key_receiver(
    robomaster_noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
    stop_event: threading.Event | None = None,
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
                            if parsed is not None:
                                _update_dataclass_inplace(robomaster_noise_key, parsed)
                                log_data("parsed", "noise_key", parsed)
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


