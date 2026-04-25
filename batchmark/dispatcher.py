"""Dispatch results to multiple handlers based on routing rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from batchmark.timer import TimingResult


RouteFn = Callable[[TimingResult], Optional[str]]


@dataclass
class DispatchedResult:
    result: TimingResult
    route: str

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["route"] = self.route
        return d


@dataclass
class DispatchReport:
    entries: List[DispatchedResult] = field(default_factory=list)
    default_route: str = "default"

    def by_route(self) -> Dict[str, List[DispatchedResult]]:
        groups: Dict[str, List[DispatchedResult]] = {}
        for entry in self.entries:
            groups.setdefault(entry.route, []).append(entry)
        return groups

    def route_counts(self) -> Dict[str, int]:
        return {route: len(items) for route, items in self.by_route().items()}

    def to_dict(self) -> dict:
        return {
            "default_route": self.default_route,
            "route_counts": self.route_counts(),
            "entries": [e.to_dict() for e in self.entries],
        }


def dispatch(
    results: List[TimingResult],
    routes: List[RouteFn],
    default_route: str = "default",
) -> DispatchReport:
    """Route each result through the first matching route function.

    Each route function returns a string label or None if it doesn't match.
    If no route matches, the result is assigned to default_route.
    """
    entries: List[DispatchedResult] = []
    for result in results:
        assigned: Optional[str] = None
        for fn in routes:
            label = fn(result)
            if label is not None:
                assigned = label
                break
        entries.append(DispatchedResult(result=result, route=assigned or default_route))
    return DispatchReport(entries=entries, default_route=default_route)


def route_by_status(success_label: str = "success", failure_label: str = "failure") -> RouteFn:
    """Return a route function that routes by job success/failure."""
    def _fn(r: TimingResult) -> Optional[str]:
        return success_label if r.success else failure_label
    return _fn


def route_by_job_prefix(prefix: str, label: str) -> RouteFn:
    """Return a route function that matches jobs whose id starts with prefix."""
    def _fn(r: TimingResult) -> Optional[str]:
        return label if r.job_id.startswith(prefix) else None
    return _fn
