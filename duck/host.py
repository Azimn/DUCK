"""Public persistent host for the current MicroPsiDUCK v0.10 organism.

The v0.9 host remains preserved on main. The branch-public host composes the
motivated-cognition core with persistent endogenous heartbeat scheduling.
"""

from .host_current import InteractionResult, PersistentDuckHost, PersistentDuckHostCurrent

__all__ = ["InteractionResult", "PersistentDuckHost", "PersistentDuckHostCurrent"]
