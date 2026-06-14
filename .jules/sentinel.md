## 2024-05-24 - [Fix Exposed Sensitive Data in Dataclass]
**Vulnerability:** Discord token exposed in string representation of Settings dataclass.
**Learning:** Dataclass string representations will automatically include all fields by default, potentially leaking sensitive data like tokens or API keys into logs or error messages.
**Prevention:** Always use `field(repr=False)` on fields that contain sensitive data within a dataclass.

## 2024-06-14 - [Missing Audit Logging for Administrative Actions]
**Vulnerability:** State-changing administrative commands (`/rotate`, `/stop`, `/delay`, `/setchannels`) were missing audit logs, creating an insufficient tracking of security events and making it difficult to attribute actions to specific users.
**Learning:** Even when operations are restricted by role or permissions (e.g. `move_members`), leaving no audit trail makes it impossible to investigate abuse or misconfigurations within the server.
**Prevention:** Always implement parameterized audit logging (e.g., `LOGGER.info("AUDIT: User %s did X", interaction.user)`) for any commands or endpoints that modify state or perform sensitive actions.
