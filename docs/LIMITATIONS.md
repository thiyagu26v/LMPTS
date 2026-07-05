# Limitations

1. **Single-user desktop app** — No concurrent multi-user access
2. **SQLite** — Not ideal for high-concurrency production (by design for capstone)
3. **No authentication** — All users share same interface
4. **GUI not auto-tested** — Manual verification required
5. **English only** — No i18n support
6. **In-memory graph** — Rebuilt on prerequisite changes (acceptable at scale)
7. **No network API** — Desktop-only deployment

These are acceptable for the capstone scope and documented for future enhancement.
