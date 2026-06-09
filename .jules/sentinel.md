## 2024-06-09 - Dataclass Auto-generated __repr__ Secret Exposure
**Vulnerability:** The `Settings` dataclass in `config/settings.py` exposed the `DISCORD_TOKEN` because Python dataclasses automatically generate a `__repr__` method that includes all fields. This meant any accidental logging or printing of the settings object would leak the bot's core credential.
**Learning:** We must be extremely careful when using dataclasses to hold sensitive information like tokens, passwords, or API keys, as default behavior is to print everything.
**Prevention:** Always use `field(repr=False)` for any field in a dataclass that contains sensitive data, or avoid using standard dataclasses for secrets entirely if a custom `__repr__` is not easy to strictly enforce.
