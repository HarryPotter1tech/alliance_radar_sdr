import threading

import zmq

from logs.event_logger import log, log_data, log_thread_start, log_thread_stop
from shared_state import (
    ZMQ_PUB_GAME_STATE,
    ZMQ_PUB_RADAR_AUTONOMOUS_DECISION_SYNC,
    rank_to_noise_grade,
)

ZMQ_SUB_ADDR = "tcp://127.0.0.1:5557"


def zmq_start_sub(
    shared_state: dict,
    lock: threading.Lock,
    stop_event: threading.Event | None = None,
) -> None:
    thread_name = threading.current_thread().name
    log_thread_start("event", thread_name)

    ctx = zmq.Context()
    sub_socket = ctx.socket(zmq.SUB)
    sub_socket.connect(ZMQ_SUB_ADDR)
    sub_socket.subscribe(b"")
    log("event", f"ZMQ SUB connected to {ZMQ_SUB_ADDR}")

    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            try:
                msg = sub_socket.recv_json()
            except Exception:
                continue

            cmd_id = msg.get("cmd_id", 0)

            with lock:
                if cmd_id == ZMQ_PUB_GAME_STATE:
                    shared_state["game_type"] = msg.get("game_type", 0)
                    shared_state["game_progress"] = msg.get("game_progress", 0)
                    shared_state["stage_remain_time"] = msg.get(
                        "stage_remain_time", 0
                    )
                    shared_state["sync_timestamp"] = msg.get(
                        "sync_timestamp", 0
                    )

                elif cmd_id == ZMQ_PUB_RADAR_AUTONOMOUS_DECISION_SYNC:
                    rank = msg.get("encryption_rank", 1)
                    shared_state["rank"] = rank
                    shared_state["key_modifiable"] = bool(
                        msg.get("key_modifiable", False)
                    )
                    shared_state["noise_grade"] = rank_to_noise_grade(rank)
                    log_data(
                        "event",
                        "noise_grade",
                        {
                            "rank": rank,
                            "noise_grade": shared_state["noise_grade"],
                        },
                    )
    finally:
        log_thread_stop("event", thread_name)
