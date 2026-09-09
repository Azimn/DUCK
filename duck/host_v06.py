"""Historical persistence adapter pinned to the v0.6 organism."""
from .historical_host import HistoricalPersistentDuckHost
from .living_v06 import LivingDuck


class PersistentDuckHostV06(HistoricalPersistentDuckHost):
    duck_class = LivingDuck
