# Security

- GitHub PAT is stored via `keyring` (Windows Credential Manager on Windows).
- PAT is never printed to logs.
- Auto-merge defaults to disabled in policy schema and examples.
- Merge strategies respect GitHub protections and return clear errors.
