#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZMQ PUB noise-key filtering test (mode-driven).

Verifies:
  1. is_valid_ascii_alnum_key: ASCII letters/digits only
  2. noise mode + valid key   -> publishes
  3. noise mode + invalid key -> skips publish (nothing sent)
  4. persistently invalid key -> keeps skipping
  5. signal mode              -> no key filter (publishes regardless)
  6. game_progress != 4 gate still holds

Run: PYTHONPATH=. python3 tests/test_zmq_pub_filter.py
"""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import zmq  # noqa: E402

from comm.zmq.zmq_pub import (  # noqa: E402
    is_valid_ascii_alnum_key,
    zmq_start_pub,
)
from parser.gnuradio_frame_parser import (  # noqa: E402
    RoboMaster_Noise_Key,
    RoboMaster_Signal_Info,
)
from shared_state import init_shared_state  # noqa: E402

TEST_PORT = 5665


def _set_key(noise_key, key_bytes: bytes):
    for idx, byte in enumerate(key_bytes):
        setattr(noise_key, f"sdr_key_{idx + 1}", byte)


def main() -> int:
    ok = True

    # --- 1. unit: key validator ---
    cases = [
        (b"Ab3xY9", True),
        (b"123456", True),
        (b"zzZZ99", True),
        (b"\x00\xffA1B2", False),
        (b"A:B2CD", False),
        (b"\xe4\xb8\xadABC", False),
    ]
    for key, expected in cases:
        got = is_valid_ascii_alnum_key(list(key))
        passed = got == expected
        ok = ok and passed
        print(f"{'PASS' if passed else 'FAIL'} | is_valid_ascii_alnum_key({key!r})={got}")

    # --- integration ---
    shared_state = init_shared_state("red", 433200000)
    shared_state["game_progress"] = 4
    shared_state["mode"] = "noise"
    signal_info = RoboMaster_Signal_Info()
    noise_key = RoboMaster_Noise_Key()
    lock = threading.Lock()
    stop = threading.Event()

    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect(f"tcp://127.0.0.1:{TEST_PORT}")
    sub.setsockopt(zmq.RCVTIMEO, 250)
    sub.subscribe(b"")
    time.sleep(0.3)  # slow joiner: connect before the publisher binds

    pub_thread = threading.Thread(
        target=zmq_start_pub,
        args=(signal_info, noise_key, lock, shared_state, stop),
        kwargs={"pub_addr": f"tcp://*:{TEST_PORT}"},
        daemon=True,
    )
    pub_thread.start()
    time.sleep(0.3)

    def drain(seconds: float) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            try:
                sub.recv_json()
            except zmq.Again:
                pass

    def recv_window(seconds: float) -> list:
        deadline = time.time() + seconds
        got = []
        while time.time() < deadline:
            try:
                got.append(sub.recv_json())
            except zmq.Again:
                pass
        return got

    # --- 2. noise + valid key -> publishes ---
    drain(0.2)
    with lock:
        _set_key(noise_key, b"Ab3xY9")
    msgs = recv_window(0.8)
    valid_sent = len(msgs) >= 1 and msgs[0]["key"]["key"] == [ord(c) for c in "Ab3xY9"]
    ok = ok and valid_sent
    print(f"{'PASS' if valid_sent else 'FAIL'} | noise + valid key published ({len(msgs)} msgs)")

    # --- 3. noise + invalid key -> nothing sent ---
    drain(0.2)
    with lock:
        _set_key(noise_key, b"\x00\xffA1B2")
    msgs = recv_window(0.8)
    invalid_skipped = len(msgs) == 0
    ok = ok and invalid_skipped
    print(f"{'PASS' if invalid_skipped else 'FAIL'} | noise + invalid key skipped ({len(msgs)} msgs)")

    # --- 4. persistently invalid -> keeps skipping ---
    drain(0.2)
    msgs = recv_window(1.2)
    persistent_skipped = len(msgs) == 0
    ok = ok and persistent_skipped
    print(f"{'PASS' if persistent_skipped else 'FAIL'} | persistent invalid key keeps skipping ({len(msgs)} msgs)")

    # --- 5. signal mode -> no key filter ---
    drain(0.2)
    with lock:
        shared_state["mode"] = "signal"
    msgs = recv_window(0.8)
    signal_no_filter = len(msgs) >= 1
    ok = ok and signal_no_filter
    print(f"{'PASS' if signal_no_filter else 'FAIL'} | signal mode publishes regardless of key ({len(msgs)} msgs)")

    # --- 6. game_progress gate still holds ---
    drain(0.2)
    with lock:
        shared_state["game_progress"] = 0
    msgs = recv_window(0.8)
    gate_ok = len(msgs) == 0
    ok = ok and gate_ok
    print(f"{'PASS' if gate_ok else 'FAIL'} | game_progress!=4 gate holds ({len(msgs)} msgs)")

    stop.set()
    pub_thread.join(timeout=2)
    sub.close()
    ctx.term()

    print("ALL PASS - zmq key filtering works" if ok else "HAS FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
