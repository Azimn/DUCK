"""Public persistent host for the MicroPsiDUCK v0.10 candidate.

The v0.9 host remains preserved on main. This development branch deliberately
publishes the new experiential-firewall host rather than maintaining API identity
with the promoted v0.9 baseline.
"""

from .host_v010 import InteractionResultV010, PersistentDuckHostV010

InteractionResult = InteractionResultV010
PersistentDuckHost = PersistentDuckHostV010

__all__ = ["InteractionResult", "PersistentDuckHost"]
