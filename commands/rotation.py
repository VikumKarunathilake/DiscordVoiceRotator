"""Slash commands for voice rotation management."""

from __future__ import annotations

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from config.guild_config import (
    GuildRotationConfig,
    MIN_ROTATION_DELAY_SECONDS,
    RotationMode,
)
from services.config_store import ConfigStore
from services.rotation_service import RotationService, RotationStatus
from utils.embeds import (
    ERROR_COLOR,
    INFO_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
    build_embed,
)

LOGGER = logging.getLogger(__name__)


class RotationCommands(commands.Cog):
    """Discord application commands for configuring and running rotations."""

    def __init__(
        self, bot: commands.Bot, store: ConfigStore, service: RotationService
    ) -> None:
        self.bot = bot
        self.store = store
        self.service = service

    @app_commands.command(name="ping", description="Check bot latency and health.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        embed = build_embed("Pong", f"Gateway latency: `{latency_ms}ms`", SUCCESS_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="status", description="Show active voice rotations in this server."
    )
    @app_commands.guild_only()
    async def status(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await self._send_error(
                interaction, "This command can only be used in a server."
            )
            return

        statuses = self.service.get_statuses(interaction.guild.id)
        if not statuses:
            embed = build_embed(
                "Rotation Status", "No active rotations in this server.", INFO_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        description = "\n".join(self._format_status(status) for status in statuses)
        embed = build_embed("Rotation Status", description, INFO_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="rotate",
        description="Start rotating a connected user between configured channels.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(move_members=True)
    async def rotate(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await self._can_manage_rotations(interaction):
            return
        if interaction.guild is None:
            await self._send_error(
                interaction, "This command can only be used in a server."
            )
            return

        config = await self.store.get_guild(interaction.guild.id)
        if config is None or len(config.channel_ids) < 2:
            await self._send_error(
                interaction,
                "Configure at least two voice channels first with `/setchannels`.",
            )
            return

        validation_error = self._validate_member_and_bot_permissions(user, config)
        if validation_error is not None:
            await self._send_error(interaction, validation_error)
            return

        try:
            status = await self.service.start_rotation(user, config)
        except ValueError as exc:
            await self._send_error(interaction, str(exc))
            return

        embed = build_embed(
            "Rotation Started",
            (
                f"Started rotating {user.mention} across "
                f"`{len(config.channel_ids)}` channels.\n"
                f"Mode: `{status.mode}`\nDelay: `{status.delay_seconds:.1f}s`"
            ),
            SUCCESS_COLOR,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="stop", description="Stop rotating a user in this server."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(move_members=True)
    async def stop(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await self._can_manage_rotations(interaction):
            return
        if interaction.guild is None:
            await self._send_error(
                interaction, "This command can only be used in a server."
            )
            return

        stopped = await self.service.stop_rotation(interaction.guild.id, user.id)
        if not stopped:
            await self._send_error(
                interaction, f"{user.mention} is not currently being rotated."
            )
            return

        embed = build_embed(
            "Rotation Stopped", f"Stopped rotating {user.mention}.", SUCCESS_COLOR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="setchannels",
        description="Configure channels, delay, and mode for this server.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(move_members=True)
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Sequential", value="sequential"),
            app_commands.Choice(name="Random", value="random"),
        ]
    )
    async def setchannels(
        self,
        interaction: discord.Interaction,
        channel_1: discord.VoiceChannel,
        channel_2: discord.VoiceChannel,
        delay_seconds: app_commands.Range[
            float, MIN_ROTATION_DELAY_SECONDS, 86400.0
        ] = 10.0,
        mode: Literal["sequential", "random"] = "sequential",
        channel_3: discord.VoiceChannel | None = None,
        channel_4: discord.VoiceChannel | None = None,
        channel_5: discord.VoiceChannel | None = None,
        channel_6: discord.VoiceChannel | None = None,
    ) -> None:
        if not await self._can_manage_rotations(interaction):
            return
        if interaction.guild is None:
            await self._send_error(
                interaction, "This command can only be used in a server."
            )
            return

        channels = [
            channel
            for channel in [
                channel_1,
                channel_2,
                channel_3,
                channel_4,
                channel_5,
                channel_6,
            ]
            if channel is not None
        ]
        unique_channels = list(dict.fromkeys(channels))
        if len(unique_channels) < 2:
            await self._send_error(
                interaction, "Please provide at least two unique voice channels."
            )
            return

        bot_member = interaction.guild.me
        if bot_member is None:
            await self._send_error(interaction, "Bot membership could not be resolved.")
            return

        missing_channels = [
            channel.mention
            for channel in unique_channels
            if not channel.permissions_for(bot_member).move_members
        ]
        if missing_channels:
            await self._send_error(
                interaction,
                "I need `Move Members` permission in these channels: "
                + ", ".join(missing_channels),
            )
            return

        config = GuildRotationConfig(
            guild_id=interaction.guild.id,
            channel_ids=[channel.id for channel in unique_channels],
            delay_seconds=float(delay_seconds),
            mode=mode,
        )
        await self.store.set_guild(config)

        channel_list = ", ".join(channel.mention for channel in unique_channels)
        embed = build_embed(
            "Rotation Channels Saved",
            (
                f"Channels: {channel_list}\n"
                f"Mode: `{mode}`\nDelay: `{float(delay_seconds):.1f}s`"
            ),
            SUCCESS_COLOR,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        LOGGER.error(
            "Slash command failed", exc_info=(type(error), error, error.__traceback__)
        )
        message = "An unexpected error occurred while processing that command."
        if isinstance(error, app_commands.MissingPermissions):
            message = (
                "You need `Move Members` permission or Administrator "
                "to use this command."
            )
        await self._send_error(interaction, message)

    async def _can_manage_rotations(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None or not isinstance(
            interaction.user, discord.Member
        ):
            await self._send_error(
                interaction, "This command can only be used in a server."
            )
            return False

        permissions = interaction.user.guild_permissions
        if permissions.administrator or permissions.move_members:
            return True

        await self._send_error(
            interaction,
            "You need `Move Members` permission or Administrator to use this command.",
        )
        return False

    def _validate_member_and_bot_permissions(
        self,
        member: discord.Member,
        config: GuildRotationConfig,
    ) -> str | None:
        if member.guild is None:
            return "The selected user must be in this server."
        if member.voice is None or member.voice.channel is None:
            return "The selected user is not connected to a voice channel."

        bot_member = member.guild.me
        if bot_member is None:
            return "Bot membership could not be resolved."
        if not bot_member.guild_permissions.move_members:
            return "I need the server-level `Move Members` permission."

        for channel_id in config.channel_ids:
            channel = member.guild.get_channel(channel_id)
            if not isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                return (
                    f"Configured channel `{channel_id}` was not found. "
                    "Run `/setchannels` again."
                )
            if not channel.permissions_for(bot_member).move_members:
                return f"I need `Move Members` permission in {channel.mention}."
        return None

    def _format_status(self, status: RotationStatus) -> str:
        last_channel = (
            f"<#{status.last_channel_id}>" if status.last_channel_id else "none yet"
        )
        error_text = f"\nLast error: `{status.last_error}`" if status.last_error else ""
        return (
            f"<@{status.user_id}> — `{status.mode}` every "
            f"`{status.delay_seconds:.1f}s`; moves: `{status.moves_completed}`; "
            f"last channel: {last_channel}{error_text}"
        )

    async def _send_error(self, interaction: discord.Interaction, message: str) -> None:
        embed = build_embed(
            "Action Required",
            message,
            WARNING_COLOR if "need" in message else ERROR_COLOR,
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """discord.py extension entrypoint."""

    store: ConfigStore = bot.config_store  # type: ignore[attr-defined]
    service: RotationService = bot.rotation_service  # type: ignore[attr-defined]
    await bot.add_cog(RotationCommands(bot, store, service))
