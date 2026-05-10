"""Async JSON-backed persistence for guild rotation settings."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from config.guild_config import GuildRotationConfig

LOGGER = logging.getLogger(__name__)


class ConfigStore:
    """Load and save per-guild configuration in a JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._configs: dict[int, GuildRotationConfig] = {}

    async def load(self) -> None:
        """Load existing configuration from disk, creating directories if needed."""

        async with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._configs = {}
                await self._write_locked()
                return

            try:
                raw = await asyncio.to_thread(self._path.read_text, encoding="utf-8")
                payload = json.loads(raw or "{}")
                guilds = payload.get("guilds", {})
                self._configs = {
                    int(guild_id): GuildRotationConfig.from_dict(config)
                    for guild_id, config in guilds.items()
                }
            except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError):
                LOGGER.exception("Failed to load guild configuration; starting empty")
                self._configs = {}

    async def get_guild(self, guild_id: int) -> GuildRotationConfig | None:
        """Return the stored configuration for a guild, if present."""

        async with self._lock:
            return self._configs.get(guild_id)

    async def set_guild(self, config: GuildRotationConfig) -> None:
        """Persist the supplied guild configuration."""

        async with self._lock:
            self._configs[config.guild_id] = config
            await self._write_locked()

    async def all_configs(self) -> dict[int, GuildRotationConfig]:
        """Return a snapshot of every loaded guild configuration."""

        async with self._lock:
            return dict(self._configs)

    async def _write_locked(self) -> None:
        payload: dict[str, Any] = {
            "guilds": {
                str(guild_id): config.to_dict()
                for guild_id, config in self._configs.items()
            }
        }
        serialized = json.dumps(payload, indent=2, sort_keys=True)
        await asyncio.to_thread(self._path.write_text, serialized, encoding="utf-8")
