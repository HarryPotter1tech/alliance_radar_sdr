#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frame parser tests: stage-driven full parsing (noise 0x0A06, signal 0x0A01-0x0A05).

Run: PYTHONPATH=. python3 tests/test_frame_parser.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser.gnuradio_frame_parser import (  # noqa: E402
    GnuRadioFrameParser,
    RoboMaster_Noise_Key,
    RoboMaster_Signal_Info,
)


def make_pos_frame():
    values = [10, -20, 30, -40, 50, -60, 70, -80, 90, -100, 110, -120]
    return (0x0A01).to_bytes(2, "little") + b"".join(
        v.to_bytes(2, "little", signed=True) for v in values
    )


def make_blood_frame():
    values = [100, 200, 300, 400, 500, 600]
    return (0x0A02).to_bytes(2, "little") + b"".join(
        v.to_bytes(2, "little") for v in values
    )


def make_ammo_frame():
    values = [1, 2, 3, 4, 5]
    return (0x0A03).to_bytes(2, "little") + b"".join(
        v.to_bytes(2, "little") for v in values
    )


def make_state_frame():
    raw = 0b1001_0011_0101_0111
    return (
        (0x0A04).to_bytes(2, "little")
        + (999).to_bytes(2, "little")
        + (888).to_bytes(2, "little")
        + raw.to_bytes(4, "little")
    )


def make_gain_frame():
    return (0x0A05).to_bytes(2, "little") + bytes(range(1, 42))


def make_noise_frame():
    return (0x0A06).to_bytes(2, "little") + bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])


def main() -> int:
    ok = True
    noise_buf = make_noise_frame() * 2  # >=10 bytes like the real 200-byte window
    signal_buf = (
        make_pos_frame()
        + make_blood_frame()
        + make_ammo_frame()
        + make_state_frame()
        + make_gain_frame()
    )

    # --- noise mode: parses 0x0A06 only ---
    r = GnuRadioFrameParser("noise").payload_parse(noise_buf)
    noise_ok = isinstance(r, RoboMaster_Noise_Key) and r.sdr_key_1 == 0x11 and r.sdr_key_6 == 0x66
    print(f"{'PASS' if noise_ok else 'FAIL'} | noise mode parses 0x0A06 keys")
    ok = ok and noise_ok

    r = GnuRadioFrameParser("noise").payload_parse(signal_buf)
    noise_ok = r is None
    print(f"{'PASS' if noise_ok else 'FAIL'} | noise mode rejects signal frames")
    ok = ok and noise_ok

    # --- signal mode: parses 0x0A01..0x0A05 ---
    r = GnuRadioFrameParser("signal").payload_parse(signal_buf)
    sig_ok = isinstance(r, RoboMaster_Signal_Info)
    if sig_ok:
        sig_ok = (
            r.hero_position == [10, -20]
            and r.sentry_position == [110, -120]
            and r.hero_blood == 100
            and r.sentry_blood == 600
            and r.aerial_ammo == 4
            and r.remaining_gold == 999
            and r.total_gold == 888
            and r.supply_zone_status == 1
            and r.tunnel_4_status == 1
            and r.road_upper_status == 1
            and r.hero_gain == [1, 0x0302, 4, 5, 0x0706]
            and r.sentry_gain == [29, 0x1F1E, 32, 33, 0x2322]
            and r.sentry_posture == 36
            and r.hero_gain_state == 37
            and r.engineer_gain_state == 38
            and r.infantry_3_gain_state == 39
            and r.infantry_4_gain_state == 40
            and r.sentry_gain_state == 41
        )
    print(f"{'PASS' if sig_ok else 'FAIL'} | signal mode parses 0x0A01..0x0A05")
    ok = ok and sig_ok

    r = GnuRadioFrameParser("signal").payload_parse(noise_buf)
    sig_ok = r is None
    print(f"{'PASS' if sig_ok else 'FAIL'} | signal mode rejects noise frames")
    ok = ok and sig_ok

    # --- frame length guard: truncated frames must not parse ---
    r = GnuRadioFrameParser("signal").payload_parse(make_blood_frame()[:-2])
    guard_ok = r is None
    # 0x0A06 placed within the last 7 bytes: not a complete 8-byte frame
    short_noise = b"\x00" * 5 + b"\x06\x0a\x11\x22\x33"
    r = GnuRadioFrameParser("noise").payload_parse(short_noise)
    guard_ok = guard_ok and r is None
    print(f"{'PASS' if guard_ok else 'FAIL'} | truncated frames rejected")
    ok = ok and guard_ok

    # --- incremental merge: frames missing from a window keep prior values ---
    p = GnuRadioFrameParser("signal")
    r1 = p.payload_parse(make_pos_frame() + make_blood_frame())
    r2 = p.payload_parse(make_ammo_frame() + make_state_frame())  # 无 0x0A01/0x0A02
    inc_ok = (
        isinstance(r1, RoboMaster_Signal_Info)
        and isinstance(r2, RoboMaster_Signal_Info)
        and r2.hero_position == [10, -20]      # 0x0A01 未命中,保留旧值
        and r2.hero_blood == 100               # 0x0A02 未命中,保留旧值
        and r2.hero_ammo == 1                  # 0x0A03 命中,更新
        and r2.remaining_gold == 999           # 0x0A04 命中,更新
    )
    print(f"{'PASS' if inc_ok else 'FAIL'} | incremental merge keeps prior frames")
    ok = ok and inc_ok

    # --- incremental merge: noise key unchanged when 0x0A06 absent ---
    p = GnuRadioFrameParser("noise")
    p.payload_parse(make_noise_frame() * 2)
    p.payload_parse(b"\x00" * 10)  # 无 0x0A06
    nk_inc = p.noise_key.sdr_key_1 == 0x11
    print(f"{'PASS' if nk_inc else 'FAIL'} | noise key kept when frame absent")
    ok = ok and nk_inc

    print("ALL PASS - parser stage parsing works" if ok else "HAS FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
