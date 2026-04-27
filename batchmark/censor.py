"""censor.py — redact or mask sensitive fields in TimingResult records."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult


_MASK = "***"


@dataclass
class CensoredResult:
    job_id: str
    success: bool
    duration: Optional[float]
    error: Optional[str]
    metadata: Dict[str, object]

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "success": self.success,
            "duration": self.duration,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class CensorReport:
    results: List[CensoredResult] = field(default_factory=list)
    redacted_count: int = 0

    def to_dict(self) -> dict:
        return {
            "redacted_count": self.redacted_count,
            "results": [r.to_dict() for r in self.results],
        }


def _mask_job_id(result: TimingResult) -> str:
    """Replace job_id with masked value."""
    return _MASK


def _mask_error(error: Optional[str]) -> Optional[str]:
    return _MASK if error else None


def censor_results(
    results: List[TimingResult],
    *,
    mask_job_id: bool = False,
    mask_error: bool = False,
    redact_metadata_keys: Optional[List[str]] = None,
    custom_job_id_fn: Optional[Callable[[TimingResult], str]] = None,
) -> CensorReport:
    """Apply censoring rules to a list of TimingResult records.

    Args:
        results: raw timing results.
        mask_job_id: replace every job_id with '***'.
        mask_error: replace error messages with '***'.
        redact_metadata_keys: list of metadata keys whose values should be masked.
        custom_job_id_fn: optional callable that receives a result and returns
            the (possibly transformed) job_id string.
    """
    redact_keys = set(redact_metadata_keys or [])
    censored: List[CensoredResult] = []
    redacted_count = 0

    for r in results:
        changed = False

        if custom_job_id_fn is not None:
            job_id = custom_job_id_fn(r)
            changed = True
        elif mask_job_id:
            job_id = _MASK
            changed = True
        else:
            job_id = r.job_id

        error = r.error
        if mask_error and error is not None:
            error = _MASK
            changed = True

        meta: Dict[str, object] = dict(getattr(r, "metadata", {}) or {})
        for key in redact_keys:
            if key in meta:
                meta[key] = _MASK
                changed = True

        if changed:
            redacted_count += 1

        censored.append(
            CensoredResult(
                job_id=job_id,
                success=r.success,
                duration=r.duration,
                error=error,
                metadata=meta,
            )
        )

    return CensorReport(results=censored, redacted_count=redacted_count)
