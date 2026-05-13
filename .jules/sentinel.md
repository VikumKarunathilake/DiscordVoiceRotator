## 2025-05-13 - [Preventing Secret Leakage in Dataclasses]
**Vulnerability:** The application stored the Discord bot token as a plain string inside a `dataclass`. If the object was logged or appeared in an error traceback, the token would be leaked in plain text.
**Learning:** Dataclasses include all fields in their auto-generated `__repr__` method by default, posing a risk when storing credentials.
**Prevention:** Use `field(repr=False)` from the `dataclasses` module for any fields containing secrets, API keys, or tokens.
