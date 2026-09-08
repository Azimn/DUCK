"""Historical persistence adapter pinned to the DUCK v0.9 organism."""
from __future__ import annotations

from .historical_host import HistoricalPersistentDuckHost
from .living_v09 import LivingDuck


class PersistentDuckHostV09(HistoricalPersistentDuckHost):
    """Minimal durable host pinned to ``living_v09.LivingDuck``."""

    duck_class = LivingDuck
