## 2026-05-16 - Safe Error Handling and Docker Least Privilege
**Vulnerability:**
1. Hardcoded internal stack details or untrusted error representations were inadvertently leaked as a Discord bot user-facing error state via `str(exc)` inside a generic exception handler.
2. The Docker container was running under the default root account, violating the principle of least privilege.

**Learning:**
1. Exposing arbitrary underlying string representations of generic Python exceptions (e.g., `str(exc)`) directly to users is risky because it can leak environment layout, memory addresses, or sensitive state data that attackers shouldn't know.
2. Docker runs as root by default. Always add explicit `useradd` / `groupadd` sequences alongside a `USER` directive in Python applications. Even standard library tasks should map volume inputs properly with `chown`.

**Prevention:**
1. Replace generic exception variable assignments in UI/status fields with safe, standardized fallback messages such as "An unexpected internal error occurred."
2. Define a dedicated non-root execution user (like `appuser`) within custom Docker images.
