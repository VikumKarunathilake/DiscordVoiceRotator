## 2024-05-24 - Dataclass Secret Exposure Risk
**Vulnerability:** The `discord_token` in the `Settings` dataclass was lacking `repr=False`, meaning that if the `Settings` object were printed or logged, the plaintext API token would be exposed in the logs.
**Learning:** Dataclasses automatically generate a `__repr__` method that includes all fields. When dealing with sensitive configuration data (tokens, passwords, API keys) in Python dataclasses, it is easy to accidentally leak them.
**Prevention:** Always use `field(repr=False)` from the `dataclasses` module for any sensitive fields within a dataclass to exclude them from the string representation.
