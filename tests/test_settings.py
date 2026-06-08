from pathlib import Path
from config.settings import Settings


def test_settings_repr_redacts_token():
    s = Settings(
        discord_token="secret_token",
        config_path=Path("config.json"),
        log_path=Path("bot.log"),
    )
    r = repr(s)
    assert "discord_token" not in r
    assert "secret_token" not in r
