"""DiscordVoiceRotator bot entrypoint."""

from __future__ import annotations

import asyncio
import logging
import signal
from types import FrameType

import discord
from discord.ext import commands

from config.settings import Settings, load_settings
from services.config_store import ConfigStore
from services.rotation_service import RotationService
from utils.logging import configure_logging

LOGGER = logging.getLogger(__name__)


class DiscordVoiceRotatorBot(commands.Bot):
    """Discord bot with shared services attached for command cogs."""

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.members = True

        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.settings = settings
        self.config_store = ConfigStore(settings.config_path)
        self.rotation_service = RotationService()

    async def setup_hook(self) -> None:
        """Initialize persistence, load slash commands, and sync commands."""

        await self.config_store.load()
        await self.load_extension("commands.rotation")
        synced = await self.tree.sync()
        LOGGER.info("Synced %s slash commands", len(synced))

    async def on_ready(self) -> None:
        """Log readiness once Discord gateway startup completes."""

        if self.user is None:
            LOGGER.info("Bot connected, but user information is unavailable")
            return
        LOGGER.info("Logged in as %s (%s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="voice rotations",
            )
        )

    async def close(self) -> None:
        """Cancel rotation tasks before closing the Discord client."""

        LOGGER.info("Closing bot and cancelling active rotations")
        await self.rotation_service.stop_all()
        await super().close()


def _install_signal_handlers(bot: DiscordVoiceRotatorBot) -> None:
    """Install graceful shutdown handlers for Unix-like platforms."""

    loop = asyncio.get_running_loop()

    def request_shutdown(signum: int, _frame: FrameType | None = None) -> None:
        LOGGER.info("Received signal %s; shutting down", signum)
        loop.create_task(bot.close())

    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, request_shutdown, signum, None)
        except NotImplementedError:
            signal.signal(signum, request_shutdown)


async def main() -> None:
    """Run the Discord bot until it is stopped."""

    settings = load_settings()
    configure_logging(settings.log_path)
    bot = DiscordVoiceRotatorBot(settings)
    _install_signal_handlers(bot)

    try:
        await bot.start(settings.discord_token)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
