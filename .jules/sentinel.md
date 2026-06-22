## 2024-05-24 - [Fix Exposed Sensitive Data in Dataclass]
**Vulnerability:** Discord token exposed in string representation of Settings dataclass.
**Learning:** Dataclass string representations will automatically include all fields by default, potentially leaking sensitive data like tokens or API keys into logs or error messages.
**Prevention:** Always use `field(repr=False)` on fields that contain sensitive data within a dataclass.
