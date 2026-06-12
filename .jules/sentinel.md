## 2024-06-12 - Prevent Secret Leakage in Dataclasses
**Vulnerability:** The `Settings` dataclass stored the `discord_token` as a standard string field, making it vulnerable to accidental exposure if the config object was logged or included in an error stack trace.
**Learning:** Python dataclasses automatically generate a `__repr__` method that includes all fields. This is a common pattern in this application for storing configuration, which poses a severe risk of secret leakage.
**Prevention:** Always use `field(repr=False)` when defining sensitive data fields (like tokens, passwords, or API keys) within Python dataclasses to prevent their inclusion in string representations.
