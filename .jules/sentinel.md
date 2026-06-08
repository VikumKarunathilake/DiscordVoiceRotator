## 2025-02-17 - Sensitive Token Exposure in Dataclass Representations
**Vulnerability:** The `Settings` dataclass included a `discord_token` without setting `repr=False`. This meant that printing the settings object or logging it implicitly would dump the plaintext Discord bot token into the application logs.
**Learning:** Python dataclasses automatically generate a `__repr__` method that includes all fields. Sensitive fields, like API keys or tokens, can accidentally be exposed when the object representation is generated.
**Prevention:** Always use `field(repr=False)` on dataclass fields that contain sensitive information to ensure they are omitted from the object's string representation.
