import argparse
import socket
import threading
import time
from control.gnuradio_control import GnuradioController
from parser.gnuradio_frame_parser import RoboMaster_Noise_Key, RoboMaster_Signal_Info
from tcp.tcp_comm import tcp_gnuradio_noise_key_receiver
from zmq.zmq_pub import zmq_start_pub
from zmq.zmq_sub import zmq_start_sub
from shared_state import init_shared_state


GFSK_SIGNAL_FREQUENCY = 433200000
ENEMY_SIDE_SIGNAL_FREQUENCY = {
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
                return
            except OSError:
                time.sleep(0.2)
    print(f"Port not ready: {host}:{port}")


def _parse_args() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enemySide", default="red")
    args = parser.parse_args()
    enemy_side = str(args.enemySide).strip().lower()
    if enemy_side not in ENEMY_SIDE_SIGNAL_FREQUENCY:
        enemy_side = "red"
    return enemy_side


def _run_status_window(controller: GnuradioController, exit_event: threading.Event) -> None:
    """Show the SDR status window on the main thread and run the Qt loop."""
    from PyQt5 import Qt

    from control.sdr_status_window import SdrStatusWindow

    qapp = Qt.QApplication([])
    window = SdrStatusWindow(exit_event)
    window.show()
    print("Status window shown")

    def poll_status() -> None:
        while not controller.status_queue.empty():
            window.update_status(controller.status_queue.get_nowait())

    timer = Qt.QTimer()
    timer.timeout.connect(poll_status)
    timer.start(200)

    qapp.exec_()
    controller.stop()
    print("Shutdown complete")


def main() -> None:
    enemy_side = _parse_args()
    signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()

    shared_state = init_shared_state(
        enemy_side,
        ENEMY_SIDE_SIGNAL_FREQUENCY[enemy_side],
    )
    lock = threading.Lock()
    signal_stop = threading.Event()
    noise_stop = threading.Event()

    gnuradio_controller = GnuradioController(shared_state, lock)
    gnuradio_controller.start()

    _wait_for_port("127.0.0.1", 2500, 1.0)

    noise_key_thread = threading.Thread(
        target=tcp_gnuradio_noise_key_receiver,
        args=(noise_key, lock, noise_stop),
        daemon=True,
    )
    noise_key_thread.start()

    zmq_pub_thread = threading.Thread(
        target=zmq_start_pub,
        args=(signal_info, noise_key, lock),
        daemon=True,
    )
    zmq_pub_thread.start()

    zmq_sub_thread = threading.Thread(
        target=zmq_start_sub,
        args=(shared_state, lock),
        daemon=True,
    )
    zmq_sub_thread.start()

    # All worker threads started; only now bring up the status window.
    print("All threads started")
    exit_event = threading.Event()
    try:
        _run_status_window(gnuradio_controller, exit_event)
    except Exception as exc:
        # Headless fallback: no display available, wait for shutdown signal.
        print(f"Status window unavailable ({exc!r}), running headless")
        try:
            while not exit_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        gnuradio_controller.stop()
        print("Shutdown complete")


if __name__ == "__main__":
    main()
