## 2024-06-11 - Python Dataclasses Secret Exposure
**Vulnerability:** The Discord token was stored in a Python `dataclass` without disabling its representation (`repr`). By default, logging or printing a dataclass exposes all its fields. This could lead to a sensitive token being logged in plain text or printed in stack traces.
**Learning:** Python dataclasses automatically generate a `__repr__` method that includes all fields. This is dangerous for sensitive data like tokens and API keys, as it can accidentally leak them into logs.
**Prevention:** Always use `field(repr=False)` when storing sensitive secrets in a Python `dataclass`.
