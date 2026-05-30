## 2024-05-30 - Add Audit Logging to Admin Commands
**Vulnerability:** Lack of audit logging for state-changing administrative commands (`rotate`, `stop`, `delay`, `setchannels`) in the discord bot.
**Learning:** Administrative commands that modify system state or configure behavior should log the user taking the action to maintain accountability and support security investigations.
**Prevention:** Always ensure that any state-changing actions explicitly log an `AUDIT:` prefixed record with the user responsible for the action.
