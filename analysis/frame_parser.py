from typing import Union
from dataclasses import dataclass


@dataclass
class RoboMasterInfo:
    cmd_id_1: int = 0x0A01
    hero_position: list[int] = [0, 0]
    engineer_position: list[int] = [0, 0]
    infentry_position_1: list[int] = [0, 0]
    infentry_position_2: list[int] = [0, 0]
    drone_position: list[int] = [0, 0]
    sentinel_position: list[int] = [0, 0]

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
    hero_gain: list[int] = [0, 0, 0, 0, 0]
    engineer_gain: list[int] = [0, 0, 0, 0, 0]
    infentry_gain_1: list[int] = [0, 0, 0, 0, 0]
    infentry_gain_2: list[int] = [0, 0, 0, 0, 0]
    sentinel_gain: list[int] = [0, 0, 0, 0, 0]
    sentinel_posture: int = 0


FrameParseResult = Union[bool, RoboMasterInfo]


class FrameParser(RoboMasterInfo):
    # fmt: off
    crc_8_table: list[int] = [
            0x00,0x5e,0xbc,0xe2,0x61,0x3f,0xdd,0x83,0xc2,0x9c,0x7e,0x20,0xa3,0xfd,0x1f,0x41,
            0x9d,0xc3,0x21,0x7f,0xfc,0xa2,0x40,0x1e,0x5f,0x01,0xe3,0xbd,0x3e,0x60,0x82,0xdc,
            0x23,0x7d,0x9f,0xc1,0x42,0x1c,0xfe,0xa0,0xe1,0xbf,0x5d,0x03,0x80,0xde,0x3c,0x62,
            0xbe,0xe0,0x02,0x5c,0xdf,0x81,0x63,0x3d,0x7c,0x22,0xc0,0x9e,0x1d,0x43,0xa1,0xff,
            0x46,0x18,0xfa,0xa4,0x27,0x79,0x9b,0xc5,0x84,0xda,0x38,0x66,0xe5,0xbb,0x59,0x07,
            0xdb,0x85,0x67,0x39,0xba,0xe4,0x06,0x58,0x19,0x47,0xa5,0xfb,0x78,0x26,0xc4,0x9a,
            0x65,0x3b,0xd9,0x87,0x04,0x5a,0xb8,0xe6,0xa7,0xf9,0x1b,0x45,0xc6,0x98,0x7a,0x24,
            0xf8,0xa6,0x44,0x1a,0x99,0xc7,0x25,0x7b,0x3a,0x64,0x86,0xd8,0x5b,0x05,0xe7,0xb9,
            0x8c,0xd2,0x30,0x6e,0xed,0xb3,0x51,0x0f,0x4e,0x10,0xf2,0xac,0x2f,0x71,0x93,0xcd,
            0x11,0x4f,0xad,0xf3,0x70,0x2e,0xcc,0x92,0xd3,0x8d,0x6f,0x31,0xb2,0xec,0x0e,0x50,
            0xaf,0xf1,0x13,0x4d,0xce,0x90,0x72,0x2c,0x6d,0x33,0xd1,0x8f,0x0c,0x52,0xb0,0xee,
            0x32,0x6c,0x8e,0xd0,0x53,0x0d,0xef,0xb1,0xf0,0xae,0x4c,0x12,0x91,0xcf,0x2d,0x73,
            0xca,0x94,0x76,0x28,0xab,0xf5,0x17,0x49,0x08,0x56,0xb4,0xea,0x69,0x37,0xd5,0x8b,
            0x57,0x09,0xeb,0xb5,0x36,0x68,0x8a,0xd4,0x95,0xcb,0x29,0x77,0xf4,0xaa,0x48,0x16,
            0xe9,0xb7,0x55,0x0b,0x88,0xd6,0x34,0x6a,0x2b,0x75,0x97,0xc9,0x4a,0x14,0xf6,0xa8,
            0x74,0x2a,0xc8,0x96,0x15,0x4b,0xa9,0xf7,0xb6,0xe8,0x0a,0x54,0xd7,0x89,0x6b,0x35
            ]
    crc_16_table: list[int] =  [
            0x0000,0x1189,0x2312,0x329b,0x4624,0x57ad,0x6536,0x74bf,0x8c48,0x9dc1,0xaf5a,0xbed3,0xca6c,0xdbe5,0xe97e,0xf8f7,
            0x1081,0x0108,0x3393,0x221a,0x56a5,0x472c,0x75b7,0x643e,0x9cc9,0x8d40,0xbfdb,0xae52,0xdaed,0xcb64,0xf9ff,0xe876,
            0x2102,0x308b,0x0210,0x1399,0x6726,0x76af,0x4434,0x55bd,0xad4a,0xbcc3,0x8e58,0x9fd1,0xeb6e,0xfae7,0xc87c,0xd9f5,
            0x3183,0x200a,0x1291,0x0318,0x77a7,0x662e,0x54b5,0x453c,0xbdcb,0xac42,0x9ed9,0x8f50,0xfbef,0xea66,0xd8fd,0xc974,
            0x4204,0x538d,0x6116,0x709f,0x0420,0x15a9,0x2732,0x36bb,0xce4c,0xdfc5,0xed5e,0xfcd7,0x8868,0x99e1,0xab7a,0xbaf3,
            0x5285,0x430c,0x7197,0x601e,0x14a1,0x0528,0x37b3,0x263a,0xdecd,0xcf44,0xfddf,0xec56,0x98e9,0x8960,0xbbfb,0xaa72,
            0x6306,0x728f,0x4014,0x519d,0x2522,0x34ab,0x0630,0x17b9,0xef4e,0xfec7,0xcc5c,0xddd5,0xa96a,0xb8e3,0x8a78,0x9bf1,
            0x7387,0x620e,0x5095,0x411c,0x35a3,0x242a,0x16b1,0x0738,0xffcf,0xee46,0xdcdd,0xcd54,0xb9eb,0xa862,0x9af9,0x8b70,
            0x8408,0x9581,0xa71a,0xb693,0xc22c,0xd3a5,0xe13e,0xf0b7,0x0840,0x19c9,0x2b52,0x3adb,0x4e64,0x5fed,0x6d76,0x7cff,
            0x9489,0x8500,0xb79b,0xa612,0xd2ad,0xc324,0xf1bf,0xe036,0x18c1,0x0948,0x3bd3,0x2a5a,0x5ee5,0x4f6c,0x7df7,0x6c7e,
            0xa50a,0xb483,0x8618,0x9791,0xe32e,0xf2a7,0xc03c,0xd1b5,0x2942,0x38cb,0x0a50,0x1bd9,0x6f66,0x7eef,0x4c74,0x5dfd,
            0xb58b,0xa402,0x9699,0x8710,0xf3af,0xe226,0xd0bd,0xc134,0x39c3,0x284a,0x1ad1,0x0b58,0x7fe7,0x6e6e,0x5cf5,0x4d7c,
            0xc60c,0xd785,0xe51e,0xf497,0x8028,0x91a1,0xa33a,0xb2b3,0x4a44,0x5bcd,0x6956,0x78df,0x0c60,0x1de9,0x2f72,0x3efb,
            0xd68d,0xc704,0xf59f,0xe416,0x90a9,0x8120,0xb3bb,0xa232,0x5ac5,0x4b4c,0x79d7,0x685e,0x1ce1,0x0d68,0x3ff3,0x2e7a,
            0xe70e,0xf687,0xc41c,0xd595,0xa12a,0xb0a3,0x82b9,0x9330,0x6b46,0x7acf,0x4854,0x59dd,0x2d62,0x3ceb,0x0e70,0x1ff9,
            0xf78f,0xe606,0xd49d,0xc514,0xb1ab,0xa022,0x92b9,0x8330,0x7bc7,0x6a4e,0x58d5,0x495c,0x3de3,0x2c6a,0x1ef1,0x0f78,
        ]
    # fmt: on
    def __init__(self, receive_mode=0):
        self.receive_mode = receive_mode
        # if receive_mode == 0 mean receive signal
        # if receive_mode == 1 mean receive noise
        self.header_1: int = 0x000F
        self.header_2: int = 0x000F
        self.access_codes: list = [0x2F6F4C74B914492E, 0x16E8D377151C712D]
        self.access_code = self.access_codes[self.receive_mode]
        self.access_code = self.access_code.to_bytes(8, byteorder="big")
        self.header_1 = self.header_1.to_bytes(2, byteorder="big")
        self.header_2 = self.header_2.to_bytes(2, byteorder="big")
        self.frame_header = self.access_code + self.header_1 + self.header_2
        self.buffer: bytes = b""
        self.pre_buffer: bytes = b""
        self.message_package: bytes = b""
        # store the broken frame header in last buffer, and add it to the head of next buffer
        self.frame_pointers: list[int] = []
        # a list record the pointer of frame header in buffer
        self.hasframe_pointer: int = -1
        # a pointer record the position of frame header in buffer, if -1 mean no frame header in buffer
        self.frame_broken: int = -1
        # a pointer record the position of frame header in buffer, if 0 mean frame header is complete in buffer, if 1 mean frame header is broken in buffer

    def find_frame_header(self, input_items: bytes) -> int:
        self.buffer = self.pre_buffer + input_items[:]
        for i in range(0, len(input_items), 27):
            if input_items[i : i + 12] == self.frame_header:
                self.frame_pointers.append(i)
        if len(self.frame_pointers) == 0:
            return -1
        bufferlen = len(self.buffer)
        maxframepointer = max(self.frame_pointers)
        minframepointer = min(self.frame_pointers)
        if maxframepointer + 27 > bufferlen:
            self.frame_broken = 1
            self.hasframe_pointer = minframepointer
            self.pre_buffer = self.buffer[-self.frame_broken :]
            # maintain the broken frame header in pre_buffer
        else:
            self.frame_broken = -1
            self.hasframe_pointer = minframepointer
            self.pre_buffer = self.buffer[maxframepointer + 27 :]
            # maintain the complete frame header in pre_buffer
            return 0

    def frame_payload_link(self) -> bytes:
        if self.frame_broken == -1:
            for i in range(0, len(self.frame_pointers)):
                self.message_package += self.buffer[
                    self.frame_pointers[i] + 12 : self.frame_pointers[i] + 27
                ]
        else:
            for i in range(0, len(self.frame_pointers) - 1):
                self.message_package += self.buffer[
                    self.frame_pointers[i] + 12 : self.frame_pointers[i] + 27
                ]
        # extract the payload from buffer and store it in message_package
        return self.message_package

    def payload_parse(self) -> RoboMasterInfo:
        if self.message_package == b"":
            return False
        # if message_package is empty, return False
        info = RoboMasterInfo()
        for i in range(0, len(self.message_package), 27):
            cmd_id = int.from_bytes(self.message_package[i : i + 2], byteorder="big")
            if cmd_id == info.cmd_id_1:
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
                    self.message_package[i + 18 : i + 20], byteorder="big", signed=True
                )
                info.drone_position[1] = int.from_bytes(
                    self.message_package[i + 20 : i + 22], byteorder="big", signed=True
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
                info.occupation_status = self.message_package[i + 6 : i + 12]
            elif cmd_id == info.cmd_id_5:
                info.hero_gain[0] = int.from_bytes(
                    self.message_package[i + 2 : i + 3], byteorder="big"
                )  # 1 byte
                info.hero_gain[1] = int.from_bytes(
                    self.message_package[i + 3 : i + 5], byteorder="little"
                )  # 2 byte
                info.hero_gain[2] = int.from_bytes(
                    self.message_package[i + 5 : i + 6], byteorder="big"
                )  # 1 byte
                info.hero_gain[3] = int.from_bytes(
                    self.message_package[i + 6 : i + 7], byteorder="big"
                )  # 1 byte
                info.hero_gain[4] = int.from_bytes(
                    self.message_package[i + 7 : i + 9], byteorder="little"
                )  # 2 byte
                info.engineer_gain[0] = int.from_bytes(
                    self.message_package[i + 9 : i + 10], byteorder="big"
                )  # 1 byte
                info.engineer_gain[1] = int.from_bytes(
                    self.message_package[i + 10 : i + 12], byteorder="little"
                )  # 2 byte
                info.engineer_gain[2] = int.from_bytes(
                    self.message_package[i + 12 : i + 13], byteorder="big"
                )  # 1 byte
                info.engineer_gain[3] = int.from_bytes(
                    self.message_package[i + 13 : i + 14], byteorder="big"
                )  # 1 byte
                info.engineer_gain[4] = int.from_bytes(
                    self.message_package[i + 14 : i + 16], byteorder="little"
                )  # 2 byte
                info.infentry_gain_1[0] = int.from_bytes(
                    self.message_package[i + 16 : i + 17], byteorder="big"
                )  # 1 byte
                info.infentry_gain_1[1] = int.from_bytes(
                    self.message_package[i + 17 : i + 19], byteorder="little"
                )  # 2 byte
                info.infentry_gain_1[2] = int.from_bytes(
                    self.message_package[i + 19 : i + 20], byteorder="big"
                )  # 1 byte
                info.infentry_gain_1[3] = int.from_bytes(
                    self.message_package[i + 20 : i + 21], byteorder="big"
                )  # 1 byte
                info.infentry_gain_1[4] = int.from_bytes(
                    self.message_package[i + 21 : i + 23], byteorder="little"
                )  # 2 byte
                info.infentry_gain_2[0] = int.from_bytes(
                    self.message_package[i + 23 : i + 24], byteorder="big"
                )  # 1 byte
                info.infentry_gain_2[1] = int.from_bytes(
                    self.message_package[i + 24 : i + 26], byteorder="little"
                )  # 2 byte
                info.infentry_gain_2[2] = int.from_bytes(
                    self.message_package[i + 26 : i + 27], byteorder="big"
                )  # 1 byte
                info.infentry_gain_2[3] = int.from_bytes(
                    self.message_package[i + 27 : i + 28], byteorder="big"
                )  # 1 byte
                info.infentry_gain_2[4] = int.from_bytes(
                    self.message_package[i + 28 : i + 30], byteorder="little"
                )  # 2 byte
                info.sentinel_gain[0] = int.from_bytes(
                    self.message_package[i + 30 : i + 31], byteorder="big"
                )  # 1 byte
                info.sentinel_gain[1] = int.from_bytes(
                    self.message_package[i + 31 : i + 33], byteorder="little"
                )  # 2 byte
                info.sentinel_gain[2] = int.from_bytes(
                    self.message_package[i + 33 : i + 34], byteorder="big"
                )  # 1 byte
                info.sentinel_gain[3] = int.from_bytes(
                    self.message_package[i + 34 : i + 35], byteorder="big"
                )  # 1 byte
                info.sentinel_gain[4] = int.from_bytes(
                    self.message_package[i + 35 : i + 37], byteorder="little"
                )  # 2 byte
                info.sentinel_posture = int.from_bytes(
                    self.message_package[i + 37 : i + 38], byteorder="big"
                )  # 1 byte
        return info
