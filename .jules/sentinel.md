## 2024-05-18 - Added Audit Logging for Sensitive Commands
**Vulnerability:** Insufficient logging of security events (missing audit trails for administrative commands).
**Learning:** In a multi-guild environment, state-changing commands (`rotate`, `stop`, `delay`, `setchannels`) lacked a centralized, identifiable logging mechanism to track which user initiated the action, making accountability and incident response difficult.
**Prevention:** Implement explicit `LOGGER.info("AUDIT: ...")` statements with parameterized logging in all application commands that manage sensitive configuration or actions.
