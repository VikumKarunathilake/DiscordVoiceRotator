"""Helpers for consistent Discord embed responses."""

from __future__ import annotations

import discord

SUCCESS_COLOR = discord.Color.green()
ERROR_COLOR = discord.Color.red()
INFO_COLOR = discord.Color.blurple()
WARNING_COLOR = discord.Color.orange()


def build_embed(
    title: str, description: str, color: discord.Color = INFO_COLOR
) -> discord.Embed:
    """Create a standard response embed."""

    return discord.Embed(title=title, description=description, color=color)
