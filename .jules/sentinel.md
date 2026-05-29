## 2026-05-29 - Missing Audit Logging on State-Changing Commands
**Vulnerability:** Administrative commands (`rotate`, `stop`, `delay`, `setchannels`) in `commands/rotation.py` modified state and changed user behavior without recording the initiating user in the logs.
**Learning:** This Discord bot relies on slash command permissions to gate access, but lacks internal audit trails to track which privileged user executed administrative actions, making it impossible to audit abuse or mistakes.
**Prevention:** Always add parameterized audit logging (e.g., `LOGGER.info("AUDIT: User %s did X", user)`) to commands that modify configuration, interact with users, or change application state.
