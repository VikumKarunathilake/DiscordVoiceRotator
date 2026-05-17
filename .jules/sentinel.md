## 2024-05-17 - Prevent Dataclass Credential Leak in Settings
**Vulnerability:** Dataclasses include all fields in their `__repr__` by default. `config/settings.py` had `discord_token: str` in the `Settings` dataclass. If `Settings` object is ever printed or logged, the bot token would leak.
**Learning:** Python dataclasses automatically stringify their fields, making them dangerous for holding sensitive credentials unless explicitly configured not to.
**Prevention:** Always use `field(repr=False)` for passwords, keys, and tokens in any dataclasses.
