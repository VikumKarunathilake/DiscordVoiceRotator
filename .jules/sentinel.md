## 2024-05-24 - Missing Authorization Check on Status Endpoint
**Vulnerability:** The `/status` slash command lacked permission checks, allowing any user in a guild to view active rotation configurations and potentially sensitive error messages, bypassing the intended `move_members` restriction used by all other management commands.
**Learning:** Even read-only diagnostic commands can leak sensitive internal state (like error strings or server configurations) and should be protected with the same authorization boundary as the operations they monitor.
**Prevention:** Always apply consistent role-based access control (RBAC) across both read and write commands in a feature set, unless explicit unauthenticated access is required.
