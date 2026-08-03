import json
import threading
import time

import zmq

from logs.event_logger import log, log_data, log_thread_start, log_thread_stop
from parser.gnuradio_frame_parser import RoboMaster_Signal_Info, RoboMaster_Noise_Key
from shared_state import ZMQ_SUB_SDR

ZMQ_PUB_ADDR = "tcp://*:5555"
PUB_INTERVAL = 0.1


def is_valid_ascii_alnum_key(key: list[int]) -> bool:
    """True if all 6 key bytes are ASCII letters or digits (rulebook: 数字字母组合)."""
    return all(
        48 <= byte <= 57 or 65 <= byte <= 90 or 97 <= byte <= 122 for byte in key
    )


def _build_position(info: RoboMaster_Signal_Info) -> dict:
    return {
        "hero_x": info.hero_position[0],
        "hero_y": info.hero_position[1],
        "engineer_x": info.engineer_position[0],
        "engineer_y": info.engineer_position[1],
        "infantry_3_x": info.infantry_3_position[0],
        "infantry_3_y": info.infantry_3_position[1],
        "infantry_4_x": info.infantry_4_position[0],
        "infantry_4_y": info.infantry_4_position[1],
        "aerial_x": info.aerial_position[0],
        "aerial_y": info.aerial_position[1],
        "sentry_x": info.sentry_position[0],
        "sentry_y": info.sentry_position[1],
    }


def _build_blood(info: RoboMaster_Signal_Info) -> dict:
    return {
        "hero_blood": info.hero_blood,
        "engineer_blood": info.engineer_blood,
        "infantry_3_blood": info.infantry_3_blood,
        "infantry_4_blood": info.infantry_4_blood,
        "reserved": info.reserved,
        "sentry_blood": info.sentry_blood,
    }


def _build_ammo(info: RoboMaster_Signal_Info) -> dict:
    return {
        "hero_ammo": info.hero_ammo,
        "infantry_3_ammo": info.infantry_3_ammo,
        "infantry_4_ammo": info.infantry_4_ammo,
        "aerial_ammo": info.aerial_ammo,
        "sentry_ammo": info.sentry_ammo,
    }


def _build_state(info: RoboMaster_Signal_Info) -> dict:
    return {
        "remaining_gold": info.remaining_gold,
        "total_gold": info.total_gold,
        "supply_zone_status": info.supply_zone_status,
        "central_highland_status": info.central_highland_status,
        "trapezoid_highland_status": info.trapezoid_highland_status,
        "fortress_gain_status": info.fortress_gain_status,
        "outpost_gain_status": info.outpost_gain_status,
        "base_gain_status": info.base_gain_status,
        "tunnel_1_status": info.tunnel_1_status,
        "tunnel_2_status": info.tunnel_2_status,
        "tunnel_3_status": info.tunnel_3_status,
        "tunnel_4_status": info.tunnel_4_status,
        "highland_upper_status": info.highland_upper_status,
        "ramp_rear_status": info.ramp_rear_status,
        "road_upper_status": info.road_upper_status,
    }


def _build_gain(info: RoboMaster_Signal_Info) -> dict:
    return {
        "hero_hp_recovery": info.hero_gain[0],
        "hero_cooling_acceleration": info.hero_gain[1],
        "hero_defence": info.hero_gain[2],
        "hero_negative_defence": info.hero_gain[3],
        "hero_attack": info.hero_gain[4],
        "engineer_hp_recovery": info.engineer_gain[0],
        "engineer_cooling_acceleration": info.engineer_gain[1],
        "engineer_defence": info.engineer_gain[2],
        "engineer_negative_defence": info.engineer_gain[3],
        "engineer_attack": info.engineer_gain[4],
        "infantry_3_hp_recovery": info.infantry_3_gain[0],
        "infantry_3_cooling_acceleration": info.infantry_3_gain[1],
        "infantry_3_defence": info.infantry_3_gain[2],
        "infantry_3_negative_defence": info.infantry_3_gain[3],
        "infantry_3_attack": info.infantry_3_gain[4],
        "infantry_4_hp_recovery": info.infantry_4_gain[0],
        "infantry_4_cooling_acceleration": info.infantry_4_gain[1],
        "infantry_4_defence": info.infantry_4_gain[2],
        "infantry_4_negative_defence": info.infantry_4_gain[3],
        "infantry_4_attack": info.infantry_4_gain[4],
        "sentry_hp_recovery": info.sentry_gain[0],
        "sentry_cooling_acceleration": info.sentry_gain[1],
        "sentry_defence": info.sentry_gain[2],
        "sentry_negative_defence": info.sentry_gain[3],
        "sentry_attack": info.sentry_gain[4],
        "sentry_posture": info.sentry_posture,
        "hero_state": info.hero_gain_state,
        "engineer_state": info.engineer_gain_state,
        "infantry_3_state": info.infantry_3_gain_state,
        "infantry_4_state": info.infantry_4_gain_state,
        "sentry_state": info.sentry_gain_state,
    }


def _build_key(noise_key: RoboMaster_Noise_Key) -> dict:
    return {
        "key": [
            noise_key.sdr_key_1,
            noise_key.sdr_key_2,
            noise_key.sdr_key_3,
            noise_key.sdr_key_4,
            noise_key.sdr_key_5,
            noise_key.sdr_key_6,
        ]
    }


def zmq_start_pub(
    signal_info: RoboMaster_Signal_Info,
    noise_key: RoboMaster_Noise_Key,
    lock: threading.Lock,
    shared_state: dict,
    stop_event: threading.Event | None = None,
    pub_addr: str = ZMQ_PUB_ADDR,
) -> None:
    thread_name = threading.current_thread().name
    log_thread_start("event", thread_name)

    ctx = zmq.Context()
    pub_socket = ctx.socket(zmq.PUB)
    pub_socket.bind(pub_addr)
    log("event", f"ZMQ PUB bound to {pub_addr}")

    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            with lock:
                game_progress = shared_state.get("game_progress", 0)
                if game_progress != 4:
                    log(
                        "zmq_pub",
                        f"skip publish: game_progress={game_progress}",
                    )
                    time.sleep(PUB_INTERVAL)
                    continue
                if shared_state.get("mode", "noise") == "noise":
                    key = _build_key(noise_key)["key"]
                    if not is_valid_ascii_alnum_key(key):
                        log(
                            "zmq_pub",
                            f"skip publish: noise key filtered (non-ASCII): {key}",
                        )
                        time.sleep(PUB_INTERVAL)
                        continue
                msg = {
                    "cmd_id": ZMQ_SUB_SDR,
                    "position": _build_position(signal_info),
                    "blood": _build_blood(signal_info),
                    "ammo": _build_ammo(signal_info),
                    "state": _build_state(signal_info),
                    "gain": _build_gain(signal_info),
                    "key": _build_key(noise_key),
                }
            pub_socket.send_string(json.dumps(msg))
            log_data("zmq_pub", "publish", msg)
            time.sleep(PUB_INTERVAL)
    finally:
        log_thread_stop("event", thread_name)
