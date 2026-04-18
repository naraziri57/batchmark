"""CPU and memory profiling helpers for batch job runs."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import resource
    _HAS_RESOURCE = True
except ImportError:
    _HAS_RESOURCE = False


@dataclass
class ProfileSnapshot:
    job_id: str
    wall_time: float
    cpu_time: float
    peak_memory_kb: Optional[int] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "wall_time": round(self.wall_time, 6),
            "cpu_time": round(self.cpu_time, 6),
            "peak_memory_kb": self.peak_memory_kb,
            "extra": self.extra,
        }


class Profiler:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self._wall_start: Optional[float] = None
        self._cpu_start: Optional[float] = None

    def start(self) -> None:
        self._wall_start = time.perf_counter()
        self._cpu_start = time.process_time()

    def stop(self) -> ProfileSnapshot:
        if self._wall_start is None or self._cpu_start is None:
            raise RuntimeError("Profiler.stop() called before start()")
        wall = time.perf_counter() - self._wall_start
        cpu = time.process_time() - self._cpu_start
        mem = _peak_memory_kb()
        return ProfileSnapshot(
            job_id=self.job_id,
            wall_time=wall,
            cpu_time=cpu,
            peak_memory_kb=mem,
        )

    def __enter__(self) -> "Profiler":
        self.start()
        return self

    def __exit__(self, *_) -> None:
        self._snapshot = self.stop()

    @property
    def snapshot(self) -> ProfileSnapshot:
        if not hasattr(self, "_snapshot"):
            raise RuntimeError("Profiler context not yet exited")
        return self._snapshot


def _peak_memory_kb() -> Optional[int]:
    if not _HAS_RESOURCE:
        return None
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux returns KB; macOS returns bytes
    if os.uname().sysname == "Darwin":
        return usage // 1024
    return usage
