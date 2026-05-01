from typing import Union
from dataclasses import dataclass


@dataclass
class RadarMarkProcess:
    cmd_id: int = 0x020C
    IsOpponentHeroDebuffed: bool = False
    IsOpponentEngineerDebuffed: bool = False
    IsOpponentInfantry3Debuffed: bool = False
    IsOpponentInfantry4Debuffed: bool = False
    IsOpponentAerialMarked: bool = False
    IsOpponentSentryDebuffed: bool = False
    IsAllyHeroMarked: bool = False
    IsAllyEngineerMarked: bool = False
    IsAllyInfantry3Marked: bool = False
    IsAllyInfantry4Marked: bool = False
    IsAllyAerialMarked: bool = False
    IsAllySentryMarked: bool = False


PackageParseResult = Union[RadarMarkProcess, None]


class PackageParser:
    def __init__(self):
        self.message_package: bytes = b""

    def package_parse(self, input_data: bytes) -> PackageParseResult:
        self.message_package = input_data
        if self.message_package is None or len(self.message_package) < 12:
            return None
        radarmarkerprocess = RadarMarkProcess()
        for i in range(0, len(self.message_package), 1):
            cmd_id = int.from_bytes(self.message_package[i : i + 2], byteorder="big")
            if cmd_id == radarmarkerprocess.cmd_id:
                return RadarMarkProcess(
                    IsOpponentHeroDebuffed=bool(self.message_package[0] & 0x01),
                    IsOpponentEngineerDebuffed=bool(self.message_package[0] & 0x02),
                    IsOpponentInfantry3Debuffed=bool(self.message_package[0] & 0x04),
                    IsOpponentInfantry4Debuffed=bool(self.message_package[0] & 0x08),
                    IsOpponentAerialMarked=bool(self.message_package[0] & 0x10),
                    IsOpponentSentryDebuffed=bool(self.message_package[0] & 0x20),
                    IsAllyHeroMarked=bool(self.message_package[1] & 0x01),
                    IsAllyEngineerMarked=bool(self.message_package[1] & 0x02),
                    IsAllyInfantry3Marked=bool(self.message_package[1] & 0x04),
                    IsAllyInfantry4Marked=bool(self.message_package[1] & 0x08),
                    IsAllyAerialMarked=bool(self.message_package[1] & 0x10),
                    IsAllySentryMarked=bool(self.message_package[1] & 0x20),
                )
