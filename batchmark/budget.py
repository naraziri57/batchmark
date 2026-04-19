"""Budget enforcement: check if jobs exceed time/cost budgets."""
from dataclasses import dataclass, field
from typing import Optional
from batchmark.timer import TimingResult


@dataclass
class BudgetViolation:
    job_id: str
    duration: Optional[float]
    budget: float
    overage: float

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration": self.duration,
            "budget": self.budget,
            "overage": round(self.overage, 4),
        }


@dataclass
class BudgetReport:
    violations: list = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def to_dict(self) -> dict:
        return {
            "has_violations": self.has_violations,
            "violations": [v.to_dict() for v in self.violations],
        }


def check_budget(
    results: list,
    global_budget: Optional[float] = None,
    per_job_budgets: Optional[dict] = None,
) -> BudgetReport:
    """Check results against time budgets (in seconds).

    Args:
        results: list of TimingResult
        global_budget: default max duration for all jobs
        per_job_budgets: optional dict mapping job_id -> max duration
    """
    per_job_budgets = per_job_budgets or {}
    violations = []

    for r in results:
        budget = per_job_budgets.get(r.job_id, global_budget)
        if budget is None:
            continue
        if r.duration is not None and r.duration > budget:
            violations.append(
                BudgetViolation(
                    job_id=r.job_id,
                    duration=r.duration,
                    budget=budget,
                    overage=r.duration - budget,
                )
            )

    return BudgetReport(violations=violations)
