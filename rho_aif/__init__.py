"""Expected Free Energy as belief-dependent utility for rho-POMDPs.

Agents live in :mod:`rho_aif.agents`, Gymnasium environments in
:mod:`rho_aif.environments`. Belief-state machinery, scoring rules, and the
benchmark registry are exposed at the top level.
"""

from rho_aif.belief import BeliefState
from rho_aif.scoring import log_score, brier_score
from rho_aif.benchmark import BENCHMARKS, list_benchmarks, get_benchmark, run_benchmark

__version__ = "1.0.0"

__all__ = [
    "BeliefState",
    "log_score",
    "brier_score",
    "BENCHMARKS",
    "list_benchmarks",
    "get_benchmark",
    "run_benchmark",
    "__version__",
]
