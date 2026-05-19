import importlib.util
import threading
import time
from pathlib import Path

from PyQt5 import Qt

from logs.event_logger import log, log_data, log_thread_start, log_thread_stop


GFSK_NOISE_PATH = (
    Path(__file__).resolve().parent.parent / "gnu radio " / "GFSK_Receive_Noise.py"
)
GFSK_SIGNAL_PATH = (
    Path(__file__).resolve().parent.parent / "gnu radio " / "GFSK_Receiver_Signal.py"
)


class GnuradioController:
    def __init__(
        self, shared_state: dict, lock: threading.Lock, poll_interval: float = 0.5
    ):
        self.shared_state = shared_state
        self.lock = lock
        self.poll_interval = poll_interval
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _read_state(self) -> tuple[str, str, int]:
        with self.lock:
            noise_grade = self.shared_state.get("noise_grade", "noise_1")
            enemy_side = self.shared_state.get("enemy_side", "red")
            signal_frequency = int(self.shared_state.get("signal_frequency", 433200000))
        return noise_grade, enemy_side, signal_frequency

    def _run(self) -> None:
        thread_name = threading.current_thread().name
        log_thread_start("event", thread_name)
        noise_spec = importlib.util.spec_from_file_location(
            "GFSK_Receive_Noise", GFSK_NOISE_PATH
        )
        if noise_spec is None or noise_spec.loader is None:
            raise RuntimeError("Failed to load GFSK noise receiver module")
        log("event", "Loaded GFSK noise receiver module (noise-only mode)")
        noise_module = importlib.util.module_from_spec(noise_spec)
        noise_spec.loader.exec_module(noise_module)

        qapp = Qt.QApplication([])
        noise_tb = noise_module.GFSK_Receive_Noise()

        # In noise-only mode we do not start or load the signal receiver.
        # Also treat any outward-facing signal info as zero.
        noise_grade, enemy_side, _ = self._read_state()
        signal_frequency = 0
        noise_tb.set_enemyside(enemy_side)
        noise_tb.set_noise_grade_chooser(noise_grade)
        noise_tb.set_signal_frequency(signal_frequency)

        noise_tb.start()
        noise_tb.show()

        last_noise_grade = noise_grade
        last_enemy_side = enemy_side
        last_signal_frequency = signal_frequency
        # Record initial state; for noise-only branch signal info is 0
        log_data(
            "gnuradiocontrol",
            "initial_state",
            {
                "noise_grade": noise_grade,
                "enemy_side": enemy_side,
                "signal_frequency": 0,
            },
        )

        def poll():
            nonlocal last_noise_grade, last_enemy_side, last_signal_frequency
            noise_grade, enemy_side, _ = self._read_state()
            if noise_grade != last_noise_grade:
                noise_tb.set_noise_grade_chooser(noise_grade)
                last_noise_grade = noise_grade
                log_data("gnuradiocontrol", "noise_grade_changed", noise_grade)
            if enemy_side != last_enemy_side:
                noise_tb.set_enemyside(enemy_side)
                last_enemy_side = enemy_side
                log_data("gnuradiocontrol", "enemy_side_changed", enemy_side)
            # In noise-only mode we ignore dynamic signal frequency changes
            # and always treat sent signal info as 0.

        timer = Qt.QTimer()
        timer.timeout.connect(poll)
        timer.start(int(self.poll_interval * 1000))

        try:
            qapp.exec_()
        finally:
            log_thread_stop("event", thread_name)
