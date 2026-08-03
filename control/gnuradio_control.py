import importlib.util
import queue
import threading
import time
import traceback
from pathlib import Path

from control.gnuradio_config import build_config
from logs.event_logger import log, log_data, log_thread_start, log_thread_stop


GFSK_RX_PATH = Path(__file__).resolve().parent.parent / "gnu radio " / "GFSK_RX.py"

RETRY_BASE_DELAY = 1.0
RETRY_MAX_DELAY = 8.0


class GnuradioController:
    def __init__(
        self, shared_state: dict, lock: threading.Lock, poll_interval: float = 0.5
    ):
        self.shared_state = shared_state
        self.lock = lock
        self.poll_interval = poll_interval
        self._stopping = threading.Event()
        self._retry_attempt = 0
        self._retry_after = 0.0
        self.status_queue: "queue.Queue[str]" = queue.Queue()
        self._current_config: dict | None = None
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self, timeout: float = 15.0) -> None:
        """Request graceful shutdown and wait for the controller thread."""
        self._stopping.set()
        if self.thread.is_alive():
            self.thread.join(timeout)

    def current_config(self) -> dict | None:
        """Return the receiver config currently applied or being attempted.

        Safe to call from any thread; returns a copy.
        """
        if self._current_config is not None:
            return dict(self._current_config)
        return self._expected_config()

    def _read_state(self) -> tuple[str, str]:
        with self.lock:
            noise_grade = self.shared_state.get("noise_grade", "noise_1")
            side = self.shared_state.get("side", "red")
        return noise_grade, side

    def _load_module(self):
        spec = importlib.util.spec_from_file_location("GFSK_RX", GFSK_RX_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to load GFSK_RX module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _expected_config(self) -> dict:
        noise_grade, side = self._read_state()
        mode = "signal" if noise_grade == "noise_3" else "noise"
        return build_config(mode, side, noise_grade)

    def _retry_delay(self) -> float:
        self._retry_attempt += 1
        delay = min(
            RETRY_BASE_DELAY * (2 ** (self._retry_attempt - 1)), RETRY_MAX_DELAY
        )
        self._retry_after = time.monotonic() + delay
        return delay

    def _wait_retry(self) -> None:
        while not self._stopping.is_set():
            wait = self._retry_after - time.monotonic()
            if wait <= 0:
                return
            time.sleep(min(0.2, wait))

    def _close_flowgraph(self, tb) -> None:
        tb.stop()
        tb.wait()
        if hasattr(tb, "close"):
            tb.close()
        log("gnuradiocontrol", "stopped old flowgraph")

    def _report_status(self, text: str) -> None:
        self.status_queue.put(text)

    def _format_running_status(self, config: dict) -> str:
        mode = config["mode"]
        freq_mhz = config["frequency"] / 1e6
        if mode == "signal":
            return f"SDR 运行中 | 模式: signal | 频率: {freq_mhz:.3f} MHz"
        return (
            f"SDR 运行中 | 模式: noise | 等级: {self._read_state()[0]} "
            f"| 频率: {freq_mhz:.3f} MHz"
        )

    def _set_mode(self, config: dict) -> None:
        """Publish the active receiver mode (noise/signal) to shared state.

        The TCP frame receiver switches its parser based on this value.
        """
        with self.lock:
            self.shared_state["mode"] = config["mode"]

    def _attempt_start(self, module, config: dict, label: str):
        """Build+start the flowgraph; on failure log and back off."""
        try:
            module.CONFIG = config
            tb = module.GFSK_RX()
            tb.start()
            self._retry_attempt = 0
            self._retry_after = 0.0
            self._current_config = config
            self._set_mode(config)
            log_data("gnuradiocontrol", label, config)
            self._report_status(self._format_running_status(config))
            return tb
        except Exception as exc:
            delay = self._retry_delay()
            log(
                "gnuradiocontrol",
                f"{label} failed (attempt {self._retry_attempt}): {exc!r} "
                f"- retry in {delay:.1f}s\n{traceback.format_exc()}",
                tag="[error]",
            )
            self._report_status(
                f"SDR 启动失败，第 {self._retry_attempt} 次重试（{delay:.1f}s 后）"
            )
            return None

    def _poll_once(self, module, tb, current_config: dict):
        """Rebuild the flowgraph when the expected config changes."""
        try:
            expected = self._expected_config()
            if expected != current_config and time.monotonic() >= self._retry_after:
                log_data(
                    "gnuradiocontrol",
                    "config_changed",
                    {"from": current_config, "to": expected},
                )
                self._current_config = expected
                self._set_mode(expected)
                try:
                    self._close_flowgraph(tb)
                except Exception as exc:
                    log(
                        "gnuradiocontrol",
                        f"stop old flowgraph failed: {exc!r}",
                        tag="[error]",
                    )
                new_tb = self._attempt_start(module, expected, "flowgraph_rebuilt")
                if new_tb is not None:
                    return new_tb, expected
        except Exception as exc:
            log(
                "gnuradiocontrol",
                f"poll error: {exc!r}\n{traceback.format_exc()}",
                tag="[error]",
            )
        return tb, current_config

    def _run(self) -> None:
        thread_name = threading.current_thread().name
        log_thread_start("event", thread_name)
        try:
            module = self._load_module()
            log("event", "Loaded GFSK_RX module")

            # Initial start with retry until success or stop requested.
            config = self._expected_config()
            self._current_config = config
            self._set_mode(config)
            tb = None
            while tb is None and not self._stopping.is_set():
                tb = self._attempt_start(module, config, "flowgraph_started")
                if tb is None:
                    self._wait_retry()
            if self._stopping.is_set():
                return

            current_config = config
            while not self._stopping.is_set():
                tb, current_config = self._poll_once(module, tb, current_config)
                time.sleep(self.poll_interval)

            try:
                self._close_flowgraph(tb)
            except Exception as exc:
                log(
                    "gnuradiocontrol",
                    f"stop on shutdown failed: {exc!r}",
                    tag="[error]",
                )
        except Exception as exc:
            log(
                "gnuradiocontrol",
                f"controller fatal: {exc!r}\n{traceback.format_exc()}",
                tag="[error]",
            )
        finally:
            log_thread_stop("event", thread_name)
