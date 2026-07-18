"""Expected Free Energy as belief-dependent utility for rho-POMDPs.

Agents live in :mod:`rho_aif.agents`, Gymnasium environments in
:mod:`rho_aif.environments`. Belief-state machinery and statistical
utilities are exposed at the top level.
"""

from rho_aif.belief import BeliefState

__version__ = "1.0.0"

__all__ = ["BeliefState", "__version__"]
