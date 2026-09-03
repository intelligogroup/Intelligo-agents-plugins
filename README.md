# Intelligo for Agents

Bring **Intelligo** risk intelligence into your AI assistant. This connector links Claude
(and Gemini) to your Intelligo account so you can pull background checks, credit checks,
and adverse-media and social-media screening straight into the conversation — summaries,
risk flags, comparisons, and portfolio-wide trends, grounded in your own data.

## Install

**Claude Code**

```bash
claude plugin marketplace add intelligogroup/Intelligo-agents-plugins
claude plugin install intelligo@intelligo-tools
```

Or from an interactive session:

```
/plugin marketplace add intelligogroup/Intelligo-agents-plugins
/plugin install intelligo@intelligo-tools
```

**Claude (web & desktop)** — add Intelligo from the Connectors directory, or as a custom
connector: **Settings → Connectors → Add** → `https://clarityapi.intelligo.ai/mcp`.

**Gemini CLI**

```bash
gemini extensions install https://github.com/intelligogroup/Intelligo-agents-plugins
```

## What you get

The connector registers the Intelligo MCP server (`https://clarityapi.intelligo.ai/mcp`),
exposing your Intelligo projects, profiles, and report content to your assistant. Ask
things like:

- "Summarize the red flags on [subject]."
- "What changed since the last report on this profile?"
- "Which of our profiles mention [entity or keyword]?"

## Authentication

Sign-in is handled by Intelligo over OAuth on first connect — there are no API keys to
place in this repo or in any config. Your assistant can only access data your Intelligo
account is permitted to see.

## Requirements

A valid Intelligo account.

## Links

- Website — https://intelligo.ai
- Support & contact — https://intelligo.ai/contact
- Privacy policy — https://intelligo.ai/privacy

## Maintainers

Intelligo Group.
