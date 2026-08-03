import socket
import threading
import time
from parser.gnuradio_frame_parser import (
    GnuRadioFrameParser,
    RoboMaster_Noise_Key,
    RoboMaster_Signal_Info,
)

from logs.event_logger import log, log_data, log_thread_start, log_thread_stop


def _update_dataclass_inplace(target, source) -> bool:
    if source is None:
        return False
    target.__dict__.update(source.__dict__)
    return True


def tcp_gnuradio_frame_receiver(
    signal_info: RoboMaster_Signal_Info,
    noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
    shared_state: dict,
    stop_event: threading.Event | None = None,
    server_address: tuple[str, int] = ("127.0.0.1", 2500),
):
    """Receive and parse the GNU Radio packet stream on the TCP sink port.

    The flowgraph outputs one frame family at a time depending on its
    mode (early game noise 0x0A06, later signal 0x0A01..0x0A05). The
    parser mode follows shared_state["mode"] published by the controller,
    so parsing stays stage-driven and never misparses the other family.
    """
    frameparser = GnuRadioFrameParser("noise")
    thread_name = threading.current_thread().name
    log_thread_start("event", thread_name)
    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            log("event", f"Connecting to gnu radio frame server {server_address[0]}:{server_address[1]}")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcp_socket.connect(server_address)
                log("event", "Connected to gnu radio frame server")
                buffer: bytes = b""
                while True:
                    if stop_event and stop_event.is_set():
                        break
                    try:
                        chunk = tcp_socket.recv(1024)
                    except socket.error as e:
                        log(
                            "event",
                            f"Error connecting to gnu radio frame server: {e}",
                        )
                        break
                    if not chunk:
                        log("event", "Connection closed, reconnecting...")
                        break
                    buffer += chunk
                    if len(buffer) >= 200:
                        with lock:
                            mode = shared_state.get("mode", "noise")
                            if frameparser.receive_mode != mode:
                                frameparser.receive_mode = mode
                                log("event", f"Frame parser switched to {mode} mode")
                            parsed = frameparser.payload_parse(buffer)
                            if isinstance(parsed, RoboMaster_Signal_Info):
                                if signal_info == parsed:
                                    log("event", "Parsed signal data unchanged")
                                _update_dataclass_inplace(signal_info, parsed)
                                log_data("parsed", "signal_info", parsed)
                            elif isinstance(parsed, RoboMaster_Noise_Key):
                                if noise_key == parsed:
                                    log("event", "Parsed noise key data unchanged")
                                _update_dataclass_inplace(noise_key, parsed)
                                log_data("parsed", "noise_key", parsed)
                        buffer = b""
            except socket.error as e:
                log("event", f"Error connecting to gnu radio frame server: {e}")
            finally:
                tcp_socket.close()
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.2)
    finally:
        log_thread_stop("event", thread_name)
