class FrameGenerate:
    def __init__(self, transmmit_mode=0):
        self.transmmit_mode = transmmit_mode
        # if transmmit_mode == 0 mean transmmit signal
        # if transmmit_mode == 1 mean transmmit noise
        self.header_1: int = 0x000F
        self.header_2: int = 0x000F
        self.access_codes: list = [0x2F6F4C74B914492E, 0x16E8D377151C712D]
        self.access_code = self.access_codes[self.transmmit_mode]

        self.access_code = self.access_code.to_bytes(8, byteorder="big")
        # transfomer access_code to big order
        self.header_1 = self.header_1.to_bytes(2, byteorder="big")
        # transfomer header_1 to big order
        self.header_2 = self.header_2.to_bytes(2, byteorder="big")
        # transfomer header_2 to big order

    def add(self, input_items: bytes) -> bytes:
        payload = input_items
        package_header = self.access_code + self.header_1 + self.header_2
        package: bytes = b""
        # package is the tatal package list of unit of access_code + header1 + header2 + payload
        for i in range(0, len(payload), 15):
            chunk = payload[i : i + 15]
            package += package_header + chunk
        output_items = package
        return output_items
