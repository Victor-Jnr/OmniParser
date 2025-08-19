import os
import time
import threading
import logging
from typing import Optional

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

try:
    import pynvml
except Exception:  # pragma: no cover
    pynvml = None


class ResourceMonitor:
    """
    Background resource monitor that periodically logs container/system and process stats.
    """

    def __init__(self, interval_seconds: float = 2.0, stats_log_path: Optional[str] = None) -> None:
        self.interval_seconds = max(0.5, float(interval_seconds))
        self.stats_log_path = stats_log_path
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._logger = logging.getLogger(__name__)
        self._file_logger: Optional[logging.Logger] = None
        if stats_log_path:
            self._file_logger = logging.getLogger("resource_monitor")
            if not self._file_logger.handlers:
                handler = logging.FileHandler(stats_log_path, encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
                handler.setFormatter(formatter)
                self._file_logger.addHandler(handler)
                self._file_logger.setLevel(logging.INFO)

        if psutil is None:
            self._logger.warning("psutil is not available; resource monitoring will be limited.")

        # Verbosity toggles via env
        self._show_gpu = os.getenv('MONITOR_SHOW_GPU', 'true').lower() == 'true'
        self._show_net = os.getenv('MONITOR_SHOW_NET', 'true').lower() == 'true'

        self._gpu_available = False
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                self._gpu_available = True
            except Exception:
                self._gpu_available = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="ResourceMonitor", daemon=True)
        self._thread.start()
        self._logger.info("Resource monitor started with interval %.2fs", self.interval_seconds)

    def stop(self, timeout: float = 2.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        if self._gpu_available:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
        self._logger.info("Resource monitor stopped")

    def _log(self, message: str) -> None:
        if self._file_logger:
            self._file_logger.info(message)
        else:
            self._logger.info(message)

    def _read_cgroup_memory_limit_bytes(self) -> Optional[int]:
        # cgroup v1 and v2 paths
        paths = [
            "/sys/fs/cgroup/memory/memory.limit_in_bytes",
            "/sys/fs/cgroup/memory.max",
        ]
        for path in paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        raw = f.read().strip()
                        if raw.isdigit():
                            return int(raw)
                        if raw.lower() == 'max':
                            return None
                        # Some kernels return numbers with newlines
                        return int(raw)
            except Exception:
                continue
        return None

    def _gpu_stats(self) -> Optional[str]:
        if not self._gpu_available:
            return None
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            entries = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                entries.append(
                    f"gpu{idx}: mem_used={meminfo.used/1e6:.1f}MB/ {meminfo.total/1e6:.1f}MB, util={util.gpu}%"
                )
            return "; ".join(entries)
        except Exception:
            return None

    def _run(self) -> None:
        process = psutil.Process(os.getpid()) if psutil else None
        cgroup_limit = self._read_cgroup_memory_limit_bytes()
        while not self._stop_event.is_set():
            try:
                if psutil:
                    vm = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=None)
                    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0.0, 0.0, 0.0)
                    disk = psutil.disk_usage('/')
                    net = psutil.net_io_counters() if self._show_net else None

                    proc_mem = process.memory_info() if process else None
                    proc_cpu = process.cpu_percent(interval=None) if process else None

                    gpu = self._gpu_stats() if (self._show_gpu and self._gpu_available) else None

                    parts = [
                        f"cpu={cpu_percent:.1f}% load1={load_avg[0]:.2f}",
                        f"mem_used={vm.used/1e6:.1f}MB mem_avail={vm.available/1e6:.1f}MB mem_pct={vm.percent:.1f}%",
                        f"disk_used={disk.used/1e9:.2f}GB/{disk.total/1e9:.2f}GB ({disk.percent:.1f}%)",
                    ]
                    if net is not None:
                        parts.append(f"net_sent={net.bytes_sent/1e6:.1f}MB net_recv={net.bytes_recv/1e6:.1f}MB")
                    if proc_mem is not None:
                        parts.append(
                            f"proc_rss={proc_mem.rss/1e6:.1f}MB proc_vms={proc_mem.vms/1e6:.1f}MB"
                        )
                    if proc_cpu is not None:
                        parts.append(f"proc_cpu={proc_cpu:.1f}%")
                    if cgroup_limit is not None:
                        parts.append(f"cgroup_mem_limit={cgroup_limit/1e6:.1f}MB")
                    if gpu:
                        parts.append(gpu)

                    self._log(" | ".join(parts))
                else:
                    self._log("psutil not installed; limited resource stats")
            except Exception as e:
                self._logger.error("Resource monitor error: %s", e, exc_info=True)
            finally:
                time.sleep(self.interval_seconds)


