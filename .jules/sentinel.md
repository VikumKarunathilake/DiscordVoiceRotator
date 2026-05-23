## 2024-05-23 - Missing Audit Logging for Administrative Actions
**Vulnerability:** Administrative/state-changing slash commands (`/rotate`, `/stop`, `/delay`, `/setchannels`) lacked audit logging to track which user initiated these actions.
**Learning:** Without audit logs, it is difficult or impossible to trace unauthorized or abusive configuration changes back to the user who executed the command, particularly since Discord does not provide built-in bot audit logs for slash command execution.
**Prevention:** Implement parameterized application-level logging with a standardized prefix (e.g., `AUDIT:`) whenever a command modifies state or performs a sensitive administrative action.
