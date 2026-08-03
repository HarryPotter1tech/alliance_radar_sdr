#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injection test: TCP frame receiver feeds shared dataclasses stage-dependently.

Verifies:
  1. mode=noise  -> 0x0A06 frames update noise_key, signal_info untouched
  2. mode=signal -> 0x0A01..0x0A05 frames update signal_info, noise_key untouched
  3. parser mode switch driven by shared_state["mode"]

Run: PYTHONPATH=. python3 tests/test_tcp_injection.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from comm.tcp.tcp_comm import tcp_gnuradio_frame_receiver  # noqa: E402
from parser.gnuradio_frame_parser import (  # noqa: E402
    RoboMaster_Noise_Key,
    RoboMaster_Signal_Info,
)


def make_pos_frame():
    values = [10, -20, 30, -40, 50, -60, 70, -80, 90, -100, 110, -120]
    return (0x0A01).to_bytes(2, "little") + b"".join(
        v.to_bytes(2, "big", signed=True) for v in values
    )


def make_noise_frame():
    return (0x0A06).to_bytes(2, "little") + bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])


def run_server(port: int, stop: threading.Event):
    """Send noise frames first, then signal frames, then stop."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)
    conn, _ = srv.accept()
    try:
        for _ in range(50):
            conn.sendall(make_noise_frame())
        time.sleep(0.8)
        for _ in range(50):
            conn.sendall(make_pos_frame())
        time.sleep(0.8)
    finally:
        conn.close()
        srv.close()
        stop.set()


def main() -> int:
    port = 2599
    signal_info = RoboMaster_Signal_Info()
    noise_key = RoboMaster_Noise_Key()
    shared_state = {"mode": "noise"}
    lock = threading.Lock()
    stop = threading.Event()

    server_thread = threading.Thread(target=run_server, args=(port, stop), daemon=True)
    server_thread.start()
    receiver_thread = threading.Thread(
        target=tcp_gnuradio_frame_receiver,
        args=(signal_info, noise_key, lock, shared_state, stop),
        kwargs={"server_address": ("127.0.0.1", port)},
        daemon=True,
    )
    receiver_thread.start()

    # phase 1: noise mode -> noise_key updated, signal_info untouched
    deadline = time.time() + 5
    while time.time() < deadline and noise_key.sdr_key_1 == 0:
        time.sleep(0.05)
    noise_ok = noise_key.sdr_key_1 == 0x11 and noise_key.sdr_key_6 == 0x66
    signal_untouched = signal_info.hero_position == [0, 0]
    print(f"{'PASS' if noise_ok else 'FAIL'} | noise mode injects noise_key")
    print(f"{'PASS' if signal_untouched else 'FAIL'} | signal_info untouched in noise mode")

    # phase 2: switch to signal mode; flowgraph side would publish this
    with lock:
        shared_state["mode"] = "signal"
    deadline = time.time() + 5
    while time.time() < deadline and signal_info.hero_position == [0, 0]:
        time.sleep(0.05)
    sig_ok = signal_info.hero_position == [10, -20]
    noise_kept = noise_key.sdr_key_1 == 0x11
    print(f"{'PASS' if sig_ok else 'FAIL'} | signal mode injects signal_info")
    print(f"{'PASS' if noise_kept else 'FAIL'} | noise_key kept after mode switch")

    ok = noise_ok and signal_untouched and sig_ok and noise_kept
    print("ALL PASS - stage-driven injection works" if ok else "HAS FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
