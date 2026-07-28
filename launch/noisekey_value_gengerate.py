import random

from crc_table import crc_8_table, crc_16_table


class NoiseKeyValueGenerator:
    def __init__(
        self,
        set_mode: str = "random",  # manual or random
        # cmd_id=0x0a01
        cmd_id_6: int = 0x0A06,
        sdr_behavior_: int = 0,
        key_1: int = 1,
        key_2: int = 2,
        key_3: int = 3,
        key_4: int = 4,
        key_5: int = 5,
        key_6: int = 6,
    ):
        self.set_mode = set_mode
        # frame_header
        # SOF(1 byte) + data_length(2 byte) + seq(1 byte)+crc8(1 byte)
        self.SOF = 0xA5
        self.data_length = 0x00
        self.seq = 0x00
        self._crc8 = 0x00

        # cmd_id
        self.cmd_id_6 = cmd_id_6.to_bytes(2, byteorder="big")
        self.key_1 = key_1.to_bytes(1, byteorder="big")
        self.key_2 = key_2.to_bytes(1, byteorder="big")
        self.key_3 = key_3.to_bytes(1, byteorder="big")
        self.key_4 = key_4.to_bytes(1, byteorder="big")
        self.key_5 = key_5.to_bytes(1, byteorder="big")
        self.key_6 = key_6.to_bytes(1, byteorder="big")
        self.sdr_behavior = sdr_behavior_.to_bytes(1, byteorder="big")

        # mode choice&&data
        if self.set_mode == "manual":
            print("Manual values generate>>>.")
            print("self.cmd_id_6:", self.cmd_id_6)
            print("self.sdr_behavior:", self.sdr_behavior)
            print("self.key_1:", self.key_1)
            print("self.key_2:", self.key_2)
            print("self.key_3:", self.key_3)
            print("self.key_4:", self.key_4)
            print("self.key_5:", self.key_5)
            print("self.key_6:", self.key_6)
            print("Manual values printed successfully.")

        if self.set_mode == "random":
            print("Random values generate>>>.")
            self.sdr_behavior = random.randint(0, 2).to_bytes(1, byteorder="big")
            self.key_1 = random.randint(0, 10).to_bytes(1, byteorder="big")
            self.key_2 = random.randint(0, 10).to_bytes(1, byteorder="big")
            self.key_3 = random.randint(0, 10).to_bytes(1, byteorder="big")
            self.key_4 = random.randint(0, 10).to_bytes(1, byteorder="big")
            self.key_5 = random.randint(0, 10).to_bytes(1, byteorder="big")
            self.key_6 = random.randint(0, 10).to_bytes(1, byteorder="big")
            print("self.cmd_id_6:", self.cmd_id_6)
            print("self.sdr_behavior:", self.sdr_behavior)
            print("self.key_1:", self.key_1)
            print("self.key_2:", self.key_2)
            print("self.key_3:", self.key_3)
            print("self.key_4:", self.key_4)
            print("self.key_5:", self.key_5)
            print("self.key_6:", self.key_6)
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
        # Protocol-defined 0x0A06 payload is only the 6-byte key.
        payload = (
            self.key_1 + self.key_2 + self.key_3 + self.key_4 + self.key_5 + self.key_6
        )
        self.message_package = self._build_frame(self.cmd_id_6, payload)
        print(len(self.message_package))
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
        return (
            frame_wo_crc16
            + crc16_val
            + b"\x01" * (15 - len(frame_wo_crc16 + crc16_val) % 15)
        )
