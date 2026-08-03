import os
import threading
import time
from datetime import datetime
from pprint import pformat


LOGS_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(LOGS_DIR, exist_ok=True)

# One timestamped session folder per launch; all business logs of a run
# are written inside it (e.g. logs/20260803_145712/event.log).
_session_dir: str | None = None
_session_lock = threading.Lock()

# per-module locks to avoid interleaved writes
_locks: dict[str, threading.Lock] = {}


def _get_lock(module: str) -> threading.Lock:
    if module not in _locks:
        _locks[module] = threading.Lock()
    return _locks[module]


def _session_dir_path() -> str:
    """Return the session folder, creating it once per launch on first use."""
    global _session_dir
    if _session_dir is None:
        with _session_lock:
            if _session_dir is None:
                _session_dir = os.path.join(
                    LOGS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S")
                )
                os.makedirs(_session_dir, exist_ok=True)
    return _session_dir


def _log_path(module: str) -> str:
    filename = f"{module}.log"
    return os.path.join(_session_dir_path(), filename)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(module: str, message: str, tag: str | None = None) -> None:
    """Append a timestamped message to module-specific log file.

    Args:
        module: short module name used to name the log file (e.g. 'unity', 'sdr_signal').
        message: message text to append.
        tag: optional tag string to include (e.g. '[unity]').
    """
    path = _log_path(module)
    line = f"[{_timestamp()}] {tag or ''} {message}\n"
    lock = _get_lock(module)
    with lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    if module in {"event", "gnuradiocontrol"}:
        echo_line = f"[{module}] {tag or ''} {message}".strip()
        print(echo_line, flush=True)


# rate-limit bookkeeping: (module, key) -> last monotonic time
_rate_limits: dict[tuple[str, str], float] = {}
_rate_lock = threading.Lock()


def log_rate_limited(
    module: str,
    message: str,
    tag: str | None = None,
    interval_sec: float = 5.0,
    key: str | None = None,
) -> None:
    """Log at most once per interval_sec for the same (module, key).

    High-frequency loops (reconnects, repeated failures) use this to
    keep disk pressure low while still recording the event.
    """
    now = time.monotonic()
    limit_key = (module, key if key is not None else message)
    with _rate_lock:
        last = _rate_limits.get(limit_key, 0.0)
        if now - last < interval_sec:
            return
        _rate_limits[limit_key] = now
    log(module, message, tag=tag)


def _stringify_data(data) -> str:
    if isinstance(data, (bytes, bytearray)):
        return data.hex(" ")
    if isinstance(data, dict):
        return pformat(data, width=120, sort_dicts=True)
    if hasattr(data, "__dict__"):
        return pformat(getattr(data, "__dict__"), width=120, sort_dicts=True)
    return pformat(data, width=120, sort_dicts=True)


def log_data(module: str, label: str, data, tag: str | None = None) -> None:
    """Append a structured data snapshot to the module-specific log file."""
    log(module, f"{label}: {_stringify_data(data)}", tag=tag)


def log_thread_start(module: str, thread_name: str) -> None:
    log(module, f"Thread '{thread_name}' started")


def log_thread_stop(module: str, thread_name: str) -> None:
    log(module, f"Thread '{thread_name}' stopped")
