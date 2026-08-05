import socket
import threading
import time
from parser.gnuradio_frame_parser import (
    GnuRadioFrameParser,
    RoboMaster_Noise_Key,
    RoboMaster_Signal_Info,
)

from logs.event_logger import (
    log,
    log_data,
    log_rate_limited,
    log_thread_start,
    log_thread_stop,
)


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
    connect_attempt = 0
    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            connect_attempt += 1
            log_rate_limited(
                "event",
                f"connect attempt #{connect_attempt} to {server_address[0]}:{server_address[1]}",
                interval_sec=5.0,
                key="connect_attempt",
            )
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                tcp_socket.connect(server_address)
                log(
                    "event",
                    f"Connected to gnu radio frame server after {connect_attempt} attempts",
                )
                connect_attempt = 0
                buffer: bytes = b""
                while True:
                    if stop_event and stop_event.is_set():
                        break
                    try:
                        chunk = tcp_socket.recv(1024)
                    except socket.error as e:
                        log_rate_limited(
                            "event",
                            f"Error connecting to gnu radio frame server: {e}",
                            interval_sec=5.0,
                        )
                        break
                    if not chunk:
                        log("event", "Connection closed, reconnecting...")
                        break
                    buffer += chunk
                    if len(buffer) >= 400:
                        with lock:
                            mode = shared_state.get("mode", "noise")
                            if frameparser.receive_mode != mode:
                                frameparser.receive_mode = mode
                                log("event", f"Frame parser switched to {mode} mode")
                            parsed = frameparser.payload_parse(buffer)
                            if isinstance(parsed, RoboMaster_Signal_Info):
                                changed = not (signal_info == parsed)
                                _update_dataclass_inplace(signal_info, parsed)
                                if changed:
                                    log_data(
                                        "parsed",
                                        f"signal_info (mode={mode})",
                                        parsed,
                                    )
                            elif isinstance(parsed, RoboMaster_Noise_Key):
                                changed = not (noise_key == parsed)
                                _update_dataclass_inplace(noise_key, parsed)
                                if changed:
                                    log_data(
                                        "parsed",
                                        f"noise_key (mode={mode})",
                                        parsed,
                                    )
                        buffer = b""
            except socket.error as e:
                log_rate_limited(
                    "event",
                    f"Error connecting to gnu radio frame server: {e}",
                    interval_sec=5.0,
                )
            finally:
                tcp_socket.close()
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.2)
    finally:
        log_thread_stop("event", thread_name)
