import argparse
import socket
import threading
import time
from control.gnuradio_control import GnuradioController
from parser.datacenter_package_parser import RadarInfo
from parser.gnuradio_frame_parser import RoboMaster_Noise_Key, RoboMaster_Signal_Info
from parser.noise_window_tracker import NoiseKeyWindowTracker
from tcp.tcp_comm import (
    tcp_datacenter_receiver,
    tcp_datacenter_transmitter,
    tcp_gnuradio_noise_key_receiver,
)


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


def main() -> None:
    enemy_side = _parse_args()
    signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()
    radar_info: RadarInfo = RadarInfo()

    shared_state = {
        "noise_grade": "noise_1",
        "signal_frequency": ENEMY_SIDE_SIGNAL_FREQUENCY[enemy_side],
        "enemy_side": enemy_side,
        "rank": 1,
        "real_key": None,
        "real_key_history": [],
        "signal_payload": None,
    }
    lock = threading.Lock()
    signal_stop = threading.Event()
    noise_stop = threading.Event()

    gnuradio_controller = GnuradioController(shared_state, lock)
    gnuradio_controller.start()

    # Only wait for noise key server in noise-only mode
    _wait_for_port("127.0.0.1", 2500, 1.0)

    noise_key_thread = threading.Thread(
        target=tcp_gnuradio_noise_key_receiver,
        args=(
            noise_key,
            lock,
            noise_stop,
            NoiseKeyWindowTracker(window_size=20),
            shared_state,
        ),
        daemon=True,
    )
    transmitter_thread = threading.Thread(
        target=tcp_datacenter_transmitter,
        args=(signal_info, noise_key, lock),
        daemon=True,
    )
    receiver_thread = threading.Thread(
        target=tcp_datacenter_receiver,
        args=(radar_info, lock, shared_state),
        daemon=True,
    )
    noise_key_thread.start()
    transmitter_thread.start()
    receiver_thread.start()

    noise_key_thread.join()
    transmitter_thread.join()
    receiver_thread.join()


if __name__ == "__main__":
    main()
