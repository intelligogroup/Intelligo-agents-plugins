# Removed

The `onBehalfOfClientId` override was removed. Scoping now always acts on the
caller's authenticated session org (the Clarity-login `orgId` carried in the
MCP token). To scope for a different org, log in as that org.

This file is no longer referenced by SKILL.md and should be deleted: `git rm`.
