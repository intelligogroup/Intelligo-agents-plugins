---
name: intelligo-profile-summary
description: >-
  High-level factual summary of one Intelligo profile — background check, credit check, and
  social media analysis, with executive summary, red/yellow flags, and key findings. Summarizes one
  profile (person or company), not a project; if the query is ambiguous it searches profiles and
  projects, and hands a project off to the project-summary skill. Use whenever the user wants a
  summary, recap, key takeaways, risk read, red flags, or major risks on a person or company in due
  diligence — even without saying "Intelligo." Offers four selectable views (executive summary, flag
  count, flags + findings, per-tab breakdown) and asks which when unspecified. Triggers: "summarize
  X", "red flags on X", "what did we find on X", "how many flags on X", "exec summary on X", "break X
  down by tab". Do NOT use for web research, monitoring, action items, or project-level summaries.
---

# Intelligo Profile Summary

Turn an Intelligo **profile** into a high-level, factual summary the user can read in under a minute.

## Data model (overview)

Hierarchy: `Project → Profile → Report → Card → Flag`. Sources link to Cards. Linked Notes attach to Cards. This hierarchy is **conceptual** — `Get_report_content` returns Report, Cards, and Flags together in one response (see Connector tools).

**Profile** is the DD subject (Person or Company shape — see tool specs for field-level detail).

**Report** belongs to a profile, carries a product type (background check, credit check, social media analysis), a status, and a format (card-based for BG checks, PDF for credit / social media). Multiple reports of the same product type can exist on a profile, distinguished by creation time; the skill picks among them by status (see Step 2).

**Card** is a finding item inside a card-based report. Each card has a type (which determines its content fields — professional, education, news, legal, etc.). Cards do **not** have a reliable generic description field — the skill renders type-specific fields instead.

**Flag** is a separate object linked from a Card. Surfacing a flag means showing flag.name + flag.description alongside the card it points to.

### Report status — what's summarizable

| Status | Usable? |
|---|---|
| Pending consent | No — falls back to older complete report if exists, otherwise skip |
| In progress | No — same fallback as Pending consent |
| Preliminary | Yes, with prominent caveat (not human-verified) |
| Ready | Yes, normal |
| Reviewed | Yes, normal (equivalent to Ready for summary purposes) |

### Report format — what the skill can do

| Product | Format | Skill can read content? |
|---|---|---|
| Background Check | Card-based | Yes — iterates cards, renders by type |
| Credit Check | PDF | Connector returns metadata only (flag counts, optional exec summary, link). The document text is readable **only when the PDF is uploaded/available** — see PDF content access below |
| Social Media Analysis | PDF | Same as Credit Check |

#### PDF content access

`Get_report_content` returns only the PDF's metadata (URL, flag counts, optional exec summary) — never the document text. But the skill **can** read and summarize a PDF when the file itself is available to it (the user uploaded the report into the conversation, or it's otherwise readable):

1. **PDF content available** → read it and answer or summarize normally, exactly like any other source. Don't limit yourself to metadata.
2. **Not available, and the user wants PDF detail** → ask the user to upload the report PDF.
3. **Still unavailable** → do **not** continue with the PDF: never guess or fabricate its content. Fall back to the connector metadata (flag counts + link) and tell the user the content isn't available.

The skill never invents PDF content.

### Summary-text source — one rule, all formats

1. If the report carries an analyst-written executive summary → use it (verbatim or near-verbatim; light editing for length OK).
2. Else, card-based → synthesize a short overview from the cards and flags.
3. Else, PDF → if the PDF content is available, summarize from it; otherwise surface flag counts + link (see PDF content access).

The skill does **not** branch on the BG-check level. Background checks carry a free-form variant label (e.g. "A3 Advantage - Level 3", "Now", "AML", "Go") — the skill displays it verbatim in the section header but doesn't change behavior based on it.

### In/out of scope

- **In scope:** Profile (for ID only), Reports (DD products, most recent per product), Cards, Flags, Linked Notes (inline with their finding).
- **Out of scope:** Monitoring (separate product), all Action items (Refresh, Reviewed, Add Monitoring, Upgrade, Flag Action Item), Comments.
- **No opinions:** no investment recommendations, no risk verdicts, no singling out / ranking ("the most material is X", "focus on Y"). Severity ordering (red → yellow → other) is the only allowed prioritization signal.

## Connector tools

The connector exposes **three tools**: `Get_profiles`, `Get_projects`, and `Get_report_content`. Field-level names are owned by engineering and live in the connector's own docs; this section specifies what each tool gives the skill.

The data hierarchy — Project → Profile → Report → Card → Flag — is a **concept**, not a tool layout: `Get_report_content` returns **Report + Cards + Flags together** in a single call.

### `Get_profiles` — resolve a name; returns profile detail + report list

Given a query (a name, partial name, or company name), return the matching profile candidates. This one tool covers both resolving the profile and learning which reports exist on it — there is no separate profile-detail call. Each candidate carries:

- Enough identifying metadata to disambiguate persons from companies and display in a picker. `references/profile-resolution.md` lists which fields to surface per case (Sr/Jr, duplicates, subsidiaries, common name).
- The profile's full identifying fields (person or company shape). The skill surfaces only the minimum needed to confirm the subject (Bucket 1); extended fields — emails, social media handles, full addresses, related key people — are present but not surfaced unless a finding references them.
- The profile's **report list** — every report attached, with the metadata Step 2 needs: a **report id** (to pass to `Get_report_content`), product type, status, and creation time. Multiple reports of the same product type can appear, distinguished by creation time; the skill picks among them by status (see the status taxonomy in the data model).

### `Get_projects` — resolve a name to a project

Same search shape as `Get_profiles`, but for projects (investments). Called in parallel with `Get_profiles` in Step 1 because the user's query might name a project, not a profile.

Each candidate project includes a short preview of the profiles attached to it (typically the first several, not all). The skill uses this preview both for disambiguation (e.g. "Acme Series B — 3 profiles under it: Acme Holdings, Jane Doe, John Smith") and as a fallback path: if the user picks the project but the project-summary skill isn't available, the skill can offer to summarize one of the listed profiles instead.

### `Get_report_content` — one report id → that report, with cards + flags merged

Takes a **single report id** (from the report list `Get_profiles` returned) and returns that one report's content. **Call it once per report** the skill decided to summarize — fetch in parallel across reports where possible. The shape depends on the product's format:

**Card-based reports (background checks):** the report's optional analyst-written executive summary, plus its findings as a list of cards, plus the flags raised — all in one response. Each card has a type (which determines its content fields), a title, optional verification state, and optionally a linked note (analyst-added context). Each flag has a severity (red or yellow), a name, a description (the analyst's reason for flagging), and a link to its card. Report, Card, and Flag remain distinct concepts but arrive merged here.

**PDF reports (credit check, social media analysis):** a stable URL to the PDF document, optional filename, flag counts, and rarely an executive summary. This tool returns only the metadata around the PDF, not its text — but the skill can read the document itself when the PDF is uploaded/available (see PDF content access).

### Concepts the skill relies on

A few specifics the skill encodes as logic and that need to map cleanly to whatever the connector returns (these all arrive inside `Get_report_content`'s card payload):

- **Verification state on cards.** The skill renders three states differently: confirmed against a source, explicitly unverified by an analyst (no source supports it), and no analyst position. The connector exposes this however it likes (a tri-state field, two booleans, etc.) — the skill expects to be able to distinguish all three.
- **Collaborators on profiles and projects.** Returned for authorization/visibility purposes. The skill does not surface this in summaries unless the user explicitly asks about access.
- **Linked notes on cards.** Optional analyst-added context attached to a card. The skill renders these inline with their finding when they add information beyond what the flag already conveys.

### Behavior if a tool is missing or returns nothing

- `Get_profiles` unavailable → ask the user for more details (company, project, jurisdiction, role); without resolution the skill can't proceed.
- `Get_projects` unavailable → skip the project-collision check; proceed with profile search only.
- `Get_profiles` returns a profile but no report list → if the user gave enough data to refine search, ask for more specifics; if only a name, stop.
- `Get_report_content` unavailable or empty → stop and tell the user the connector isn't returning report content.

Never invent content the connector didn't return.

## Step 1 — Resolve to a Profile

**Read `references/profile-resolution.md` first.** That reference defines the resolution logic: searching profiles + projects in parallel, disambiguating multiple matches, recognizing edge cases (Sr/Jr, duplicates, subsidiaries, common names), the combining-with-warning behavior, and the rule about reusing an already-resolved profile from earlier in the conversation. It's shared across future Intelligo skills.

This skill's specific decisions after resolution:

1. **User picks a profile** → proceed to Step 2.
2. **User picks a project** → hand off to the project-summary skill if available. If unavailable, list the profiles under the project (returned alongside each project in the search results) and offer to summarize one instead.

## Step 2 — Pick the right report per product

`Get_profiles` already returned the profile's full metadata and its report list during Step 1 resolution. From that list:

1. Filter out any monitoring entries.
2. Group remaining entries by product type.
3. For each product group, sort by creation time newest first, then walk the list with the **status-aware selection rules** below.
4. Silently skip products with no entries (e.g. credit check wasn't run).

If no product yields a summarizable report, tell the user plainly what's available and what isn't, then stop.

### Status-aware selection (per product)

Walk the product's reports newest-first by creation time:

| Latest status | Action |
|---|---|
| Ready or Reviewed | Use it. |
| Preliminary | Use it. Add a preliminary caveat alert (see Bucket 2 in Step 3). |
| In progress | Use an older Ready or Reviewed report from the same product group if one exists, with a fallback caveat alert. If none exists, skip this product and tell the user. |
| Pending consent | Same logic as In progress. |

If any product fell back to an older report or was skipped entirely, surface it in both the profile-level intro line AND the product section — the user should see the warning in both places.

If the user explicitly asked for a different version (in-progress, preliminary, an older one), override the default and use the one they asked for. Status caveats still apply.

For each selected report, call `Get_report_content` with its report id to fetch the full content (cards + flags merged). Fetch in parallel across reports where possible.

### Narrowing to a single product

If the user named a single product ("just the background check"), apply the same selection rules only for that product.

## Step 3 — Choose a summary view, then write

The skill offers **four independent summary views**. They're self-contained, but the user can ask for one or several — deliver exactly what their request calls for, combining views in a single response when needed, with no extra prompting once the need is clear. Two buckets always render (profile ID + alerts); the chosen view(s) fill the body. After delivering, the skill offers to go deeper into anything not yet shown.

### The four views

| View | Returns | Products |
|---|---|---|
| **Executive summary** | The analyst exec-summary text (verbatim / light edit) **plus the red/yellow flags** (BG → flag lines: severity, name, description; PDF → flag counts). No exec summary? BG → a 2–3 sentence overview synthesized from cards; PDF → if the PDF is available, summarize from it, else note the summary lives in the PDF + link. Omits non-flagged cards. | All |
| **Flag count** | Red / yellow flag counts per product (a fast risk gauge); optionally broken down per report tab/category on request (BG only). No names, no descriptions. | All |
| **Flags + findings** | The full per-finding list (the detailed view). BG → iterates cards; PDF → if available, summarize findings from the document, else flag counts + PDF link. | All |
| **Per-tab summary** | A 1–2 sentence synthesis per card category/tab present (Professional, Legal, News, Education, Regulatory, etc.). Organized by category, not by flag. | BG only; PDFs have no tabs — if available, a short summary from the document, else counts + link |

### Picking the view

- **Phrasing names a level → use it, don't ask:**
  - "exec summary", "the gist", "tl;dr", "high level", "key takeaways", "what should I know about X", "most important info" → Executive summary
  - "how many flags", "flag count", "how many red/yellow flags", "risk gauge", "do we have any risk on X", "anything concerning?" → Flag count ("…by tab/section/category" → Flag count with the per-tab breakdown)
  - "findings", "what did we find", "key findings", "show me / all the red flags on X" (scope to red-flagged items), "just the yellow flags" → Flags + findings
  - "by category", "by section", "per tab", "break it down by area" → Per-tab summary
- **Risk-oriented phrasing** ("any risk", "red flags", "what should I worry about") maps to whichever view above fits — but the skill stays factual: it reports what was flagged and never gives a risk verdict or investment opinion (see "No opinions" in the data model). Severity order (red → yellow) is the only allowed prioritization.
- **Phrasing names several levels, or asks for "everything" / "the full picture" / "all of it" → deliver those views together in one response, don't ask.** Render them in canonical order: Executive summary → Flag count → Flags + findings → Per-tab summary. "Everything" means all four.
- **Just "summarize X" with no level → ask**, after resolving the profile and checking what's available. The user may pick one or more:

  > "Which level(s) do you want for [Name]? (pick any — I can combine them)
  > 1. **Executive summary** — the analyst's headline read
  > 2. **Flag count** — just how many red / yellow flags
  > 3. **Flags + findings** — the full flagged-finding list
  > 4. **Per-tab breakdown** — short summary by category (Professional, Legal, News…)"
- **A single product was named** ("just the background check") → the chosen view(s) apply within that product only.

### Always shown in every view: profile ID + alerts

Buckets 1 and 2 render regardless of the chosen view — the user must confirm the subject and see caveats at any depth.

### Bucket 1 — Profile identification

The minimum needed to confirm the right profile — name + a few identifying fields per type. Anything beyond this (addresses, emails, social media, related key people, etc.) stays out of this bucket and only surfaces if a finding directly references it.

- **Persons:** name, current Position @ Company, date of birth (use what the connector returns — full date, year only, or whatever's available; omit silently if unknown), jurisdiction, project name.
- **Companies:** name, company type, HQ City + Country, jurisdiction, project name. When HQ location and jurisdiction are the same, show one — don't repeat (e.g. a Delaware US company HQ'd in Delaware shows "Delaware US" once, not twice). When they differ (e.g. Delaware corp HQ'd in NYC), show both.

### Bucket 2 — Alerts (only if applicable)

Caveats the user needs to see *before* reading the summary. Each on its own line, prefixed `⚠`. Omit the bucket entirely if no alerts apply. Examples:

- ⚠ Preliminary report — not human-verified. Data may change in the final version.
- ⚠ The most recent background check is still in progress. This summary is from the previous report (Feb 2026).
- ⚠ Combined output across N profiles — see warning at the top.

The combining warning has its full text specified in `references/profile-resolution.md`. Use that exact warning when the user explicitly asked to combine profiles.

### Bucket 3 — View body

The body is the chosen view. Every view renders one section per product that exists on the profile (BG, Credit, Social) — silently skip products that weren't run. Length is short by default (the user is time-constrained) but **not capped**: extend when the content is genuinely substantial.

**Executive summary view.** Per product, the analyst exec-summary text (verbatim or lightly edited for length), **followed by the report's flags** — for a BG check, the red/yellow flag lines (severity · name — description, using the finding-line format but only the flagged items); for a PDF, the flag counts. If a product has no exec summary: BG → synthesize a 2–3 sentence overview from its cards and flags; PDF → if the PDF content is available, write a short summary from it, otherwise state the summary is only in the PDF and give the link (see PDF content access). Omits non-flagged cards and per-card type detail (that's the Flags + findings view).

**Flag count view.** Per product, the red / yellow counts only — e.g. "Background Check: 2 red, 3 yellow." No flag names or descriptions. If a product has zero flags, say so ("no flags"). Available for all products, including PDFs (counts come from metadata). **Optional per-tab breakdown:** when the user asks (e.g. "flag count by tab", "how many flags in each section"), break the counts down per report tab/category for a BG check — "Background Check — 5 total · Professional 1 red · Legal 1 red, 2 yellow · News 1 yellow." Default is the per-product total; the breakdown applies only on request and only to card-based reports (PDFs have no tabs, so they stay at the product total).

**Flags + findings view.** The detailed view. Per product: BG checks render the full per-finding list (see "Rendering a finding line," "Ordering," and "Findings filter" below). PDF products: if the PDF content is available, summarize its findings from the document; otherwise show flag counts + the PDF link (see PDF content access). If the user scopes to a severity ("all the red flags", "only the yellow flags"), render just that tier and omit the rest; if that tier is empty, say so plainly.

**Per-tab summary view (BG check only).** Group the BG check's cards by category/tab (Professional, Legal, News, Education, Regulatory, etc.). For each category that has content, write a 1–2 sentence synthesis of what's there, noting whether it carries flags (e.g. "Legal — one red-flagged item, a 2019 civil judgment; rest clean."). Organize by category, not by severity. Skip categories with no cards. PDF products have no tabs to break down — if their content is available, give a short summary from the document, otherwise fall back to flag counts + PDF link.

### Output skeletons

Every view opens with the ID line + any alerts:

```
**[Profile Name]**
[Persons: Position @ Company, b. [DOB as returned] · [Jurisdiction] · Project: <project name>]
[Companies: Company Type · HQ City, Country · [Jurisdiction] · Project: <project name>]

[⚠ Alert lines, each on its own line — only if applicable.]
```

**Executive summary view**
```
### Background Check — [variant label verbatim, e.g. "A3 Advantage - Level 3"]
[Exec summary, or synthesized 2–3 sentence overview.]
Flags:
- 🔴 RED · [flag name] — [flag description].
- 🟡 YELLOW · [flag name] — [flag description].

### Credit Check
[Exec summary if present; else summarize from the PDF if it's available; else: "Summary is in the PDF — (link)."]
Flag counts: N red, M yellow.
```

**Flag count view**
```
Background Check — 2 red, 3 yellow
Credit Check — 0 red, 1 yellow
Social Media Analysis — no flags
```
Per-tab breakdown (on request, BG only):
```
Background Check — 5 total
- Professional — 1 red
- Legal — 1 red, 2 yellow
- News — 1 yellow
Credit Check — 0 red, 1 yellow   (PDF, no tabs)
```

**Flags + findings view**
```
### Background Check — [variant label verbatim]
[Exec summary if present, else synthesized short overview.]

Findings:
- 🔴 RED · [flag name] — [flag description]. Card: [card title]. [Type-specific context if it adds value.]
- 🟡 YELLOW · [flag name] — [flag description]. Card: [card title]. [Type-specific context.]
- [card title] — [type-specific content for non-flagged material cards]. [Verified: yes/no if set.]

### Credit Check
[Exec summary if present.]
Flag counts: N red, M yellow.
Full report: [filename or "Credit Check PDF"] (link)

### Social Media Analysis
[Same structure as Credit Check.]
```

**Per-tab summary view (BG only)**
```
### Background Check — [variant label verbatim]
- **Professional** — [1–2 sentence synthesis]. [flags noted if any]
- **Legal** — [1–2 sentence synthesis]. [flags noted if any]
- **News** — [1–2 sentence synthesis].
- [other categories present…]

(Credit / Social have no tabs — show flag counts + PDF link instead.)
```

Every view closes with a one-line "go deeper" offer (see below).

### Rendering a finding line

These rules apply to the **Flags + findings view** (and the flag-noting in the Per-tab view). Order is **always: flag first, card second.** The flag is the headline (severity + reason for flagging); the card is supporting context. Card titles can be cryptic and there's no reliable generic description on a card, so the flag is what carries substance.

1. `🔴 RED ·` or `🟡 YELLOW ·` — severity prefix. **The icon color must match the flag's severity: 🔴 for red flags, 🟡 for yellow flags. Never use a red icon for a yellow flag or vice versa.**
2. [flag name] — [flag description] — what and why.
3. Card: [card title] — the underlying card.
4. **Type-specific context** — when the title alone doesn't carry the substance, add the type-specific fields that genuinely help the user understand the finding. Use judgment: pick the fields that identify and contextualize the item without padding. The exact set varies by card type and by what's populated. Some patterns:
   - Professional cards → position, company, dates
   - Education cards → degree, institution
   - News cards → article date, short summary text
   - Legal cards → case type, jurisdiction
   - Other types: surface whatever type-specific fields are populated and add information beyond the title; otherwise stop at the title.
5. If a linked note is attached AND adds something beyond the flag/card content → append the note inline. Skip if redundant.
6. If the card has an explicit verification state → append "Verified: yes" or "Verified: no — no source confirms this." Skip if absent (no analyst position).

Non-flagged material cards use the same type-specific rendering, just without the flag prefix.

### Ordering within a finding list

1. 🔴 RED-flagged cards first
2. 🟡 YELLOW-flagged cards next
3. Non-flagged material cards last

Within each tier, preserve the order Intelligo returned. The connector's order reflects Intelligo's classification — keep it.

### Findings filter — what stays out of the list

These items belong to the data model but stay out of the rendered findings list. Listed here so it's clear they're intentionally excluded, not missed:

- Routine clean sections. (A clean section gets one line *only if* its cleanliness is itself notable, e.g. "No adverse legal records found.")
- Findings that aren't material.
- Same finding appearing in multiple reports → mention it under the section carrying the higher-severity flag, with a short cross-reference noting it also appears in the other report. One full description per finding, even when the finding shows up in multiple places.
- Profile metadata beyond what's on the ID line.
- Redundant linked notes.
- Fabricated detail. If a report doesn't say it, don't infer it.

### Offer to go deeper

After delivering, close with a one-line offer naming only the views **not already shown** (skip anything already included in this response):

- After **Executive summary** or **Flag count** → "Want the full flags + findings, or a per-tab breakdown?"
- After **Per-tab summary** → "Want the full flags + findings for any category?"
- After **Flags + findings** (or when all four views were already delivered) → "Want me to drill into any specific finding?"

## Examples

**Example 1 — plain "summarize" with no level → ask which view:**
> User: "Summarize what we have on Sarah Levin."
> [Profile resolved → BG Check (card-based, latest), Credit Check (PDF, latest), Social Media (PDF, latest); monitoring filtered out]
> Since no level was specified, ask: "Which level of summary do you want for Sarah Levin? 1. Executive summary · 2. Flag count · 3. Flags + findings · 4. Per-tab breakdown."
> The user picks; the skill renders only that view, then offers to go deeper.

**Example 1a — Executive summary view:**
> User: "Give me the exec summary on Sarah Levin." (or picks 1 above)
> Per product, render the analyst's exec summary text, then the red/yellow flags (BG → flag lines; PDF → flag counts). Non-flagged cards are omitted. Close: "Want the full flags + findings, or a per-tab breakdown?"

**Example 1b — Flag count view:**
> User: "How many flags on Sarah Levin?"
> ID line + alerts, then: "Background Check — 2 red, 3 yellow · Credit Check — 0 red, 1 yellow · Social Media — no flags." No descriptions. Close: "Want the full flags + findings, or a per-tab breakdown?"

**Example 1c — Flags + findings view (the detailed default lens):**
> User: "What did we find on Sarah Levin?" (or picks 3)
> BG Check iterates cards as findings; Credit/Social show flag counts + PDF link (or a summary from the document if the PDF is uploaded). Close: "Want me to drill into any specific finding?"

**Example 1d — Per-tab summary view:**
> User: "Break Sarah Levin's background check down by category."
> One line per category present: "Professional — 12 yrs at two PE firms, no gaps. · Legal — one red-flagged item, a 2019 civil judgment; rest clean. · News — minor coverage, nothing adverse." Credit/Social fall back to counts + link. Close: "Want the full flags + findings for any category?"

**Example 1e — combined views in one response (no extra prompting):**
> User: "Give me the exec summary and the flag count for Sarah Levin." (or "give me everything")
> Deliver both (or all four for "everything") in a single response, in canonical order: ID line + alerts, then Executive summary, then Flag count. No picker. Close by offering only what wasn't shown.

**Example 2 — partial coverage, silent skip:**
> User: "What did we find on Acme Holdings?"
> [Profile fetched → BG Check only]
> Summarize BG Check. The summary stays focused on what exists; products that weren't run are silently absent from the output.

**Example 3 — narrowing to one product:**
> User: "Just give me the background check on Sarah Levin."
> Restrict to the background check product only.

**Example 4 — no DD reports, only monitoring:**
> User: "Summarize what we have on Marcus Webb."
> [Profile fetched → only monitoring]
> "This profile has no due-diligence reports to summarize — only monitoring, which isn't covered by this flow."

**Example 5 — alternate-vocabulary triggers:**
> User A: "Summarize the candidate Sarah Levin."
> User B: "What did we find on the entity Acme Holdings?"
> User C: "Give me a recap on the investment subject."
> All three trigger the same way. The skill resolves to the right Profile and produces the standard summary. User B's "the entity" can be echoed back as "the entity" or "the company."

**Example 6 — mixed profile + project results:**
> User: "Summarize Acme."
> [Profile search → Acme Holdings (company); project search → Acme Series B (project, 3 profiles)]
> "I found a few matches for 'Acme':
>
> **Profiles** (subjects)
> 1. **Acme Holdings** — Corp, Delaware US, project: Acme Series B
>
> **Projects** (investments)
> 2. **Acme Series B** — 3 profiles under it (Acme Holdings, Jane Doe — CEO, John Smith — CFO)
>
> Which one?"

**Example 7 — user picks a project:**
> User: "Summarize the Acme investment." (or picks the project from Example 6's list)
> If project-summary skill is available → hand off.
> If not → "The Acme investment is a project (Acme Series B, 3 profiles). The project-summary flow isn't available right now. Want me to summarize one of the profiles instead? They are: Acme Holdings, Jane Doe, John Smith."

**Example 8 — disambiguation across profiles (Sr/Jr, duplicates, subsidiaries, common names):**
> See `references/profile-resolution.md` for the full edge-case handling.

**Example 9 — preliminary report:**
> [BG Check latest status = Preliminary]
> BG Check section opens with: `⚠ Preliminary report — not human-verified. Data may change in the final version.`
> Profile-level intro mentions: "Background check is preliminary."

**Example 10 — in-progress with older fallback:**
> [BG Check latest = In progress; previous = Reviewed (Feb 2026)]
> Use the Feb 2026 report. Alert: `⚠ The most recent background check is still in progress. This summary is from the previous report (Feb 2026).`

**Example 11 — pending consent, no fallback:**
> [BG Check latest = Pending consent, no older versions. No other products.]
> "Marcus Webb's background check is pending the subject's consent — no completed prior version exists. There's nothing to summarize yet."

**Example 12 — user asks about PDF content:**
> User: "What did the credit check say about her bankruptcy history?"
> If the credit-check PDF has been uploaded / is readable → answer from its content directly and summarize the relevant section.
> If not → "The credit check is a PDF and I don't have its content yet — only the flag counts and the link. Upload the report PDF and I'll summarize the bankruptcy section, or open it yourself: [PDF link]."
> If the user can't provide it → don't guess at the content; stop at the flag counts + link. The skill never invents PDF content.

**Example 13 — follow-up about a finding goes to a different skill:**
> Earlier: skill resolved and summarized Sarah Levin's profile.
> User (now): "Tell me more about that bankruptcy finding."
> This is no longer a summary request — it's a drill-down on a specific finding, handled by a separate skill. The shared `references/profile-resolution.md` rule about reusing an already-resolved profile applies there too, so the user doesn't have to re-identify Sarah Levin.
> Contrast: "Now summarize Marcus Webb" names a new profile → this skill fires again with fresh resolution.

**Example 14 — "all the red flags":**
> User: "I want to see all the red flags for Sarah Levin."
> Flags + findings view, scoped to red-flagged items only (omit yellow and non-flagged cards), each as a standard finding line. If there are no red flags, say so plainly. Close: "Want the yellow flags too, or the full findings?"

**Example 15 — "most important info" / "key takeaways":**
> User: "What's the most important information I should know about Sarah Levin?" — or "What are the key takeaways from this report?"
> Executive summary view — the analyst's headline read plus the red/yellow flags. No verdict or ranking beyond severity order.

**Example 16 — "do we have any risk" (factual, no verdict):**
> User: "Do we have any risk on Sarah Levin?"
> Answer with the flag gauge, factually: the red/yellow counts, and name the red flags if any — e.g. "The background check carries 2 red and 3 yellow flags; the reds are [flag], [flag]." Do **not** give a risk verdict or investment opinion (see "No opinions"). Offer to go deeper: "Want the full flags + findings?"

