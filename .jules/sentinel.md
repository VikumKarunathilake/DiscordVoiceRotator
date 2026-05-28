## 2024-05-28 - Add audit logging for state-changing operations
**Vulnerability:** Missing audit logs for administrative / state-changing operations. It was difficult to trace which user performed actions like starting/stopping voice channel rotations and changing configuration options.
**Learning:** For a Discord bot, always ensure that administrative commands that change persistent state or invoke rate-limited operations on users are logged with the invoking user's ID for accountability.
**Prevention:** In the future, require parameterized logging (e.g., `LOGGER.info("AUDIT: User %s did X", user)`) for all slash commands handling significant state mutations.
