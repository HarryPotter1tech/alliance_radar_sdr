from frame_generate import FrameGenerate
from message_value_generate import MessageValueGenerator
from noisekey_value_gengerate import NoiseKeyValueGenerator

__name__ = "__main__"
if __name__ == "__main__":
    message_value_generate = MessageValueGenerator()
    noise_key_value_generate = NoiseKeyValueGenerator()
    message_frame_generate = FrameGenerate(transmmit_mode=0)
    noise_key_frame_generate = FrameGenerate(transmmit_mode=1)
    message_package: bytes = message_value_generate.message_pack()
    noisekey_package: bytes = noise_key_value_generate.message_pack()
    noisekey_frame: bytes = noise_key_frame_generate.add(noisekey_package)
    with open("noisekey_package.bin", "wb") as f:
        f.write(noisekey_frame)
        print("Package written to noisekey_package.bin")
        print("Loading>>>")
    with open("noisekey_package.bin", "rb") as f:
        loaded_package = f.read()
        print("Loaded noisekey Package:", loaded_package)
        print("noisekey Package loaded successfully.")
        print("total package length:", len(loaded_package))
        print("Loading complete.")
    message_frame: bytes = message_frame_generate.add(message_package)
    with open("message_package.bin", "wb") as f:
        f.write(message_frame)
        print("Package written to message_package.bin")
        print("Loading>>>")
    with open("message_package.bin", "rb") as f:
        loaded_package = f.read()
        print("Loaded message Package:", loaded_package)
        print("message Package loaded successfully.")
        print("total package length:", len(loaded_package))
        print("Loading complete.")
