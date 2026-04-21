import socket
from frame_parser import FrameParser
from frame_parser import RoboMasterInfo

print("Connecting to gnu radio receiver server…")
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("127.0.0.1", 2000)
tcp_socket.connect(server_address)
print("Connected to gnu radio receiver server.")
buffer: bytes = b""
message_package: bytes = b""
robomasterinfo: RoboMasterInfo = RoboMasterInfo()
frameparser = FrameParser()
while True:
    try:
        chunk = tcp_socket.recv(1024)
    except socket.error as e:
        print("Error receiving data: ", e)
        continue
    buffer += chunk
    if len(buffer) >= 200:
        print("Received data: ", buffer)
        robomasterinfo = frameparser.payload_parse(buffer)
        print("Parse message package complete, robomasterinfo: ", robomasterinfo)
        buffer = b""
