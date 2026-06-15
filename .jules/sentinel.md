## 2024-05-24 - [Fix Exposed Sensitive Data in Dataclass]
**Vulnerability:** Discord token exposed in string representation of Settings dataclass.
**Learning:** Dataclass string representations will automatically include all fields by default, potentially leaking sensitive data like tokens or API keys into logs or error messages.
**Prevention:** Always use `field(repr=False)` on fields that contain sensitive data within a dataclass.

## 2024-06-05 - [Add Audit Logging for Administrative Actions]
**Vulnerability:** Lack of audit trails for administrative commands like starting/stopping rotations or changing configuration.
**Learning:** In a multi-administrator Discord environment, it is critical to have a clear audit trail of who initiated state-changing actions to ensure accountability and facilitate incident response.
**Prevention:** Always implement parameterized logging with an 'AUDIT:' prefix for all administrative or state-changing commands, recording the initiating user, target user, and relevant parameters.
