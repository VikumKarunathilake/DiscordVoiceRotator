"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the bot process."""

    discord_token: str
    config_path: Path
    log_path: Path


def load_settings() -> Settings:
    """Load and validate settings from the environment."""

    load_dotenv()
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("DISCORD_TOKEN is required and must be a Discord bot token.")

    return Settings(
        discord_token=token,
        config_path=Path("config/guilds.json"),
        log_path=Path("logs/bot.log"),
    )
