import argparse
import signal
import socket
import threading
import time
from control.gnuradio_control import GnuradioController
from parser.gnuradio_frame_parser import RoboMaster_Noise_Key, RoboMaster_Signal_Info
from comm.tcp.tcp_comm import tcp_gnuradio_frame_receiver
from comm.zmq.zmq_pub import zmq_start_pub
from comm.zmq.zmq_sub import zmq_start_sub
from shared_state import init_shared_state
from logs.event_logger import log


SIDE_SIGNAL_FREQUENCY = {
    "red": 433200000,
    "blue": 433920000,
}


def _wait_for_port(host: str, port: int, timeout_sec: float) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                log("event", f"Port ready: {host}:{port}")
                return
            except OSError:
                time.sleep(0.2)
    log("event", f"Port not ready: {host}:{port}")


def _parse_args() -> str:
    """Parse our side (red/blue). The SDR receives the wave source placed
    at our own radar base, which carries the opponent's data (rulebook 5.6).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", default="red", help="我方阵营: red / blue")
    parser.add_argument(
        "--enemySide",
        dest="side",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    side = str(args.side).strip().lower()
    if side not in SIDE_SIGNAL_FREQUENCY:
        log("event", f"Invalid --side {side!r}, fallback to red")
        side = "red"
    log("event", f"Parsed --side {side}")
    return side


def _run_status_window(controller: GnuradioController) -> None:
    """Show the SDR status window on the main thread and run the Qt loop.

    Closing the window only hides it; the receiver keeps running. Exit
    via the 退出 button, Ctrl+C or SIGTERM.
    """
    from PyQt5 import Qt

    from control.sdr_status_window import SdrStatusWindow

    qapp = Qt.QApplication([])
    window = SdrStatusWindow()
    window.show()
    log("event", "Status window shown")

    interrupted = False

    def on_signal(signum, frame) -> None:
        nonlocal interrupted
        interrupted = True

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    def poll_status() -> None:
        nonlocal interrupted
        if interrupted:
            qapp.quit()
            return
        while not controller.status_queue.empty():
            window.update_status(controller.status_queue.get_nowait())
        window.update_config(controller.current_config())

    timer = Qt.QTimer()
    timer.timeout.connect(poll_status)
    timer.start(200)

    qapp.exec_()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    controller.stop()
    log("event", "Shutdown complete")


def main() -> None:
    side = _parse_args()
    signal_frequency = SIDE_SIGNAL_FREQUENCY[side]
    log(
        "event",
        f"SDR startup: side={side}, 接收 {side} 方基座波源 {signal_frequency / 1e6:.3f} MHz",
    )
    signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()

    shared_state = init_shared_state(side, signal_frequency)
    lock = threading.Lock()
    signal_stop = threading.Event()
    noise_stop = threading.Event()

    gnuradio_controller = GnuradioController(shared_state, lock)
    gnuradio_controller.start()

    _wait_for_port("127.0.0.1", 2500, 1.0)

    frame_receiver_thread = threading.Thread(
        target=tcp_gnuradio_frame_receiver,
        args=(signal_info, noise_key, lock, shared_state, noise_stop),
        daemon=True,
    )
    frame_receiver_thread.start()
    log("event", f"Thread started: {frame_receiver_thread.name}")

    zmq_pub_thread = threading.Thread(
        target=zmq_start_pub,
        args=(signal_info, noise_key, lock, shared_state),
        daemon=True,
    )
    zmq_pub_thread.start()
    log("event", f"Thread started: {zmq_pub_thread.name}")

    zmq_sub_thread = threading.Thread(
        target=zmq_start_sub,
        args=(shared_state, lock),
        daemon=True,
    )
    zmq_sub_thread.start()
    log("event", f"Thread started: {zmq_sub_thread.name}")

    # All worker threads started; only now bring up the status window.
    log("event", "All threads started")
    try:
        _run_status_window(gnuradio_controller)
    except Exception as exc:
        # Headless fallback: no display available, wait for Ctrl+C.
        log("event", f"Status window unavailable ({exc!r}), running headless")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        gnuradio_controller.stop()
        log("event", "Shutdown complete")


if __name__ == "__main__":
    main()
