# DiscordVoiceRotator

DiscordVoiceRotator is a production-ready Python Discord bot that rotates a selected, connected Discord member between configured voice channels. It uses official Discord bot tokens only, `discord.py` slash commands, `uv`, `python-dotenv`, persistent JSON configuration, structured logs, and safe async task management.

> **Important:** This project does **not** support self-bots or user tokens. Use only official Discord bot tokens from the Discord Developer Portal and respect Discord API rate limits.

## Features

- Slash-command-only Discord bot built with `discord.py`.
- Multi-guild support with independent per-server configuration.
- Persistent channel, delay, and mode configuration stored in `config/guilds.json`.
- Random or sequential voice rotation modes.
- Moves the user back to their original voice channel automatically when the rotation is stopped.
- Minimum delay of 1 second to prevent unsafe move spam.
- Duplicate rotation prevention per guild/user pair.
- Graceful handling for disconnected users, missing channels, missing permissions, Discord API errors, and shutdown.
- Structured JSON logs written to `logs/bot.log`.
- Embed-based command responses.
- Docker and Docker Compose support.

## Project Structure

```text
DiscordVoiceRotator/
├── bot.py
├── commands/
│   └── rotation.py
├── config/
│   ├── guild_config.py
│   └── settings.py
├── services/
│   ├── config_store.py
│   └── rotation_service.py
├── utils/
│   ├── embeds.py
│   └── logging.py
├── logs/
│   └── .gitkeep
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Requirements

- Python 3.11 or newer.
- [`uv`](https://docs.astral.sh/uv/) for local dependency management.
- A Discord application with a bot user.
- A Discord bot token in `DISCORD_TOKEN`.

## Required Bot Permissions

Invite the bot with these permissions:

- `Move Members`
- `View Channels`
- `Connect`
- `Send Messages`
- `Use Slash Commands`
- `Embed Links`

The bot must have `Move Members` permission in every voice channel configured with `/setchannels`. Users invoking management commands must either be Administrators or have `Move Members` permission.

## Discord Developer Portal Setup

1. Open the Discord Developer Portal.
2. Create an application and add a bot user.
3. Copy the bot token and place it in `.env` as `DISCORD_TOKEN`.
4. Enable the **Server Members Intent** if your server requires member resolution for slash-command member options.
5. Invite the bot to your server with the required permissions above.

## Installation

```bash
git clone <your-repo-url>
cd DiscordVoiceRotator
cp .env.example .env
uv venv
uv pip install -r requirements.txt
```

Edit `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

## Running Locally

```bash
uv run python bot.py
```

On startup, the bot loads persistent guild settings, registers slash commands globally, and writes logs to `logs/bot.log`. Global Discord slash-command syncs can take time to appear in every server.

## Commands

### `/ping`

Checks gateway latency.

### `/setchannels`

Configures the voice channels and default rotation behavior for the current server.

Example:

```text
/setchannels channel_1:General channel_2:Gaming delay_seconds:10 mode:Sequential
```

Optional `channel_3` through `channel_6` parameters can add more channels. The delay cannot be below 1 second.

### `/delay <seconds>`

Updates the rotation delay for the current server.

Example:

```text
/delay seconds:5
```

### `/rotate <user>`

Starts rotating a connected member between the configured voice channels.

Example:

```text
/rotate user:@ExampleUser
```

### `/stop <user>`

Stops an active rotation for a member in the current server.

Example:

```text
/stop user:@ExampleUser
```

### `/status`

Shows active rotations in the current server, including mode, delay, moves completed, last channel, and last error when present.

## Safety and Rate Limits

- The minimum rotation delay is 3 seconds.
- A user can only have one active rotation task per server.
- The bot validates invoker permissions and its own `Move Members` permissions before moving users.
- If a target user disconnects from voice, their rotation task exits safely.
- `discord.py` handles Discord API rate limits internally; the rotation service also backs off when an HTTP error exposes a retry delay.
- Shutdown signals cancel all active tasks before closing the Discord client.

## VPS Deployment

1. Install Python 3.11+ and `uv` on the VPS.
2. Clone the repository.
3. Create `.env` from `.env.example` and add `DISCORD_TOKEN`.
4. Install dependencies:

   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

5. Run the bot:

   ```bash
   uv run python bot.py
   ```

For long-running production use, run it behind `systemd`, `supervisord`, or a process manager that restarts on failure. Persist the `config/` and `logs/` directories.

## Docker Deployment

Build and run with Docker Compose:

```bash
cp .env.example .env
# edit .env and set DISCORD_TOKEN
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f discord-voice-rotator
```

Stop the bot:

```bash
docker compose down
```

The Compose file mounts `./config` and `./logs` so guild settings and logs survive container restarts.

## Coolify Deployment

1. Create a new Coolify application from this repository.
2. Choose Dockerfile or Docker Compose deployment.
3. Add an environment variable named `DISCORD_TOKEN` with your official bot token.
4. Add persistent storage mounts for:
   - `/app/config`
   - `/app/logs`
5. Deploy the application.
6. Check Coolify logs and confirm the bot logs in and syncs slash commands.

## Security Notes

- Never commit `.env`, Discord tokens, or runtime config containing sensitive data.
- Rotate the Discord bot token immediately if it is exposed.
- Do not increase move frequency below the enforced 3-second minimum.
- Use Discord role/channel permissions to restrict who can manage rotations.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
