## 2024-06-25 - Missing Audit Logging for State-Changing Commands
**Vulnerability:** The application had missing audit logging for critical state-changing commands (`rotate`, `stop`, `delay`, `setchannels`), which could allow administrative actions to go untracked and prevent accountability.
**Learning:** In Discord bots with management interfaces, any command that alters application state or configuration must log the initiating user to ensure proper tracking and accountability.
**Prevention:** Ensure all state-changing slash commands use parameterized `LOGGER.info` with an `AUDIT:` prefix to track the user (`interaction.user`) performing the action.
