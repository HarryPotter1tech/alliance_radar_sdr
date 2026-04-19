from frame_generate import FrameGenerate
from message_value_generate import MessageValueGenerator

__name__ = "__main__"
if __name__ == "__main__":
    message_value_generate = MessageValueGenerator()
    frame_generate = FrameGenerate(transmmit_mode=0)
    message_package: bytes = message_value_generate.message_pack()
    package: bytes = frame_generate.add(message_package)
    with open("package.bin", "wb") as f:
        f.write(package)
        print("Package written to package.bin")
        print("Loading>>>")
    with open("package.bin", "rb") as f:
        loaded_package = f.read()
        print("Loaded Package:", loaded_package)
        print("Package loaded successfully.")
        print("total package length:", len(loaded_package))
        print("Loading complete.")
