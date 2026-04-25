"""cutter.py — slice a result list into fixed-size pages."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class Page:
    index: int          # 0-based page number
    results: List[TimingResult] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.results)

    def to_dict(self) -> dict:
        return {
            "page": self.index,
            "count": self.count,
            "results": [
                {"job_id": r.job_id, "duration": r.duration, "success": r.success}
                for r in self.results
            ],
        }


@dataclass
class CutReport:
    pages: List[Page] = field(default_factory=list)
    page_size: int = 10
    total: int = 0

    @property
    def page_count(self) -> int:
        return len(self.pages)

    def get(self, index: int) -> Optional[Page]:
        """Return page by 0-based index, or None if out of range."""
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None

    def to_dict(self) -> dict:
        return {
            "page_size": self.page_size,
            "total": self.total,
            "page_count": self.page_count,
            "pages": [p.to_dict() for p in self.pages],
        }


def cut_results(results: List[TimingResult], page_size: int = 10) -> CutReport:
    """Slice *results* into pages of *page_size* entries each."""
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    pages: List[Page] = []
    for i in range(0, max(1, len(results)), page_size):
        chunk = results[i : i + page_size]
        if not chunk and i > 0:
            break
        pages.append(Page(index=len(pages), results=chunk))

    return CutReport(pages=pages, page_size=page_size, total=len(results))
