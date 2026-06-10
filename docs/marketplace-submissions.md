# Clarity — multi-platform marketplace submissions

Status and requirements for publishing the Clarity MCP connector across AI assistants.
This is the living tracker for the "publish to all AI marketplaces" effort.

## The one thing that makes this tractable

Every target platform now speaks the **same protocol: MCP (Model Context Protocol)**.
That means there is **one product to maintain** — the remote Clarity MCP server at
`https://clarityapi.intelligo.ai/mcp`, with OAuth handled at connect time — and each
"marketplace" is just a different way of *pointing users at that same server*.

So the work splits cleanly:

- **Server-side (one time, benefits all platforms):** make sure the MCP server meets the
  strictest platform's bar (currently ChatGPT — see its checklist below).
- **Per-platform (this repo + each dashboard):** the listing/manifest/submission for each
  storefront.

## Do ChatGPT and Gemini work the same way? Short answer: no.

They share the MCP core, but their **distribution models are opposites**:

- **ChatGPT** is a *centralized, reviewed* directory. You submit through OpenAI's
  dashboard (a web form, not a repo file), pass a review, and OpenAI lists you. This is
  most similar to the **Claude.ai connector directory**.
- **Gemini's** realistic third-party path today is *decentralized*: a **Gemini CLI
  extension** is just a public git repo with a `gemini-extension.json` manifest — no
  review, users install it directly. This is most similar to the **Claude Code plugin
  marketplace** (this repo). A separate, reviewed path exists for **Gemini Enterprise**.

| | Claude Code | Claude.ai connectors | ChatGPT (Apps SDK) | Gemini CLI extension | Gemini Enterprise |
|---|---|---|---|---|---|
| Core protocol | MCP | MCP | MCP | MCP | MCP |
| Distribution | Public git repo marketplace | Anthropic-curated directory | OpenAI-curated App Directory | Public git repo / release | GCP-managed connector |
| How you submit | Push repo; share `owner/repo` | Submit MCP URL in portal + review | Dashboard form + review | Publish repo; `gemini extensions install` | GCP console + security review |
| Repo artifact | `.claude-plugin/marketplace.json` + `plugin.json` | none (submit server URL) | none (web form) | `gemini-extension.json` | none (console config) |
| Review by vendor? | No | Yes | Yes | No (unvetted) | Yes (security review) |
| Auth | Server-side OAuth | Server-side OAuth | Server-side OAuth + reviewer demo account | Server-side OAuth (`dynamic_discovery`) | IAP / service account / OAuth |
| Status in this repo | ✅ Ready | ⏳ Assets needed | ⏳ Dashboard submission | ✅ Manifest shipped | ⏳ Enterprise-only |

---

## 1. Claude Code  — ✅ ready in this repo

- **Mechanism:** git-repo plugin marketplace. No review.
- **Files:** [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) (catalog) +
  [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) (plugin) at repo root.
- **Install:**
  ```bash
  claude plugin marketplace add intelligogroup/clarity-agents-plugins
  claude plugin install intelligo-clarity@clarity-tools
  ```
- **Remaining:** commit + push; confirm the GitHub repo exists/public.

## 2. Claude.ai Connectors Directory  — ⏳ submit the MCP server (this is the screenshot)

This is the curated directory in Claude.ai → Customize → Connectors ("Anthropic &
Partners"), alongside Canva, Notion, Slack, etc. **The vehicle is the remote Clarity MCP
server itself — not this repo.** Two outcomes:

- **Use it in your org now (not public):** an org **Owner** goes to Organization settings
  → Connectors → **Add**, and pastes `https://clarityapi.intelligo.ai/mcp` (optionally an
  OAuth client id/secret under Advanced). Members then connect individually. Self-serve,
  instant. Available on Free/Pro/Max/Team/Enterprise (beta).
- **Get listed publicly (be "there"):** submit to the **Connectors Directory** for
  Anthropic review; approved connectors become available to all Claude users.

**Submit at:** `https://claude.ai/admin-settings/directory/submissions/new`
(track at `.../directory/submissions`). No Team/Enterprise portal access? Use the public
form `https://clau.de/mcp-directory-submission`.

**Who can submit:** Team/Enterprise org, **Owner / Primary Owner** by default. Enterprise
can delegate via a custom role with the **Directory management** permission.

**Server requirements (Clarity API team):**
- HTTPS; transport = streamable HTTP or SSE (✅ current `.mcp.json` is `http`)
- OAuth 2.0 with user-consent flow (✅)
- **Every tool needs `title` + `readOnlyHint` or `destructiveHint`** — missing annotations
  cause ~30% of rejections
- Tool results ≤ 25,000 tokens; tool handlers finish within 5 min (300s)
- Declare allowed link URIs (HTTPS origins you own)

**Listing assets (portal stages 4–6):**
- Name ≤ 100 chars · Tagline ≤ 55 · Description ≤ 2,000 · 1–5 categories
- **Icon/logo** (square; exact spec stated in the portal) — see Assets below
- **Screenshots:** PNG, ≥ 1000px wide, **3–5 images**, crop to the app response only (not
  the prompt; supply prompt text separately). No video/GIF.
- Documentation URL · **Privacy policy URL (HTTPS)** · support contact · URL slug (permanent once published)
- **Missing/incomplete privacy policy = immediate rejection**

**Test & launch:** a fully-populated **demo account** + step-by-step reviewer access
instructions; confirm you've run every tool (via MCP Inspector or as a custom connector).

### Draft listing copy (ready to paste)
- **Name:** `Intelligo Clarity`
- **Tagline:** `Risk intelligence & background checks, inside Claude`
- **Categories:** Security & Compliance · Research · Productivity (match to the portal's list)
- **Description:**
  > Intelligo Clarity brings AI-powered risk intelligence into Claude. Connect your Clarity
  > account to surface what matters across background checks, credit checks, and
  > adverse-media and social screening — without leaving the conversation.
  >
  > With Clarity connected, Claude can: summarize a profile's key findings with red/yellow
  > risk flags; compare reports (what changed since a prior check, or overlaps across
  > profiles); surface risk trends across your portfolio (flags over time, emerging risks,
  > keyword search); and turn findings into investment-committee-ready materials.
  >
  > Built for due-diligence, compliance, and investment teams who need defensible,
  > source-backed answers fast. Authentication is via OAuth; Claude only accesses data the
  > signed-in user is permitted to see. Requires an Intelligo Clarity account with API access.

## 3. ChatGPT — Apps SDK / App Directory  — ⏳ dashboard submission

OpenAI is **accepting third-party app submissions** (App Directory). There is **no repo
manifest** — submission is a form in the OpenAI developer dashboard. Self-serve publishing
is "coming soon"; today it's the dashboard review flow.

**Account / eligibility**
- Verified organization (business verification → company name is published) with
  `api.apps.write` / `api.apps.read` permissions on the OpenAI Platform.

**Listing assets to prepare (paste into the dashboard):**
- Icon: **64 × 64 px, under 5 KB**
- App name: **≤ 30 chars**, clear, not a generic single word — e.g. `Intelligo Clarity`
- Short + long description
- Screenshots that accurately show functionality
- Developer name, **verified website**, support contact
- **Privacy policy URL** (must list: categories of personal data collected, purpose,
  recipients, retention) and **terms & conditions**
- Country availability + localization

**Server / technical requirements (action items for the Clarity server team):**
- Publicly accessible domain (✅ `clarityapi.intelligo.ai`)
- **Tool annotations** on every tool: `readOnlyHint`, `destructiveHint`, `openWorldHint`
- **Structured output**: tools return `structuredContent` + `content`, each with an
  `output_schema` (JSON Schema)
- **Content Security Policy** allowing exactly the domains the app fetches from
- Transport: MCP over streamable HTTP / SSE — confirm compatibility with ChatGPT
- **Demo account**: a fully-featured login + password with sample data and **no MFA**,
  for the review team
- Do **not** collect payment-card, health, government-ID, or credential data; no ads

**Process:** test in **Developer Mode** (works on web + mobile) → submit draft → automated
+ manual review (connectivity, test cases, privacy audit, annotation checks) → approve /
reject-with-feedback / appeal. Only one version under review at a time; timeline varies.

## 4. Gemini  — ✅ CLI manifest shipped; ⏳ enterprise path

There are three Gemini surfaces; pick by audience.

**a) Gemini CLI extension — shipped in this repo.**
- **Files:** [`gemini-extension.json`](../gemini-extension.json) + [`GEMINI.md`](../GEMINI.md)
  at repo root. Points at the same Clarity MCP server with `authProviderType:
  "dynamic_discovery"` (standard MCP OAuth).
- **Distribution:** public git repo / GitHub release, installed directly. No Google review.
- **Install:** `gemini extensions install https://github.com/intelligogroup/clarity-agents-plugins`
  (verify exact flag/syntax against the Gemini CLI releasing guide).

**b) Gemini Enterprise custom MCP connector — for enterprise customers.**
- Configured in the Google Cloud console as a custom MCP server data store; subject to a
  Google security review. Auth via IAP / service-account impersonation or OAuth.

**c) Consumer Gemini app "connected apps".**
- As of mid-2026, connecting an arbitrary third-party MCP server to the consumer Gemini
  app is **not generally self-serve for SaaS** (largely partner-gated, per Google's
  community threads). Track this; the CLI extension is the open path today.

---

## Shared open items (needed by ChatGPT + Claude.ai, nice for all)

- [ ] **Logo / icon** (incl. 64×64 ≤5KB for ChatGPT)
- [ ] **Public privacy policy URL** covering data categories, purpose, recipients, retention
- [ ] **Terms & conditions URL**
- [ ] **Screenshots** of Clarity in use
- [ ] **Reviewer demo account** (login + password, sample data, no MFA)
- [ ] **Org verification** on OpenAI (and confirm on Anthropic)
- [ ] **Server team:** tool annotations + structured `output_schema` + CSP on the MCP server

## Sources

- [Submit and maintain your app — OpenAI Apps SDK](https://developers.openai.com/apps-sdk/deploy/submission)
- [App submission guidelines — OpenAI Apps SDK](https://developers.openai.com/apps-sdk/app-submission-guidelines)
- [MCP & connectors — OpenAI API](https://developers.openai.com/api/docs/mcp)
- [Developers can now submit apps to ChatGPT — OpenAI](https://openai.com/index/developers-can-now-submit-apps-to-chatgpt/)
- [MCP servers with Gemini CLI](https://geminicli.com/docs/tools/mcp-server/)
- [Gemini CLI — writing extensions](https://geminicli.com/docs/extensions/writing-extensions/)
- [Set up a custom MCP server — Gemini Enterprise](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/custom-mcp-server/set-up-custom-mcp-server)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
