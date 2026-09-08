"""Historical persistence adapter pinned to the DUCK v0.8 organism."""
from __future__ import annotations

from .historical_host import HistoricalPersistentDuckHost
from .living_v08 import LivingDuck


class PersistentDuckHostV08(HistoricalPersistentDuckHost):
    """Minimal durable host pinned to ``living_v08.LivingDuck``."""

    duck_class = LivingDuck
