# -*- coding: utf-8 -*-
# Single source of truth for the unified GFSK-RX receiver.
# Holds all noise (interference) and signal (information wave) parameters
# for one match, aligned with official rulebook V2.0.1 (Table 5-23 + Appendix 1).

SPS = 47
SAMPLE_RATE = 1000000
BT = 0.35
SDR_URI = "192.168.1.10"
TCP_PORT = 2500

# Access codes (8 bytes / 64 bits, big-endian), same for red and blue.
NOISE_ACCESS_CODE = "0001011011101000110100110111011100010101000111000111000100101101"  # 0x16E8D377151C712D
SIGNAL_ACCESS_CODE = "0010111101101111010011000111010010111001000101000100100100101110"  # 0x2F6F4C74B914492E

# Low-pass filter cutoff (Hz) used by the unified receiver.
NOISE_LPF_CUTOFF = 500000
SIGNAL_LPF_CUTOFF = 260000

# Signal (information wave) config per enemy side.
SIGNAL_CONFIGS = {
    "red": {
        "signal_frequency": 433200000,
        "signal_bandwidth": 540000,
        "signal_sensitivity": 1.5628,
    },
    "blue": {
        "signal_frequency": 433920000,
        "signal_bandwidth": 540000,
        "signal_sensitivity": 1.5628,
    },
}

# Noise (interference wave) config per grade and enemy side.
NOISE_CONFIGS = {
    "noise_1": {
        "red": {
            "noise_sensitivity": 2.8194,
            "noise_frequency": 432200000,
            "noise_bandwidth": 940000,
        },
        "blue": {
            "noise_sensitivity": 2.8194,
            "noise_frequency": 434920000,
            "noise_bandwidth": 940000,
        },
    },
    "noise_2": {
        "red": {
            "noise_sensitivity": 2.5681,
            "noise_frequency": 432500000,
            "noise_bandwidth": 860000,
        },
        "blue": {
            "noise_sensitivity": 2.5681,
            "noise_frequency": 434620000,
            "noise_bandwidth": 860000,
        },
    },
    "noise_3": {
        "red": {
            "noise_sensitivity": 0.6517,
            "noise_frequency": 432800000,
            "noise_bandwidth": 250000,
        },
        "blue": {
            "noise_sensitivity": 0.6517,
            "noise_frequency": 434320000,
            "noise_bandwidth": 250000,
        },
    },
}


def build_config(mode: str, enemy_side: str, noise_grade: str) -> dict:
    """Build the receiver config for the given stage.

    mode: "noise" (before rank 3) or "signal" (after interference reaches grade 3).
    """
    if mode == "signal":
        side = SIGNAL_CONFIGS[enemy_side]
        return {
            "mode": mode,
            "access_code": SIGNAL_ACCESS_CODE,
            "frequency": side["signal_frequency"],
            "bandwidth": SIGNAL_LPF_CUTOFF,
            "sensitivity": side["signal_sensitivity"],
            "sdr_uri": SDR_URI,
            "tcp_port": TCP_PORT,
        }
    grade = NOISE_CONFIGS[noise_grade][enemy_side]
    return {
        "mode": mode,
        "access_code": NOISE_ACCESS_CODE,
        "frequency": grade["noise_frequency"],
        "bandwidth": NOISE_LPF_CUTOFF,
        "sensitivity": grade["noise_sensitivity"],
        "sdr_uri": SDR_URI,
        "tcp_port": TCP_PORT,
    }
