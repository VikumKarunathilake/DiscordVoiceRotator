## 2026-05-19 - Missing Authorization on Slash Commands & Sensitive Data Exposure in Error Responses

**Vulnerability:**
1. The `/status` slash command lacked the necessary permission decorators and internal checks, allowing any Discord user to execute it.
2. The unexpected exception handler in `services/rotation_service.py` set `status.last_error` to `str(exc)`, leaking raw exception strings (which could contain stack traces or environment paths) to Discord users viewing the rotation status.

**Learning:**
1. Slash commands without `@app_commands.default_permissions()` or explicit code checks can be executed by anyone in a guild. Default server permissions don't automatically restrict all slash commands unless configured.
2. Direct serialization of raw exceptions to user-facing API or Discord bot responses is a severe information disclosure vector, especially in long-running tasks or background workers.

**Prevention:**
1. Always apply `@app_commands.default_permissions(move_members=True)` and internal authorization validation (`if not await self._can_manage_rotations(interaction): return`) to sensitive bot commands.
2. Ensure generic, safe error messages are returned to users while retaining full `LOGGER.exception()` calls in the backend to capture debugging context without exposing it.
