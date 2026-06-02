## 2024-05-18 - Prevent Sensitive Data Exposure in Dataclasses
**Vulnerability:** The `Settings` dataclass stored the `discord_token` without setting `repr=False`. This could lead to the token being exposed in plaintext in logs, debug outputs, or anywhere the object is represented as a string.
**Learning:** Dataclasses automatically generate a `__repr__` method that includes the values of all fields. If a field contains sensitive data (like a token or API key), it will be leaked when the object is printed or logged.
**Prevention:** Always use `field(repr=False)` from the `dataclasses` module for any fields containing sensitive information to ensure they are excluded from the string representation.
