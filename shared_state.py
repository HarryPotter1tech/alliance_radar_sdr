# ZMQ message command IDs (radar-egui PUB/SUB)
ZMQ_PUB_GAME_STATE = 0x0001
ZMQ_PUB_RADAR_AUTONOMOUS_DECISION_SYNC = 0x020E
ZMQ_SUB_SDR = 0x2002


def rank_to_noise_grade(rank: int) -> str:
    if rank <= 1:
        return "noise_1"
    if rank == 2:
        return "noise_2"
    return "noise_3"


def init_shared_state(side: str, signal_frequency: int) -> dict:
    return {
        "noise_grade": "noise_1",
        "signal_frequency": signal_frequency,
        "side": side,
        "rank": 1,
        "game_type": 0,
        "game_progress": 0,
        "stage_remain_time": 0,
        "sync_timestamp": 0,
        "key_modifiable": False,
    }
