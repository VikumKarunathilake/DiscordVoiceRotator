## 2024-05-15 - Dataclass Secret Leak
**Vulnerability:** A dataclass (`Settings`) containing a secret (`discord_token`) lacked `repr=False` on the secret field. If this object were printed or logged (e.g. during an exception trace), the plaintext token would be exposed in logs.
**Learning:** Python's `@dataclass` automatically generates a `__repr__` method that includes all fields by default, which is a common source of secret leakage when passing around configuration objects.
**Prevention:** Always use `field(repr=False)` on dataclass attributes that contain sensitive information like API keys, tokens, or passwords to prevent accidental exposure in string representations.
