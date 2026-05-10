"""Voice rotation task orchestration."""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime

import discord

from config.guild_config import GuildRotationConfig, MIN_ROTATION_DELAY_SECONDS

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RotationStatus:
    """Runtime status for a member rotation task."""

    guild_id: int
    user_id: int
    user_display: str
    channel_ids: list[int]
    delay_seconds: float
    mode: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    moves_completed: int = 0
    last_channel_id: int | None = None
    original_channel_id: int | None = None
    last_error: str | None = None


class RotationService:
    """Manage voice rotation tasks across many guilds."""

    def __init__(self) -> None:
        self._tasks: dict[tuple[int, int], asyncio.Task[None]] = {}
        self._statuses: dict[tuple[int, int], RotationStatus] = {}
        self._lock = asyncio.Lock()

    async def start_rotation(
        self,
        member: discord.Member,
        config: GuildRotationConfig,
    ) -> RotationStatus:
        """Start rotating a guild member, preventing duplicate tasks."""

        if len(config.channel_ids) < 2:
            raise ValueError(
                "Configure at least two voice channels before rotating users."
            )
        if member.guild is None:
            raise ValueError("The selected user must belong to a guild.")
        if member.voice is None or member.voice.channel is None:
            raise ValueError("The selected user is not connected to a voice channel.")

        delay = max(config.delay_seconds, MIN_ROTATION_DELAY_SECONDS)
        key = (member.guild.id, member.id)
        async with self._lock:
            if key in self._tasks and not self._tasks[key].done():
                raise ValueError("That user is already being rotated in this guild.")

            status = RotationStatus(
                guild_id=member.guild.id,
                user_id=member.id,
                user_display=member.display_name,
                channel_ids=list(config.channel_ids),
                delay_seconds=delay,
                mode=config.mode,
                original_channel_id=member.voice.channel.id,
            )
            task = asyncio.create_task(
                self._rotation_loop(member, status),
                name=f"rotation:{member.guild.id}:{member.id}",
            )
            self._tasks[key] = task
            self._statuses[key] = status
            task.add_done_callback(lambda completed: self._cleanup_task(key, completed))
            return status

    async def stop_rotation(self, guild_id: int, user_id: int) -> bool:
        """Stop an active rotation task for a user."""

        key = (guild_id, user_id)
        async with self._lock:
            task = self._tasks.get(key)
            if task is None or task.done():
                self._tasks.pop(key, None)
                self._statuses.pop(key, None)
                return False
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return True

    async def stop_all(self) -> None:
        """Cancel every active rotation task during shutdown."""

        async with self._lock:
            tasks = [task for task in self._tasks.values() if not task.done()]
            for task in tasks:
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_statuses(self, guild_id: int | None = None) -> list[RotationStatus]:
        """Return current rotation status snapshots."""

        statuses = list(self._statuses.values())
        if guild_id is None:
            return statuses
        return [status for status in statuses if status.guild_id == guild_id]

    def is_rotating(self, guild_id: int, user_id: int) -> bool:
        """Return whether a user currently has an active rotation task."""

        task = self._tasks.get((guild_id, user_id))
        return task is not None and not task.done()

    async def _rotation_loop(
        self,
        member: discord.Member,
        status: RotationStatus,
    ) -> None:
        index = 0
        LOGGER.info(
            "Started rotation for guild=%s user=%s", status.guild_id, status.user_id
        )
        try:
            while True:
                if member.voice is None or member.voice.channel is None:
                    status.last_error = "User disconnected from voice."
                    LOGGER.info(
                        "Stopping rotation because user disconnected guild=%s user=%s",
                        status.guild_id,
                        status.user_id,
                    )
                    return

                channel = self._select_channel(member, status, index)
                if channel is None:
                    status.last_error = "Configured voice channel was not found."
                    return

                if member.voice.channel.id != channel.id:
                    await self._move_with_backoff(member, channel, status)
                    status.moves_completed += 1
                    status.last_channel_id = channel.id

                if status.mode == "sequential":
                    index = (index + 1) % len(status.channel_ids)
                await asyncio.sleep(status.delay_seconds)
        except asyncio.CancelledError:
            LOGGER.info(
                "Cancelled rotation for guild=%s user=%s",
                status.guild_id,
                status.user_id,
            )
            raise
        except discord.Forbidden:
            status.last_error = "Bot no longer has permission to move this user."
            LOGGER.exception("Missing permissions during rotation")
        except discord.HTTPException as exc:
            status.last_error = f"Discord API error: {exc.status}"
            LOGGER.exception("Discord API error during rotation")
        except (
            Exception
        ) as exc:  # noqa: BLE001 - keep long-running task failures contained.
            status.last_error = str(exc)
            LOGGER.exception("Unexpected rotation failure")
        finally:
            # Move member back to original channel if they are still connected
            if (
                status.original_channel_id
                and member.voice
                and member.voice.channel
                and member.voice.channel.id != status.original_channel_id
            ):
                original_channel = member.guild.get_channel(status.original_channel_id)
                if isinstance(
                    original_channel, (discord.VoiceChannel, discord.StageChannel)
                ):
                    try:
                        await member.move_to(
                            original_channel,
                            reason="DiscordVoiceRotator rotation stopped; returning to original channel",
                        )
                    except (discord.Forbidden, discord.HTTPException):
                        LOGGER.warning(
                            "Could not move member back to original channel guild=%s user=%s",
                            status.guild_id,
                            status.user_id,
                        )

    def _select_channel(
        self,
        member: discord.Member,
        status: RotationStatus,
        index: int,
    ) -> discord.VoiceChannel | discord.StageChannel | None:
        guild = member.guild
        channels = [
            channel
            for channel_id in status.channel_ids
            if isinstance(
                (channel := guild.get_channel(channel_id)),
                (discord.VoiceChannel, discord.StageChannel),
            )
        ]
        if not channels:
            return None
        if status.mode == "random":
            current_id = (
                member.voice.channel.id
                if member.voice and member.voice.channel
                else None
            )
            candidates = [channel for channel in channels if channel.id != current_id]
            return random.choice(candidates or channels)
        return channels[index % len(channels)]

    async def _move_with_backoff(
        self,
        member: discord.Member,
        channel: discord.VoiceChannel | discord.StageChannel,
        status: RotationStatus,
    ) -> None:
        try:
            await member.move_to(channel, reason="DiscordVoiceRotator active rotation")
        except discord.HTTPException as exc:
            retry_after = float(getattr(exc, "retry_after", status.delay_seconds))
            status.last_error = (
                f"Rate limited or API error; retrying after {retry_after:.1f}s."
            )
            await asyncio.sleep(max(retry_after, status.delay_seconds))
            await member.move_to(
                channel, reason="DiscordVoiceRotator retry after API error"
            )

    def _cleanup_task(self, key: tuple[int, int], task: asyncio.Task[None]) -> None:
        self._tasks.pop(key, None)
        self._statuses.pop(key, None)
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            LOGGER.error(
                "Rotation task ended with error",
                exc_info=(type(exc), exc, exc.__traceback__),
            )
