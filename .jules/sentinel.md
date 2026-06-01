## 2026-06-01 - Python Dataclass Secret Exposure
**Vulnerability:** Discord bot token (`discord_token`) was defined as a standard dataclass field in `config/settings.py` without `repr=False`.
**Learning:** Python dataclasses automatically generate a `__repr__` method that includes all fields by default. This can inadvertently leak sensitive data (like tokens, passwords, API keys) into logs, error messages, or monitoring systems if the dataclass instance is printed or logged.
**Prevention:** Always use `field(repr=False)` for fields containing sensitive information in Python dataclasses.
