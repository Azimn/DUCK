"""Explicit temporal representations, including Swatch Internet Time."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


BMT = timezone(timedelta(hours=1))


@dataclass(frozen=True)
class TemporalStamp:
    logical_tick: int
    utc_iso: str
    bmt_date: str
    beat: float

    @property
    def beat_label(self) -> str:
        return f"@{self.beat:06.2f}"


def internet_time(value: datetime | None = None) -> tuple[str, float]:
    now = value or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    bmt = now.astimezone(BMT)
    seconds = bmt.hour * 3600 + bmt.minute * 60 + bmt.second + bmt.microsecond / 1_000_000
    return bmt.date().isoformat(), seconds / 86.4


def stamp(logical_tick: int, value: datetime | None = None) -> TemporalStamp:
    now = value or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    date, beat = internet_time(now)
    return TemporalStamp(int(logical_tick), now.isoformat(), date, beat)
