import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TimingResult:
    name: str
    start_time: float
    end_time: Optional[float] = None
    elapsed: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def finish(self, success: bool = True, error: Optional[str] = None) -> None:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        self.success = success
        self.error = error

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "elapsed": round(self.elapsed, 6) if self.elapsed is not None else None,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class JobTimer:
    def __init__(self) -> None:
        self._results: list[TimingResult] = []

    def start(self, name: str, metadata: Optional[dict] = None) -> TimingResult:
        result = TimingResult(
            name=name,
            start_time=time.perf_counter(),
            metadata=metadata or {},
        )
        self._results.append(result)
        return result

    def results(self) -> list[TimingResult]:
        return list(self._results)

    def summary(self) -> dict:
        completed = [r for r in self._results if r.elapsed is not None]
        if not completed:
            return {"total_jobs": 0, "completed": 0, "failed": 0, "total_elapsed": 0.0}
        elapsed_values = [r.elapsed for r in completed]
        failed = [r for r in completed if not r.success]
        return {
            "total_jobs": len(self._results),
            "completed": len(completed),
            "failed": len(failed),
            "total_elapsed": round(sum(elapsed_values), 6),
            "min_elapsed": round(min(elapsed_values), 6),
            "max_elapsed": round(max(elapsed_values), 6),
            "avg_elapsed": round(sum(elapsed_values) / len(elapsed_values), 6),
        }
