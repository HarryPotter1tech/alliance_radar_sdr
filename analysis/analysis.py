import zmq
from frame_parser import FrameParser
from frame_parser import RoboMasterInfo

context = zmq.Context()
print("Connecting to gnu radio receiver server…")
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5555")
print("Connected to gnu radio receiver server.")
print("Requesting data from gnu radio receiver server…")
buffer: bytes = b""
message_package: bytes = b""
robomasterinfo: RoboMasterInfo = RoboMasterInfo()
frameparser = FrameParser(receive_mode=0)
while True:
    buffer = socket.recv()
    frameparser.find_frame_header(buffer)
    if frameparser.hasframe_pointer != -1:
        print("Frame header found at position: ", frameparser.hasframe_pointer)
        message_package = frameparser.frame_payload_link()
        print(
            "link frame payload complete, message package length: ",
            len(message_package),
        )
        robomasterinfo = frameparser.payload_parse()
        print("Parse message package complete, robomasterinfo: ", robomasterinfo)
