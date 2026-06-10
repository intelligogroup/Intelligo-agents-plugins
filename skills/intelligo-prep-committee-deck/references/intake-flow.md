# Intake Flow

Goal: learn just enough about THIS output to pick a flavor and adjust details. Default to 4 questions — scope plus three behavioral. Skip anything you can already infer from the conversation.

Use the AskUserQuestion tool when available — multiple-choice is faster than free text. For free-text follow-ups (terminology, quirks), ask inline.

Don't ask about firm type. It's a noisy proxy; behavioral questions predict format. Infer terminology (sponsor / GP / manager) from how the analyst already talks.

## Question tree

### Q0 — Scope (ask first, never skip unless obvious)

> Is this for one subject, a whole deal/project, or a deal with specific subject focus?

Options:
- Single subject (one Clarity report)
- Whole project / deal rollup (every subject in the project)
- Project rollup + deep dive on specific subjects

Why this matters: scope changes everything downstream — the data fetched, the template, the snippet patterns.

Follow-up if "project rollup + deep dive": ask which subjects to expand. If the project has only 2–4 subjects, offer to deep-dive all of them.

### Q0.5 — Examples (optional, offer right after scope)

> *Optional but useful:* do you have an example of what your IC pack usually looks like? A screenshot of your standard slide, a previous IC deck, or a sample memo — anything that shows your usual style and structure. I can mirror it and skip most of the questions below.

Three valid inputs:
- A screenshot (PNG / JPG) — Read the image, infer layout, headings, length, terminology.
- A file attachment (.pptx / .docx / .pdf / .md) — Read it, parse structure and tone.
- A short verbal description — "we use a one-page memo with a header, three bullets, and a sources footer."

When the user provides one:

1. Read it carefully. Note: structure (sections, headings), length, tone (terse vs. narrative), terminology (sponsor / GP / manager), what gets emphasized (severity first? disclosure first?), what gets omitted (no methodology section? no sources?).
2. Short-circuit the behavioral questions (Q1–Q3) where the example clearly answers them. Don't re-ask things you can infer.
3. Confirm what you inferred in one short message: "I'll match your style — one-pager, lead with severity summary, you call them 'sponsors', no methodology section. Confirm or correct?" Then proceed.
4. Note any open questions the example didn't answer and ask only those.

If the user doesn't have an example, that's fine — move on to Q1.

**Why offer this early:** an example is the highest-bandwidth way for the user to tell you what they want. One screenshot can replace four multiple-choice questions and produce a closer-fitting result.

### Q1 — Audience inside the IC

> Who reads this first?

Options:
- Investment partners / decision-makers
- Risk / compliance / GC
- Board / non-technical committee
- Mixed audience

Why: partners want narrative + headline; risk wants flag detail with sources; board wants plain language and no jargon. This is the single best predictor of tone and depth.

### Q2 — Format the IC consumes

> What format does this output need to fit into?

Options:
- Slide-ready snippets to paste into the IC deck
- Word memo (drop into a section of existing memo)
- One-pager / tear sheet (standalone)
- Polished PDF / standalone document

Why: drives the output mode. "Slide-ready snippets" produces the styled HTML the analyst copies block-by-block into PowerPoint or Google Slides. The others produce different files.

### Q3 — What this output should lead with

> What should the IC read in the first 10 seconds?

Options:
- Highest-severity flag + finding (the most severe flag and what was actually found behind it)
- All red and yellow flags upfront (every material flag listed with finding text)
- Disclosure delta first (what subject said vs. what we found)
- Narrative story (chronological / biographical context)

Why: this is the actual stylistic decision. A risk team picks all red/yellow upfront; a board picks the highest-severity flag; some firms pick disclosure delta. Note this question is about *which finding leads*, not *what verdict to assign* — the skill never assigns verdicts (see SKILL.md).

### Q4 — External enrichment (optional, ask before generating)

> Want me to pull in anything from outside Clarity for this output? Pick any that fit:

Options (multi-select):
- **Recent news** — pull current news / press coverage on the subject from web search. Adds a "Recent news" snippet with date-bounded items, sourced.
- **Public filings** — pull recent SEC filings, regulatory actions, or court records dated after the last Clarity refresh.
- **Internal context (CRM / docs)** — pull deal notes, prior IC discussion, or relationship history from a connected CRM or knowledge tool (Salesforce, HubSpot, Notion, Confluence, etc.).
- **Industry / peer context** — pull research on the subject's firm, sector, or peer GPs / sponsors from external sources.
- **None — Clarity only.**

This question is specifically about **non-Clarity** sources. Clarity-internal enrichment (comparing against a prior Clarity report for refresh-delta, or computing patterns across other subjects in the same project) is handled automatically in Step 3 of the core flow — the analyst doesn't need to ask for it.

How to handle each:

1. **Before offering**, probe what's actually available in this session. Web search loaded? CRM MCP connected? Public-filings connector? Hide options that can't be fulfilled — don't offer something you can't deliver.
2. **When the user picks one or more**, pull the data and integrate it into the output as clearly-labeled snippets:
   - Recent news → "Recent news" snippet, each item with date + source.
   - Public filings → "Recent filings" snippet, each entry sourced.
   - Internal context → "Internal context" snippet, attributed to the source system (e.g. "From Salesforce: opportunity notes, last updated Nov 10").
   - Industry / peer context → "Industry context" snippet.
3. **Note in the output footer** what was pulled in. The IC should know whether the snippets are Clarity-only or enriched. Example footer: *"Enriched with: 2 web news items (Nov 1–18, 2025) · 1 SEC filing (Oct 28, 2025) · CRM notes from Salesforce."*

If the user says "Clarity only," skip this step entirely and generate from Clarity data alone.

## Optional follow-ups (ask only if relevant)

- **Depth:** "Executive only (1–2 paragraphs), standard IC summary, or full review with everything?" Default to standard. Only ask if Q1 was "Mixed" or unclear.
- **Terminology:** Don't ask if you can infer from the conversation. If the analyst used "sponsor" or "GP" or "manager" or "counterparty", use that word everywhere. Only ask explicitly if you have no signal: *"What does your firm call the subject — sponsor, manager, GP, counterparty, target?"*
- **Style constraints:** *"Anything your IC specifically does or does not want to see? (e.g., 'never include social media findings', 'always show coverage scope')"* Ask only if the user has hinted at quirks.
- **Profile save:** At the end of intake, offer: *"Want me to remember this profile for the next subject in this session? Give it a short name."* This is the highest-leverage follow-up — most analysts reuse the same format for every IC subject in a deal.

## Skipping questions

If you can infer an answer from prior conversation, MCP data, or obvious context, skip the question. Examples:

- The user said "summarize the Acme deal for IC" → Q0 = project rollup (or hybrid if they name people too).
- The user said "write up the CEO background for IC" → Q0 = single subject.
- The user said "give me slides for our IC" → skip Q2, output is slide-ready snippets.
- The user said "I just need to know if this is a problem" → skip Q3, lead-with = top-line judgement.
- The user uploaded their last IC memo as a template → skip Q2 and Q3, mimic the structure.
- The user has already used the skill earlier in the session with a saved profile → skip everything except scope.

## A note on minimum viable intake

The skill should feel light. If the analyst types "summarize the Acme deal for the partner meeting Thursday, slide-ready", you have:
- Scope: project (and probably hybrid if they name a specific subject)
- Audience: investment partners
- Format: slide-ready
- Lead-with: not specified — default to top-line judgement

Don't ask them four questions just to confirm. Ask zero. Generate. Show preview. Adjust if they push back. The fewer questions, the better the experience.

## Edge cases

- **Analyst says "just give me something, you decide":** pick the most common combination (partners audience + top-line lead + standard depth + snippets), generate, and offer to adjust after they see it.
- **Analyst gives conflicting signals** (e.g. "for the board, full risk detail"): ask the one question that resolves the conflict — usually depth, since audience and lead-with rarely conflict.
- **No MCP data available:** never ask for a Clarity report ID or project ID — analysts don't know those. Offer instead: (a) paste Clarity content as text, (b) attach a PDF export of the report, or (c) describe findings from memory (only viable for top-line / executive flavors). Then proceed with intake as normal. See SKILL.md "When Clarity MCP isn't available" for the full handling.

- **MCP available but the analyst doesn't remember exact names:** search Clarity using whatever they remember — partial name, approximate date, deal context, GP name, fund vehicle. Show short lists with enough context (names, dates, roles, deal) for the analyst to recognize the right one. Never display internal IDs in the picker.
