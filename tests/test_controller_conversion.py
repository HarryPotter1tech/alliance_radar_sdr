#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single-instance conversion test for GnuradioController (mock PlutoSDR).

Verifies:
  1. rank/grade driven dynamic conversion (noise_1 -> noise_2 -> signal)
  2. rebuild failure retry with backoff (simulated device open failure)
  3. graceful shutdown via controller.stop() (no segfault on exit)

Run: PYTHONPATH=/usr/lib/python3/dist-packages:. python3 tests/test_controller_conversion.py
"""
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gnuradio import iio
from gnuradio import gr
import numpy as np


class FakePluto(gr.sync_block):
    """In-memory replacement for iio.fmcomms2_source_fc32 (no hardware)."""

    instances: list["FakePluto"] = []
    fail_next: bool = False

    def __init__(self, uri, channels, buffer_size):
        if FakePluto.fail_next:
            FakePluto.fail_next = False
            raise RuntimeError("simulated device open failure")
        gr.sync_block.__init__(
            self, name="FakePluto", in_sig=[], out_sig=[np.complex64]
        )
        self.uri = uri
        self.frequency = None
        self.calls = []
        FakePluto.instances.append(self)

    def set_len_tag_key(self, key):
        pass

    def set_frequency(self, freq):
        self.frequency = freq
        self.calls.append(("set_frequency", freq))

    def set_samplerate(self, rate):
        self.calls.append(("set_samplerate", rate))

    def set_gain_mode(self, *args):
        pass

    def set_gain(self, *args):
        pass

    def set_quadrature(self, *args):
        pass

    def set_rfdc(self, *args):
        pass

    def set_bbdc(self, *args):
        pass

    def set_filter_params(self, *args):
        pass

    def work(self, input_items, output_items):
        return 0


iio.fmcomms2_source_fc32 = FakePluto

from control.gnuradio_control import GnuradioController  # noqa: E402
from shared_state import init_shared_state, rank_to_noise_grade  # noqa: E402


def wait_for_frequency(expected_freq, timeout_sec=15.0):
    deadline = time.time() + timeout_sec
    last = None
    while time.time() < deadline:
        if FakePluto.instances:
            last = FakePluto.instances[-1].frequency
        if last == expected_freq:
            return last
        time.sleep(0.2)
    return last


def log_contains(label, since_instances=0):
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    session_dirs = sorted(
        (p for p in logs_dir.iterdir() if p.is_dir() and p.name[:8].isdigit()),
        key=lambda p: p.name,
    )
    if not session_dirs:
        return False
    log_path = session_dirs[-1] / "gnuradiocontrol.log"
    if not log_path.exists():
        return False
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return label in text


def main() -> int:
    shared_state = init_shared_state("red", 433200000)
    lock = threading.Lock()
    controller = GnuradioController(shared_state, lock, poll_interval=0.3)
    controller.start()

    ok = True

    def check(label, expected_freq, timeout=15.0):
        nonlocal ok
        got = wait_for_frequency(expected_freq, timeout)
        passed = got == expected_freq
        ok = ok and passed
        print(f"{'PASS' if passed else 'FAIL'} | {label} | "
              f"expect freq={expected_freq} got={got} "
              f"(flowgraph instances so far: {len(FakePluto.instances)})")
        return passed

    # 1. initial noise_1
    check("noise_1 (rank=1)", 432200000, timeout=8.0)
    mode_ok = shared_state.get("mode") == "noise"
    print(f"{'PASS' if mode_ok else 'FAIL'} | shared_state mode published as noise "
          f"(got={shared_state.get('mode')})")
    ok = ok and mode_ok
    cfg = controller.current_config()
    cfg_ok = cfg is not None and cfg["mode"] == "noise" and cfg["frequency"] == 432200000
    bw_ok = cfg is not None and cfg["bandwidth"] == 480000
    print(f"{'PASS' if cfg_ok else 'FAIL'} | current_config exposes noise_1 params "
          f"(mode={cfg and cfg.get('mode')}, freq={cfg and cfg.get('frequency')})")
    print(f"{'PASS' if bw_ok else 'FAIL'} | noise_1 lpf bandwidth = {cfg and cfg.get('bandwidth')} (expect 480000)")
    ok = ok and cfg_ok and bw_ok

    # 2. retry scenario: fail the next device open, then rank=2 must succeed after backoff
    FakePluto.fail_next = True
    with lock:
        shared_state["rank"] = 2
        shared_state["noise_grade"] = rank_to_noise_grade(2)
    passed = check("noise_2 with retry (rank=2)", 432500000, timeout=20.0)
    retried = log_contains("flowgraph_rebuilt failed (attempt 1")
    print(f"{'PASS' if retried else 'FAIL'} | retry logged (backoff on failure)")
    ok = ok and retried
    cfg = controller.current_config()
    bw_ok = cfg is not None and cfg["bandwidth"] == 440000
    print(f"{'PASS' if bw_ok else 'FAIL'} | noise_2 lpf bandwidth = {cfg and cfg.get('bandwidth')} (expect 440000)")
    ok = ok and bw_ok

    # 3. rank=3 -> signal
    with lock:
        shared_state["rank"] = 3
        shared_state["noise_grade"] = rank_to_noise_grade(3)
    check("signal (rank=3)", 433200000, timeout=8.0)
    mode_ok = shared_state.get("mode") == "signal"
    print(f"{'PASS' if mode_ok else 'FAIL'} | shared_state mode published as signal "
          f"(got={shared_state.get('mode')})")
    ok = ok and mode_ok
    cfg = controller.current_config()
    cfg_ok = cfg is not None and cfg["mode"] == "signal" and cfg["frequency"] == 433200000
    bw_ok = cfg is not None and cfg["bandwidth"] == 280000
    print(f"{'PASS' if cfg_ok else 'FAIL'} | current_config follows signal conversion "
          f"(mode={cfg and cfg.get('mode')}, freq={cfg and cfg.get('frequency')})")
    print(f"{'PASS' if bw_ok else 'FAIL'} | signal lpf bandwidth = {cfg and cfg.get('bandwidth')} (expect 280000)")
    ok = ok and cfg_ok and bw_ok

    # 4. graceful shutdown
    controller.stop()
    time.sleep(0.3)
    alive = controller.thread.is_alive()
    print(f"{'PASS' if not alive else 'FAIL'} | graceful shutdown (thread stopped)")
    ok = ok and not alive

    # 5. status reports pushed to the window queue
    statuses = []
    while not controller.status_queue.empty():
        statuses.append(controller.status_queue.get_nowait())
    has_running_noise = any("SDR 运行中" in s and "noise" in s for s in statuses)
    has_retry = any("启动失败" in s for s in statuses)
    has_signal = any("signal" in s for s in statuses)
    print(f"{'PASS' if has_running_noise else 'FAIL'} | status: noise running reported")
    print(f"{'PASS' if has_retry else 'FAIL'} | status: retry failure reported")
    print(f"{'PASS' if has_signal else 'FAIL'} | status: signal mode reported")
    ok = ok and has_running_noise and has_retry and has_signal

    print("ALL PASS - dynamic conversion works" if ok else "HAS FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
