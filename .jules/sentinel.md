## 2024-06-25 - Missing Audit Logs for Administrative Actions
**Vulnerability:** State-changing Discord bot commands (`rotate`, `stop`, `delay`, `setchannels`) could be executed by users with `Move Members` permissions, but there was no audit log tracking who initiated these actions. If abuse occurred, it would be impossible to determine which authorized user made the changes.
**Learning:** Even if commands are protected by permissions (e.g., `move_members=True`), failing to log who executes them creates a gap in non-repudiation and makes auditing administrative actions impossible.
**Prevention:** All administrative or state-changing bot commands must emit an audit log entry (e.g., `LOGGER.info("AUDIT: User %s did X", user)`) to ensure accountability and traceability.
