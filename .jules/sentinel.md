## 2024-05-20 - Missing Audit Logging for Admin Actions
**Vulnerability:** The /setchannels and /delay commands modify critical server settings but did not have audit logging enabled.
**Learning:** In a multi-tenant Discord bot, changes to server configuration must be auditable so administrators and support can identify when and by whom a malicious or unintended change was made.
**Prevention:** Implement structured logging prefixing admin/state-changing logs with 'AUDIT:' to ensure traceability.
