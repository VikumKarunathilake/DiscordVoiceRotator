"""Persistent per-guild rotation configuration models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

RotationMode = Literal["sequential", "random"]
MIN_ROTATION_DELAY_SECONDS = 3.0
DEFAULT_ROTATION_DELAY_SECONDS = 3.0


@dataclass(slots=True)
class GuildRotationConfig:
    """Configuration used by rotation tasks in a single guild."""

    guild_id: int
    channel_ids: list[int]
    delay_seconds: float = DEFAULT_ROTATION_DELAY_SECONDS
    mode: RotationMode = "sequential"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GuildRotationConfig":
        """Build a configuration instance from JSON-compatible data."""

        mode = payload.get("mode", "sequential")
        if mode not in {"sequential", "random"}:
            mode = "sequential"

        delay = max(
            float(payload.get("delay_seconds", DEFAULT_ROTATION_DELAY_SECONDS)),
            MIN_ROTATION_DELAY_SECONDS,
        )
        return cls(
            guild_id=int(payload["guild_id"]),
            channel_ids=[
                int(channel_id) for channel_id in payload.get("channel_ids", [])
            ],
            delay_seconds=delay,
            mode=mode,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this configuration to JSON-compatible data."""

        return asdict(self)
