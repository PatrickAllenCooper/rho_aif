"""Shared per-decision value-of-information audit record.

Optional, backward-compatible instrumentation for the common observation-
decision evaluation boundary shared by ``PlanningInfoGainAgent``, ``EFEAgent``
(the ``w=1`` special case), and any subclass such as ``DualWeightAgent`` (the
shadow-priced online controller). When an agent is constructed with
``record_audit=True`` it appends one ``DecisionAudit`` per ``select_action``
call, listing every candidate action's task/information decomposition; action
selection itself is completely unaffected (verified in
``tests/test_audit.py``). This is an interpretability artifact, not a new
headline claim (Section 4.3 of the review-response plan).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ActionAudit:
    """Decomposition of one candidate action's evaluated score.

    For an observe action: ``total_score = expected_task_value + weighted_info_gain``
    (the immediate-step decomposition; ``expected_task_value`` already embeds
    any deeper-recursion information bonuses from continuation values, which
    is a property of the additive planning objective itself, not an artifact
    of this record). For a commit action, ``expected_task_value`` equals
    ``total_score`` and the information-gain fields are zero.
    """

    action: int
    kind: str  # "observe" or "commit"
    sensing_cost: float
    info_gain_weight: float
    expected_info_gain: float
    weighted_info_gain: float
    expected_task_value: float
    total_score: float
    chosen: bool = False


@dataclass
class DecisionAudit:
    """All candidate actions evaluated for one ``select_action`` call."""

    step: int
    candidates: List[ActionAudit] = field(default_factory=list)
    chosen_action: int = -1

    def chosen_candidate(self) -> ActionAudit:
        for c in self.candidates:
            if c.chosen:
                return c
        raise ValueError(f"No candidate marked chosen in step {self.step}")

    def max_total_score(self) -> float:
        return max(c.total_score for c in self.candidates)
