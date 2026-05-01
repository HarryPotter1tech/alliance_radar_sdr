from tcp_comm.tcp_comm import (
    tcp_gnuradio_signal_receiver,
    tcp_gnuradio_noise_key_receiver,
    tcp_datacenter_transmitter,
    tcp_datacenter_receiver,
)
from parser.gnuradio_frame_parser import (
    RoboMaster_Signal_Info,
    RoboMaster_Noise_Key,
)
from parser.datacenter_package_parser import RadarMarkProcess
import threading


def main():
    signal_info: RoboMaster_Signal_Info = RoboMaster_Signal_Info()
    noise_key: RoboMaster_Noise_Key = RoboMaster_Noise_Key()
    radar_mark_process: RadarMarkProcess = RadarMarkProcess()
    lock = threading.Lock()
    signal_thread = threading.Thread(
        target=tcp_gnuradio_signal_receiver, args=(signal_info, lock), daemon=True
    )
    noise_key_thread = threading.Thread(
        target=tcp_gnuradio_noise_key_receiver, args=(noise_key, lock), daemon=True
    )
    transmitter_thread = threading.Thread(
        target=tcp_datacenter_transmitter,
        args=(signal_info, noise_key, lock),
        daemon=True,
    )
    receiver_thread = threading.Thread(
        target=tcp_datacenter_receiver, args=(radar_mark_process, lock), daemon=True
    )
    signal_thread.start()
    noise_key_thread.start()
    transmitter_thread.start()
    receiver_thread.start()
    signal_thread.join()
    noise_key_thread.join()
    transmitter_thread.join()
    receiver_thread.join()


if __name__ == "__main__":
    main()
