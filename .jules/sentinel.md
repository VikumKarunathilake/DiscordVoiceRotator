## 2024-06-06 - [Python Dataclass Secrets]
**Vulnerability:** Accidental exposure of sensitive tokens in Python dataclass representations.
**Learning:** Python dataclasses auto-generate `__repr__` methods that include all fields by default, meaning logging or printing a configuration dataclass can leak secrets (like `discord_token`).
**Prevention:** Always use `field(repr=False)` when defining sensitive fields in Python dataclasses.
