import random

from crc_table import crc_8_table, crc_16_table


class MessageValueGenerator:
    def __init__(
        self,
        set_mode: str = "random",  # manual or random
        # cmd_id=0x0a01
        cmd_id_1: int = 0x0A01,
        hero_position: list[int] = [0, 0],
        engineer_position: list[int] = [0, 0],
        infentry_position_1: list[int] = [0, 0],
        infentry_position_2: list[int] = [0, 0],
        drone_position: list[int] = [0, 0],
        sentinel_position: list[int] = [0, 0],
        # cmd_id=0x0a02
        cmd_id_2: int = 0x0A02,
        hero_blood: int = 200,
        engineer_blood: int = 200,
        infentry_blood_1: int = 200,
        infentry_blood_2: int = 200,
        save_blood: int = 0x0000,
        sentinel_blood: int = 200,
        # cmd_id=0x0a03
        cmd_id_3: int = 0x0A03,
        hero_ammunition: int = 100,
        infentry_ammunition_1: int = 100,
        infentry_ammunition_2: int = 100,
        drone_ammunition: int = 100,
        sentinel_ammunition: int = 100,
        # cmd_id=0x0a04
        cmd_id_4: int = 0x0A04,
        econmic_remain: int = 1000,
        economic_total: int = 0,
        occupation_status: int = 0b0000010001001110,
        # cmd_id_5: int = 0x0A05,
        # robot_gain=health_regeneration_gain(1 byte)+shooting_heat_cooling_gain(2 bytes)+defense_gain(1 byte)+negative_defense_gain(1 byte)+attack_gain(2 bytes)
        cmd_id_5: int = 0x0A05,
        hero_gain: list[int] = [0, 0, 0, 0, 0],
        engineer_gain: list[int] = [0, 0, 0, 0, 0],
        infentry_gain_1: list[int] = [0, 0, 0, 0, 0],
        infentry_gain_2: list[int] = [0, 0, 0, 0, 0],
        drone_gain: list[int] = [0, 0, 0, 0, 0],
        sentinel_gain: list[int] = [0, 0, 0, 0, 0],
        sentinel_posture: int = 0,
    ):
        self.set_mode = set_mode
        # frame_header
        # SOF(1 byte) + data_length(2 byte) + seq(1 byte)+crc8(1 byte)
        self.SOF = 0xA5
        self.data_length = 0x00
        self.seq = 0x00
        self._crc8 = 0x00

        # cmd_id
        self.cmd_id_1 = cmd_id_1.to_bytes(2, byteorder="big")
        self.cmd_id_2 = cmd_id_2.to_bytes(2, byteorder="big")
        self.cmd_id_3 = cmd_id_3.to_bytes(2, byteorder="big")
        self.cmd_id_4 = cmd_id_4.to_bytes(2, byteorder="big")
        self.cmd_id_5 = cmd_id_5.to_bytes(2, byteorder="big")

        # mode choice&&data
        if self.set_mode == "manual":
            self.hero_position_x = hero_position[0].to_bytes(2, byteorder="big")
            self.hero_position_y = hero_position[1].to_bytes(2, byteorder="big")
            self.engineer_position_x = engineer_position[0].to_bytes(2, byteorder="big")
            self.engineer_position_y = engineer_position[1].to_bytes(2, byteorder="big")
            self.infentry_position_1_x = infentry_position_1[0].to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_1_y = infentry_position_1[1].to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_2_x = infentry_position_2[0].to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_2_y = infentry_position_2[1].to_bytes(
                2, byteorder="big"
            )
            self.drone_position_x = drone_position[0].to_bytes(2, byteorder="big")
            self.drone_position_y = drone_position[1].to_bytes(2, byteorder="big")
            self.sentinel_position_x = sentinel_position[0].to_bytes(2, byteorder="big")
            self.sentinel_position_y = sentinel_position[1].to_bytes(2, byteorder="big")

            self.hero_blood = hero_blood.to_bytes(2, byteorder="big")
            self.engineer_blood = engineer_blood.to_bytes(2, byteorder="big")
            self.infentry_blood_1 = infentry_blood_1.to_bytes(2, byteorder="big")
            self.infentry_blood_2 = infentry_blood_2.to_bytes(2, byteorder="big")
            self.save_blood = save_blood.to_bytes(2, byteorder="big")
            self.sentinel_blood = sentinel_blood.to_bytes(2, byteorder="big")

            self.hero_ammunition = hero_ammunition.to_bytes(2, byteorder="big")
            self.infentry_ammunition_1 = infentry_ammunition_1.to_bytes(
                2, byteorder="big"
            )
            self.infentry_ammunition_2 = infentry_ammunition_2.to_bytes(
                2, byteorder="big"
            )
            self.drone_ammunition = drone_ammunition.to_bytes(2, byteorder="big")
            self.sentinel_ammunition = sentinel_ammunition.to_bytes(2, byteorder="big")

            self.econmic_remain = econmic_remain.to_bytes(2, byteorder="big")
            self.economic_total = economic_total.to_bytes(2, byteorder="big")
            self.occupation_status = occupation_status.to_bytes(4, byteorder="big")

            self.hero_gain = self._pack_gain(hero_gain)
            self.engineer_gain = self._pack_gain(engineer_gain)
            self.infentry_gain_1 = self._pack_gain(infentry_gain_1)
            self.infentry_gain_2 = self._pack_gain(infentry_gain_2)
            self.drone_gain = self._pack_gain(drone_gain)
            self.sentinel_gain = self._pack_gain(sentinel_gain)
            self.sentinel_posture = sentinel_posture.to_bytes(1, byteorder="big")
        if self.set_mode == "random":
            self.hero_position_x = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.hero_position_y = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.engineer_position_x = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.engineer_position_y = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_1_x = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_1_y = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_2_x = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.infentry_position_2_y = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.drone_position_x = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.drone_position_y = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.sentinel_position_x = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.sentinel_position_y = random.randint(0, 1000).to_bytes(
                2, byteorder="big"
            )
            self.hero_blood = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.engineer_blood = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.infentry_blood_1 = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.infentry_blood_2 = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.save_blood = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.sentinel_blood = random.randint(0, 200).to_bytes(2, byteorder="big")
            self.hero_ammunition = random.randint(0, 100).to_bytes(2, byteorder="big")
            self.infentry_ammunition_1 = random.randint(0, 100).to_bytes(
                2, byteorder="big"
            )
            self.infentry_ammunition_2 = random.randint(0, 100).to_bytes(
                2, byteorder="big"
            )
            self.drone_ammunition = random.randint(0, 100).to_bytes(2, byteorder="big")
            self.sentinel_ammunition = random.randint(0, 100).to_bytes(
                2, byteorder="big"
            )
            self.econmic_remain = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.economic_total = random.randint(0, 1000).to_bytes(2, byteorder="big")
            self.occupation_status = random.randint(0, 0xFFFFFFFF).to_bytes(
                4, byteorder="big"
            )
            self.hero_gain = [random.randint(0, 100) for _ in range(5)]
            self.engineer_gain = [random.randint(0, 100) for _ in range(5)]
            self.infentry_gain_1 = [random.randint(0, 100) for _ in range(5)]
            self.infentry_gain_2 = [random.randint(0, 100) for _ in range(5)]
            self.drone_gain = [random.randint(0, 100) for _ in range(5)]
            self.sentinel_gain = [random.randint(0, 100) for _ in range(5)]
            self.hero_gain = self._pack_gain(self.hero_gain)
            self.engineer_gain = self._pack_gain(self.engineer_gain)
            self.infentry_gain_1 = self._pack_gain(self.infentry_gain_1)
            self.infentry_gain_2 = self._pack_gain(self.infentry_gain_2)
            self.drone_gain = self._pack_gain(self.drone_gain)
            self.sentinel_gain = self._pack_gain(self.sentinel_gain)
            self.sentinel_posture = random.randint(0, 255).to_bytes(1, byteorder="big")
            print("Random values generate>>>.")
            print(
                int.from_bytes(self.hero_position_x, byteorder="big"),
                int.from_bytes(self.hero_position_y, byteorder="big"),
            )
            print(
                int.from_bytes(self.engineer_position_x, byteorder="big"),
                int.from_bytes(self.engineer_position_y, byteorder="big"),
            )
            print(
                int.from_bytes(self.infentry_position_1_x, byteorder="big"),
                int.from_bytes(self.infentry_position_1_y, byteorder="big"),
            )
            print(
                int.from_bytes(self.infentry_position_2_x, byteorder="big"),
                int.from_bytes(self.infentry_position_2_y, byteorder="big"),
            )
            print(
                int.from_bytes(self.drone_position_x, byteorder="big"),
                int.from_bytes(self.drone_position_y, byteorder="big"),
            )
            print(
                int.from_bytes(self.sentinel_position_x, byteorder="big"),
                int.from_bytes(self.sentinel_position_y, byteorder="big"),
            )
            print(int.from_bytes(self.hero_blood, byteorder="big"))
            print(int.from_bytes(self.engineer_blood, byteorder="big"))
            print(int.from_bytes(self.infentry_blood_1, byteorder="big"))
            print(int.from_bytes(self.infentry_blood_2, byteorder="big"))
            print(int.from_bytes(self.save_blood, byteorder="big"))
            print(int.from_bytes(self.sentinel_blood, byteorder="big"))
            print(int.from_bytes(self.hero_ammunition, byteorder="big"))
            print(int.from_bytes(self.infentry_ammunition_1, byteorder="big"))
            print(int.from_bytes(self.infentry_ammunition_2, byteorder="big"))
            print(int.from_bytes(self.drone_ammunition, byteorder="big"))
            print(int.from_bytes(self.sentinel_ammunition, byteorder="big"))
            print(int.from_bytes(self.econmic_remain, byteorder="big"))
            print(int.from_bytes(self.economic_total, byteorder="big"))
            print(int.from_bytes(self.occupation_status, byteorder="big"))
            print(int.from_bytes(self.hero_gain, byteorder="big"))
            print(int.from_bytes(self.engineer_gain, byteorder="big"))
            print(int.from_bytes(self.infentry_gain_1, byteorder="big"))
            print(int.from_bytes(self.infentry_gain_2, byteorder="big"))
            print(int.from_bytes(self.sentinel_gain, byteorder="big"))
            print(int.from_bytes(self.sentinel_posture, byteorder="big"))
            print("Random values printed successfully.")
        # frame_tail
        self._crc16 = 0x0000

    def crc8(self, data: bytes) -> int:
        crc = 0xFF
        for byte in data:
            crc = crc_8_table[crc ^ byte]
        return crc ^ 0xFF

    def crc16(self, data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ crc_16_table[(crc & 0xFF) ^ byte]
        return crc ^ 0xFFFF

    def message_pack(self) -> bytes:
        # cmd_id_1 的负载：位置
        payload_1 = (
            self.hero_position_x
            + self.hero_position_y
            + self.engineer_position_x
            + self.engineer_position_y
            + self.infentry_position_1_x
            + self.infentry_position_1_y
            + self.infentry_position_2_x
            + self.infentry_position_2_y
            + self.drone_position_x
            + self.drone_position_y
            + self.sentinel_position_x
            + self.sentinel_position_y
        )

        # cmd_id_2 的负载：血量
        payload_2 = (
            self.hero_blood
            + self.engineer_blood
            + self.infentry_blood_1
            + self.infentry_blood_2
            + self.save_blood
            + self.sentinel_blood
        )

        # cmd_id_3 的负载：弹量
        payload_3 = (
            self.hero_ammunition
            + self.infentry_ammunition_1
            + self.infentry_ammunition_2
            + self.drone_ammunition
            + self.sentinel_ammunition
        )

        # cmd_id_4 的负载：经济、占点
        payload_4 = self.econmic_remain + self.economic_total + self.occupation_status

        # cmd_id_5 的负载：各类增益，先把 list[bytes] 拼成 bytes
        payload_5 = (
            self.hero_gain
            + self.engineer_gain
            + self.infentry_gain_1
            + self.infentry_gain_2
            + self.sentinel_gain
            + self.sentinel_posture
        )

        # 生成 5 个完整帧并拼接
        self.message_package = (
            self._build_frame(self.cmd_id_1, payload_1)
            + self._build_frame(self.cmd_id_2, payload_2)
            + self._build_frame(self.cmd_id_3, payload_3)
            + self._build_frame(self.cmd_id_4, payload_4)
            + self._build_frame(self.cmd_id_5, payload_5)
        )
        return self.message_package

    def _build_frame(self, cmd_id: bytes, payload: bytes) -> bytes:
        # data_length: 2 字节
        data_length = len(payload).to_bytes(2, byteorder="big")

        # 头: SOF(1) + data_length(2) + seq(1)
        header = (
            self.SOF.to_bytes(1, byteorder="big")
            + data_length
            + self.seq.to_bytes(1, byteorder="big")
        )
        crc8_val = self.crc8(header).to_bytes(1, byteorder="big")
        frame_wo_crc16 = header + crc8_val + cmd_id + payload
        crc16_val = self.crc16(frame_wo_crc16).to_bytes(2, byteorder="big")

        return frame_wo_crc16 + crc16_val

    def _pack_gain(self, gain: list[int]) -> bytes:
        heal, cooling, defense, neg_def, attack = gain

        # 1 字节回血增益
        heal_b = heal.to_bytes(1, byteorder="big", signed=False)

        # 2 字节射击热量冷却增益，小端
        cooling_b = cooling.to_bytes(2, byteorder="big", signed=False)

        # 1 字节防御增益
        defense_b = defense.to_bytes(1, byteorder="big", signed=False)

        # 1 字节负防御增益（易伤）
        neg_def_b = neg_def.to_bytes(1, byteorder="big", signed=False)

        # 2 字节攻击增益，小端
        attack_b = attack.to_bytes(2, byteorder="big", signed=False)

        return heal_b + cooling_b + defense_b + neg_def_b + attack_b
