## 2024-06-07 - Python Dataclasses Exposing Secrets
**Vulnerability:** The `Settings` dataclass in `config/settings.py` exposed the `discord_token` secret. By default, Python dataclasses generate a `__repr__` method that includes the values of all fields. If a dataclass object is logged or included in a traceback, its secrets are leaked.
**Learning:** Automatically generated methods like `__repr__` in dataclasses (and potentially other object serialization methods) can inadvertently leak sensitive data if not configured correctly.
**Prevention:** Always use `field(repr=False)` in Python dataclasses for any fields that contain sensitive data, such as API keys, tokens, or passwords.
