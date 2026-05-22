## 2024-05-18 - Missing Audit Logging for Administrative Commands
**Vulnerability:** The application was missing audit logging for critical, state-changing slash commands (e.g., `rotate`, `stop`, `delay`, `setchannels`), meaning there was no programmatic way to determine which user initiated an administrative action. This violates the security principle of non-repudiation.
**Learning:** Even though Discord tracks who uses an interaction on their end for some time, the application itself needs to explicitly log administrative operations mapped to the initiating user for independent auditing and troubleshooting.
**Prevention:** Any new state-changing administrative command should include a parameterized log statement using the format `LOGGER.info("AUDIT: User %s did X", interaction.user)`.
