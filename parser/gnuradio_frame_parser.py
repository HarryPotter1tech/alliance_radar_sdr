from typing import Union
from dataclasses import dataclass, field


@dataclass
class RoboMaster_Signal_Info:
    cmd_id_1: int = 0x0A01
    hero_position: list[int] = field(default_factory=lambda: [0, 0])
    engineer_position: list[int] = field(default_factory=lambda: [0, 0])
    infantry_3_position: list[int] = field(default_factory=lambda: [0, 0])
    infantry_4_position: list[int] = field(default_factory=lambda: [0, 0])
    aerial_position: list[int] = field(default_factory=lambda: [0, 0])
    sentry_position: list[int] = field(default_factory=lambda: [0, 0])

    cmd_id_2: int = 0x0A02
    hero_blood: int = 0
    engineer_blood: int = 0
    infantry_3_blood: int = 0
    infantry_4_blood: int = 0
    reserved: int = 0
    sentry_blood: int = 0

    cmd_id_3: int = 0x0A03
    hero_ammo: int = 0
    infantry_3_ammo: int = 0
    infantry_4_ammo: int = 0
    aerial_ammo: int = 0
    sentry_ammo: int = 0

    cmd_id_4: int = 0x0A04
    remaining_gold: int = 0
    total_gold: int = 0
    supply_zone_status: int = 0
    central_highland_status: int = 0
    trapezoid_highland_status: int = 0
    fortress_gain_status: int = 0
    outpost_gain_status: int = 0
    base_gain_status: int = 0
    tunnel_1_status: int = 0
    tunnel_2_status: int = 0
    tunnel_3_status: int = 0
    tunnel_4_status: int = 0
    highland_upper_status: int = 0
    ramp_rear_status: int = 0
    road_upper_status: int = 0
    cmd_id_5: int = 0x0A05
    hero_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    engineer_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    infantry_3_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    infantry_4_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    sentry_gain: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    sentry_posture: int = 0
    hero_gain_state: int = 0
    engineer_gain_state: int = 0
    infantry_3_gain_state: int = 0
    infantry_4_gain_state: int = 0
    sentry_gain_state: int = 0


@dataclass
class RoboMaster_Noise_Key:
    cmd_id_6: int = 0x0A06
    sdr_behavior: int = 2
    sdr_key_1: int = 0
    sdr_key_2: int = 0
    sdr_key_3: int = 0
    sdr_key_4: int = 0
    sdr_key_5: int = 0
    sdr_key_6: int = 0


FrameParseResult = Union[RoboMaster_Signal_Info, RoboMaster_Noise_Key, None]

# cmd_id (LE u16) -> full frame length in bytes (cmd_id + data)
FRAME_LENGTHS = {
    0x0A01: 26,
    0x0A02: 14,
    0x0A03: 12,
    0x0A04: 10,
    0x0A05: 43,
    0x0A06: 8,
}


class GnuRadioFrameParser:
    def __init__(self, receive_mode: str = "signal"):
        self.message_package: bytes = b""
        self.receive_mode: str = receive_mode

    def payload_parse(self, input_data: bytes) -> FrameParseResult:
        self.message_package = input_data
        if self.message_package is None or len(self.message_package) < 10:
            return None
        if self.receive_mode == "noise":
            return self._parse_noise(input_data)
        return self._parse_signal(input_data)

    def _frame_complete(self, index: int, cmd_id: int) -> bool:
        return index + FRAME_LENGTHS.get(cmd_id, 0) <= len(self.message_package)

    def _parse_signal(self, input_data: bytes) -> RoboMaster_Signal_Info | None:
        info = RoboMaster_Signal_Info()
        parsed_any = False
        for i in range(0, len(self.message_package), 1):
            cmd_id: int = int.from_bytes(
                self.message_package[i : i + 2], byteorder="little"
            )
            if not self._frame_complete(i, cmd_id):
                continue

            if cmd_id == info.cmd_id_1:
                parsed_any = True
                info.hero_position[0] = int.from_bytes(
                    self.message_package[i + 2 : i + 4], byteorder="big", signed=True
                )
                info.hero_position[1] = int.from_bytes(
                    self.message_package[i + 4 : i + 6], byteorder="big", signed=True
                )
                info.engineer_position[0] = int.from_bytes(
                    self.message_package[i + 6 : i + 8], byteorder="big", signed=True
                )
                info.engineer_position[1] = int.from_bytes(
                    self.message_package[i + 8 : i + 10], byteorder="big", signed=True
                )
                info.infantry_3_position[0] = int.from_bytes(
                    self.message_package[i + 10 : i + 12], byteorder="big", signed=True
                )
                info.infantry_3_position[1] = int.from_bytes(
                    self.message_package[i + 12 : i + 14], byteorder="big", signed=True
                )
                info.infantry_4_position[0] = int.from_bytes(
                    self.message_package[i + 14 : i + 16], byteorder="big", signed=True
                )
                info.infantry_4_position[1] = int.from_bytes(
                    self.message_package[i + 16 : i + 18], byteorder="big", signed=True
                )
                info.aerial_position[0] = int.from_bytes(
                    self.message_package[i + 18 : i + 20], byteorder="big", signed=True
                )
                info.aerial_position[1] = int.from_bytes(
                    self.message_package[i + 20 : i + 22], byteorder="big", signed=True
                )
                info.sentry_position[0] = int.from_bytes(
                    self.message_package[i + 22 : i + 24], byteorder="big", signed=True
                )
                info.sentry_position[1] = int.from_bytes(
                    self.message_package[i + 24 : i + 26], byteorder="big", signed=True
                )

            elif cmd_id == info.cmd_id_2:
                parsed_any = True
                info.hero_blood = int.from_bytes(
                    self.message_package[i + 2 : i + 4], byteorder="big"
                )
                info.engineer_blood = int.from_bytes(
                    self.message_package[i + 4 : i + 6], byteorder="big"
                )
                info.infantry_3_blood = int.from_bytes(
                    self.message_package[i + 6 : i + 8], byteorder="big"
                )
                info.infantry_4_blood = int.from_bytes(
                    self.message_package[i + 8 : i + 10], byteorder="big"
                )
                info.reserved = int.from_bytes(
                    self.message_package[i + 10 : i + 12], byteorder="big"
                )
                info.sentry_blood = int.from_bytes(
                    self.message_package[i + 12 : i + 14], byteorder="big"
                )

            elif cmd_id == info.cmd_id_3:
                parsed_any = True
                info.hero_ammo = int.from_bytes(
                    self.message_package[i + 2 : i + 4], byteorder="big"
                )
                info.infantry_3_ammo = int.from_bytes(
                    self.message_package[i + 4 : i + 6], byteorder="big"
                )
                info.infantry_4_ammo = int.from_bytes(
                    self.message_package[i + 6 : i + 8], byteorder="big"
                )
                info.aerial_ammo = int.from_bytes(
                    self.message_package[i + 8 : i + 10], byteorder="big"
                )
                info.sentry_ammo = int.from_bytes(
                    self.message_package[i + 10 : i + 12], byteorder="big"
                )

            elif cmd_id == info.cmd_id_4:
                parsed_any = True
                info.remaining_gold = int.from_bytes(
                    self.message_package[i + 2 : i + 4], byteorder="big"
                )
                info.total_gold = int.from_bytes(
                    self.message_package[i + 4 : i + 6], byteorder="big"
                )
                raw = int.from_bytes(
                    self.message_package[i + 6 : i + 10], byteorder="little"
                )
                info.supply_zone_status = raw & 0x01
                info.central_highland_status = (raw >> 1) & 0x03
                info.trapezoid_highland_status = (raw >> 3) & 0x01
                info.fortress_gain_status = (raw >> 4) & 0x03
                info.outpost_gain_status = (raw >> 6) & 0x03
                info.base_gain_status = (raw >> 8) & 0x01
                info.tunnel_1_status = (raw >> 9) & 0x01
                info.tunnel_2_status = (raw >> 10) & 0x01
                info.tunnel_3_status = (raw >> 11) & 0x01
                info.tunnel_4_status = (raw >> 12) & 0x01
                info.highland_upper_status = (raw >> 13) & 0x01
                info.ramp_rear_status = (raw >> 14) & 0x01
                info.road_upper_status = (raw >> 15) & 0x01

            elif cmd_id == info.cmd_id_5:
                parsed_any = True
                info.hero_gain[0] = int.from_bytes(
                    self.message_package[i + 2 : i + 3], byteorder="big"
                )
                info.hero_gain[1] = int.from_bytes(
                    self.message_package[i + 3 : i + 5], byteorder="big"
                )
                info.hero_gain[2] = int.from_bytes(
                    self.message_package[i + 5 : i + 6], byteorder="big"
                )
                info.hero_gain[3] = int.from_bytes(
                    self.message_package[i + 6 : i + 7], byteorder="big"
                )
                info.hero_gain[4] = int.from_bytes(
                    self.message_package[i + 7 : i + 9], byteorder="big"
                )
                info.engineer_gain[0] = int.from_bytes(
                    self.message_package[i + 9 : i + 10], byteorder="big"
                )
                info.engineer_gain[1] = int.from_bytes(
                    self.message_package[i + 10 : i + 12], byteorder="big"
                )
                info.engineer_gain[2] = int.from_bytes(
                    self.message_package[i + 12 : i + 13], byteorder="big"
                )
                info.engineer_gain[3] = int.from_bytes(
                    self.message_package[i + 13 : i + 14], byteorder="big"
                )
                info.engineer_gain[4] = int.from_bytes(
                    self.message_package[i + 14 : i + 16], byteorder="big"
                )
                info.infantry_3_gain[0] = int.from_bytes(
                    self.message_package[i + 16 : i + 17], byteorder="big"
                )
                info.infantry_3_gain[1] = int.from_bytes(
                    self.message_package[i + 17 : i + 19], byteorder="big"
                )
                info.infantry_3_gain[2] = int.from_bytes(
                    self.message_package[i + 19 : i + 20], byteorder="big"
                )
                info.infantry_3_gain[3] = int.from_bytes(
                    self.message_package[i + 20 : i + 21], byteorder="big"
                )
                info.infantry_3_gain[4] = int.from_bytes(
                    self.message_package[i + 21 : i + 23], byteorder="big"
                )
                info.infantry_4_gain[0] = int.from_bytes(
                    self.message_package[i + 23 : i + 24], byteorder="big"
                )
                info.infantry_4_gain[1] = int.from_bytes(
                    self.message_package[i + 24 : i + 26], byteorder="big"
                )
                info.infantry_4_gain[2] = int.from_bytes(
                    self.message_package[i + 26 : i + 27], byteorder="big"
                )
                info.infantry_4_gain[3] = int.from_bytes(
                    self.message_package[i + 27 : i + 28], byteorder="big"
                )
                info.infantry_4_gain[4] = int.from_bytes(
                    self.message_package[i + 28 : i + 30], byteorder="big"
                )
                info.sentry_gain[0] = int.from_bytes(
                    self.message_package[i + 30 : i + 31], byteorder="big"
                )
                info.sentry_gain[1] = int.from_bytes(
                    self.message_package[i + 31 : i + 33], byteorder="big"
                )
                info.sentry_gain[2] = int.from_bytes(
                    self.message_package[i + 33 : i + 34], byteorder="big"
                )
                info.sentry_gain[3] = int.from_bytes(
                    self.message_package[i + 34 : i + 35], byteorder="big"
                )
                info.sentry_gain[4] = int.from_bytes(
                    self.message_package[i + 35 : i + 37], byteorder="big"
                )
                info.sentry_posture = int.from_bytes(
                    self.message_package[i + 37 : i + 38], byteorder="big"
                )
                info.hero_gain_state = int.from_bytes(
                    self.message_package[i + 38 : i + 39], byteorder="big"
                )
                info.engineer_gain_state = int.from_bytes(
                    self.message_package[i + 39 : i + 40], byteorder="big"
                )
                info.infantry_3_gain_state = int.from_bytes(
                    self.message_package[i + 40 : i + 41], byteorder="big"
                )
                info.infantry_4_gain_state = int.from_bytes(
                    self.message_package[i + 41 : i + 42], byteorder="big"
                )
                info.sentry_gain_state = int.from_bytes(
                    self.message_package[i + 42 : i + 43], byteorder="big"
                )
        return info if parsed_any else None

    def _parse_noise(self, input_data: bytes) -> RoboMaster_Noise_Key | None:
        noise_key = RoboMaster_Noise_Key()
        for i in range(0, len(self.message_package), 1):
            cmd_id: int = int.from_bytes(
                self.message_package[i : i + 2], byteorder="little"
            )
            if cmd_id == noise_key.cmd_id_6 and self._frame_complete(i, cmd_id):
                noise_key.sdr_key_1 = int.from_bytes(
                    self.message_package[i + 2 : i + 3], byteorder="big"
                )
                noise_key.sdr_key_2 = int.from_bytes(
                    self.message_package[i + 3 : i + 4], byteorder="big"
                )
                noise_key.sdr_key_3 = int.from_bytes(
                    self.message_package[i + 4 : i + 5], byteorder="big"
                )
                noise_key.sdr_key_4 = int.from_bytes(
                    self.message_package[i + 5 : i + 6], byteorder="big"
                )
                noise_key.sdr_key_5 = int.from_bytes(
                    self.message_package[i + 6 : i + 7], byteorder="big"
                )
                noise_key.sdr_key_6 = int.from_bytes(
                    self.message_package[i + 7 : i + 8], byteorder="big"
                )
                return noise_key
        return None
