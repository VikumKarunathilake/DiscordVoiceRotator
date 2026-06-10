## 2024-06-10 - Dataclass Secret Leakage
**Vulnerability:** Sensitive configuration data (Discord token) was stored in a standard dataclass without `repr=False`, making it vulnerable to accidental exposure in logs or stack traces.
**Learning:** Python dataclasses automatically generate a `__repr__` method that includes all fields, which can unintentionally leak secrets when the object is printed or logged.
**Prevention:** Always use `field(repr=False)` for sensitive fields (e.g., tokens, API keys) in Python dataclasses to prevent accidental exposure.
