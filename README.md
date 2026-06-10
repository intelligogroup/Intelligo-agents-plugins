# clarity-agents-plugins

The official [Claude Code](https://code.claude.com) plugin marketplace for
**Intelligo Clarity**. It distributes the `intelligo-clarity` plugin: the Clarity
risk-intelligence MCP connector bundled with skills for working with Clarity
background-check data.

## Install

Add the marketplace, then install the plugin:

```bash
claude plugin marketplace add intelligogroup/clarity-agents-plugins
claude plugin install intelligo-clarity@clarity-tools
```

Or from inside an interactive Claude Code session:

```
/plugin marketplace add intelligogroup/clarity-agents-plugins
/plugin install intelligo-clarity@clarity-tools
```

## What you get

The `intelligo-clarity` plugin registers:

- **Clarity MCP connector** — an HTTP MCP server pointing at Clarity's hosted
  endpoint (`https://clarityapi.intelligo.ai/mcp`), exposing Clarity projects,
  profiles, and report content.
- **Four skills** that trigger from natural language:

  | Skill | What it does |
  |-------|--------------|
  | `intelligo-profile-summary` | Factual summary of one profile — background, credit, social — with red/yellow flags and key findings. |
  | `compare-clarity-reports` | What changed since a prior report, or what overlaps across profiles. Read-only. |
  | `intelligo-risk-trends` | Risk trends across many reports — flags over time, emerging risks, keyword search; summary, table, charts, or live dashboard. |
  | `intelligo-prep-committee-deck` | Turns Clarity findings into IC-ready narratives, PDFs, or PPTX decks. |

## Authentication

Auth is handled by the Clarity MCP server at connect time (OAuth). There are no
API keys to place in this repo or in the manifest.

## Requirements

- A valid Intelligo Clarity account with access to the Clarity API.

## Updating

The plugin version lives in `plugins/intelligo-clarity/.claude-plugin/plugin.json`.
Bump it on every release so existing users pick up changes via
`/plugin marketplace update`. (Omit it to track the commit SHA instead.)

## Layout

```
.claude-plugin/
  marketplace.json              # marketplace catalog (lists the intelligo-clarity plugin)
plugins/
  intelligo-clarity/
    .claude-plugin/plugin.json  # plugin manifest
    .mcp.json                   # Clarity HTTP MCP server
    skills/                     # the four skills above
```

## Other AI platforms

The same Clarity MCP server powers connectors on ChatGPT and Gemini too — they all speak
MCP, so there's one server to maintain. This repo also ships a **Gemini CLI extension**
manifest ([`gemini-extension.json`](gemini-extension.json) + [`GEMINI.md`](GEMINI.md)):

```bash
gemini extensions install https://github.com/intelligogroup/clarity-agents-plugins
```

ChatGPT (Apps SDK) is submitted via OpenAI's dashboard rather than a repo file. See
[docs/marketplace-submissions.md](docs/marketplace-submissions.md) for the full
cross-platform status, requirements, and checklists.

## Maintainers

Intelligo — internal back-office / platform engineering.
