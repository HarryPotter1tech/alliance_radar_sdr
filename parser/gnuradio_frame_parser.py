from typing import Union
from dataclasses import dataclass, field


@dataclass
class RoboMaster_Signal_Info:
    cmd_id_1: int = 0x0A01
    hero_position: list[int] = field(default_factory=lambda: [0, 0])
    engineer_position: list[int] = field(default_factory=lambda: [0, 0])
    infentry_position_1: list[int] = field(default_factory=lambda: [0, 0])
    infentry_position_2: list[int] = field(default_factory=lambda: [0, 0])
    drone_position: list[int] = field(default_factory=lambda: [0, 0])
    sentinel_position: list[int] = field(default_factory=lambda: [0, 0])

    cmd_id_2: int = 0x0A02
    hero_blood: int = 0
    engineer_blood: int = 0
    infentry_blood_1: int = 0
    infentry_blood_2: int = 0
    saven_blood: int = 0
    sentinel_blood: int = 0

    cmd_id_3: int = 0x0A03
    hero_amnunition: int = 0
    infentry_amnunition_1: int = 0
    infentry_amnunition_2: int = 0
    drone_amnunition: int = 0
    sentinel_amnunition: int = 0

    cmd_id_4: int = 0x0A04
    econmic_remain: int = 0
    economic_total: int = 0
    occupation_status: bytes = b""
    cmd_id_5: int = 0x0A05
    # each gain=1+2+1+1+2 total 7 bytes
    hero_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    engineer_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    infentry_gain_1: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    infentry_gain_2: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    sentinel_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    sentinel_posture: int = 0


@dataclass
class RoboMaster_Noise_Key:
    cmd_id_6: int = 0x0A06
    sdr_behavior: int = 2  # 1 byte
    # if sdr_behavior=1,change sdr_key
    # if sdr_behavior=2, transmit sdr_key to robomaster server
    sdr_key_1: int = 0  # 1 byte
    sdr_key_2: int = 0  # 1 byte
    sdr_key_3: int = 0  # 1 byte
    sdr_key_4: int = 0  # 1 byte
    sdr_key_5: int = 0  # 1 byte
    sdr_key_6: int = 0  # 1 byte


FrameParseResult = Union[RoboMaster_Signal_Info, RoboMaster_Noise_Key, None]


class FrameParser:
    def __init__(self, receive_mode: str = "signal"):
        self.message_package: bytes = b""
        self.receive_mode: str = receive_mode

    def payload_parse(self, input_data: bytes) -> FrameParseResult:
        self.message_package = input_data
        # Different minimum length for signal vs noise: signal needs 90 bytes, noise frame is 16 bytes
        min_length = 10
        if self.message_package is None or len(self.message_package) < min_length:
            return None

        if self.receive_mode == "signal":
            info = RoboMaster_Signal_Info()
            for i in range(0, len(self.message_package), 1):
                # len(message_package)=26+14+12+12+38=102
                cmd_id: int = int.from_bytes(
                    self.message_package[i : i + 2], byteorder="big"
                )

                if cmd_id == info.cmd_id_1:
                    info.hero_position[0] = int.from_bytes(
                        self.message_package[i + 2 : i + 4],
                        byteorder="big",
                        signed=True,
                    )
                    info.hero_position[1] = int.from_bytes(
                        self.message_package[i + 4 : i + 6],
                        byteorder="big",
                        signed=True,
                    )
                    info.engineer_position[0] = int.from_bytes(
                        self.message_package[i + 6 : i + 8],
                        byteorder="big",
                        signed=True,
                    )
                    info.engineer_position[1] = int.from_bytes(
                        self.message_package[i + 8 : i + 10],
                        byteorder="big",
                        signed=True,
                    )
                    info.infentry_position_1[0] = int.from_bytes(
                        self.message_package[i + 10 : i + 12],
                        byteorder="big",
                        signed=True,
                    )
                    info.infentry_position_1[1] = int.from_bytes(
                        self.message_package[i + 12 : i + 14],
                        byteorder="big",
                        signed=True,
                    )
                    info.infentry_position_2[0] = int.from_bytes(
                        self.message_package[i + 14 : i + 16],
                        byteorder="big",
                        signed=True,
                    )
                    info.infentry_position_2[1] = int.from_bytes(
                        self.message_package[i + 16 : i + 18],
                        byteorder="big",
                        signed=True,
                    )
                    info.drone_position[0] = int.from_bytes(
                        self.message_package[i + 18 : i + 20],
                        byteorder="big",
                        signed=True,
                    )
                    info.drone_position[1] = int.from_bytes(
                        self.message_package[i + 20 : i + 22],
                        byteorder="big",
                        signed=True,
                    )
                    info.sentinel_position[0] = int.from_bytes(
                        self.message_package[i + 22 : i + 24],
                        byteorder="big",
                        signed=True,
                    )
                    info.sentinel_position[1] = int.from_bytes(
                        self.message_package[i + 24 : i + 26],
                        byteorder="big",
                        signed=True,
                    )

                elif cmd_id == info.cmd_id_2:
                    info.hero_blood = int.from_bytes(
                        self.message_package[i + 2 : i + 4], byteorder="big"
                    )
                    info.engineer_blood = int.from_bytes(
                        self.message_package[i + 4 : i + 6], byteorder="big"
                    )
                    info.infentry_blood_1 = int.from_bytes(
                        self.message_package[i + 6 : i + 8], byteorder="big"
                    )
                    info.infentry_blood_2 = int.from_bytes(
                        self.message_package[i + 8 : i + 10], byteorder="big"
                    )
                    info.saven_blood = int.from_bytes(
                        self.message_package[i + 10 : i + 12], byteorder="big"
                    )
                    info.sentinel_blood = int.from_bytes(
                        self.message_package[i + 12 : i + 14], byteorder="big"
                    )

                elif cmd_id == info.cmd_id_3:
                    info.hero_amnunition = int.from_bytes(
                        self.message_package[i + 2 : i + 4], byteorder="big"
                    )
                    info.infentry_amnunition_1 = int.from_bytes(
                        self.message_package[i + 4 : i + 6], byteorder="big"
                    )
                    info.infentry_amnunition_2 = int.from_bytes(
                        self.message_package[i + 6 : i + 8], byteorder="big"
                    )
                    info.drone_amnunition = int.from_bytes(
                        self.message_package[i + 8 : i + 10], byteorder="big"
                    )
                    info.sentinel_amnunition = int.from_bytes(
                        self.message_package[i + 10 : i + 12], byteorder="big"
                    )

                elif cmd_id == info.cmd_id_4:
                    info.econmic_remain = int.from_bytes(
                        self.message_package[i + 2 : i + 4], byteorder="big"
                    )
                    info.economic_total = int.from_bytes(
                        self.message_package[i + 4 : i + 6], byteorder="big"
                    )
                    info.occupation_status = self.message_package[i + 6 : i + 10]

                elif cmd_id == info.cmd_id_5:
                    info.hero_gain[0] = int.from_bytes(
                        self.message_package[i + 2 : i + 3], byteorder="big"
                    )  # 1 byte
                    info.hero_gain[1] = int.from_bytes(
                        self.message_package[i + 3 : i + 5], byteorder="big"
                    )  # 2 byte
                    info.hero_gain[2] = int.from_bytes(
                        self.message_package[i + 5 : i + 6], byteorder="big"
                    )  # 1 byte
                    info.hero_gain[3] = int.from_bytes(
                        self.message_package[i + 6 : i + 7], byteorder="big"
                    )  # 1 byte
                    info.hero_gain[4] = int.from_bytes(
                        self.message_package[i + 7 : i + 9], byteorder="big"
                    )  # 2 byte
                    info.engineer_gain[0] = int.from_bytes(
                        self.message_package[i + 9 : i + 10], byteorder="big"
                    )  # 1 byte
                    info.engineer_gain[1] = int.from_bytes(
                        self.message_package[i + 10 : i + 12], byteorder="big"
                    )  # 2 byte
                    info.engineer_gain[2] = int.from_bytes(
                        self.message_package[i + 12 : i + 13], byteorder="big"
                    )  # 1 byte
                    info.engineer_gain[3] = int.from_bytes(
                        self.message_package[i + 13 : i + 14], byteorder="big"
                    )  # 1 byte
                    info.engineer_gain[4] = int.from_bytes(
                        self.message_package[i + 14 : i + 16], byteorder="big"
                    )  # 2 byte
                    info.infentry_gain_1[0] = int.from_bytes(
                        self.message_package[i + 16 : i + 17], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_1[1] = int.from_bytes(
                        self.message_package[i + 17 : i + 19], byteorder="big"
                    )  # 2 byte
                    info.infentry_gain_1[2] = int.from_bytes(
                        self.message_package[i + 19 : i + 20], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_1[3] = int.from_bytes(
                        self.message_package[i + 20 : i + 21], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_1[4] = int.from_bytes(
                        self.message_package[i + 21 : i + 23], byteorder="big"
                    )  # 2 byte
                    info.infentry_gain_2[0] = int.from_bytes(
                        self.message_package[i + 23 : i + 24], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_2[1] = int.from_bytes(
                        self.message_package[i + 24 : i + 26], byteorder="big"
                    )  # 2 byte
                    info.infentry_gain_2[2] = int.from_bytes(
                        self.message_package[i + 26 : i + 27], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_2[3] = int.from_bytes(
                        self.message_package[i + 27 : i + 28], byteorder="big"
                    )  # 1 byte
                    info.infentry_gain_2[4] = int.from_bytes(
                        self.message_package[i + 28 : i + 30], byteorder="big"
                    )  # 2 byte
                    info.sentinel_gain[0] = int.from_bytes(
                        self.message_package[i + 30 : i + 31], byteorder="big"
                    )  # 1 byte
                    info.sentinel_gain[1] = int.from_bytes(
                        self.message_package[i + 31 : i + 33], byteorder="big"
                    )  # 2 byte
                    info.sentinel_gain[2] = int.from_bytes(
                        self.message_package[i + 33 : i + 34], byteorder="big"
                    )  # 1 byte
                    info.sentinel_gain[3] = int.from_bytes(
                        self.message_package[i + 34 : i + 35], byteorder="big"
                    )  # 1 byte
                    info.sentinel_gain[4] = int.from_bytes(
                        self.message_package[i + 35 : i + 37], byteorder="big"
                    )  # 2 byte
                    info.sentinel_posture = int.from_bytes(
                        self.message_package[i + 37 : i + 38], byteorder="big"
                    )  # 1 byte
            return info

        if self.receive_mode == "noise":
            noise_key = RoboMaster_Noise_Key()
            print(self.receive_mode)
            for i in range(0, len(self.message_package), 1):
                cmd_id: int = int.from_bytes(
                    self.message_package[i : i + 2], byteorder="big"
                )
                if cmd_id == noise_key.cmd_id_6:
                    noise_key.sdr_behavior = int.from_bytes(
                        self.message_package[i + 2 : i + 3], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_1 = int.from_bytes(
                        self.message_package[i + 3 : i + 4], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_2 = int.from_bytes(
                        self.message_package[i + 4 : i + 5], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_3 = int.from_bytes(
                        self.message_package[i + 5 : i + 6], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_4 = int.from_bytes(
                        self.message_package[i + 6 : i + 7], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_5 = int.from_bytes(
                        self.message_package[i + 7 : i + 8], byteorder="big"
                    )  # 1 byte
                    noise_key.sdr_key_6 = int.from_bytes(
                        self.message_package[i + 8 : i + 9], byteorder="big"
                    )  # 1 byte
                    print(self.message_package[i : i + 9])
                    return noise_key
            return None
