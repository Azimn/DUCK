"""Historical persistence adapter pinned to the v0.5 organism."""
from .historical_host import HistoricalPersistentDuckHost
from .living import LivingDuck


class PersistentDuckHostV05(HistoricalPersistentDuckHost):
    duck_class = LivingDuck
