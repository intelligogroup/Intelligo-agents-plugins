---
name: compare-clarity-reports
description: >-
  Compare Intelligo Clarity background-check reports and report what changed or
  what overlaps. Use this skill whenever the user wants to compare, diff, or
  cross-reference Clarity reports or profiles — including "what changed since the
  last report", "refresh comparison", "compare this profile's new and old
  report", "what's common between these two profiles", "do these subjects share
  anything", or comparing every profile in a Clarity project against each other.
  Trigger on phrases like "compare reports", "what's new in this refresh",
  "diff these profiles", "shared connections between profiles", and on any
  request that names two or more Clarity profiles/reports and asks how they
  relate. Two modes: REFRESH (same profile over time) and CROSS-PROFILE (two or
  more distinct profiles, including a whole project). Read-only — never writes
  back to Clarity.
---

# Compare Clarity Reports

Compare Intelligo Clarity background-check reports and explain — in plain
language, facts only — what changed or what overlaps. Picking the right *kind* of
comparison is the first decision, so start there.

## The two modes

**Refresh — same subject, different points in time.** One profile, a newer report
and an older one. Question: *what changed since last time?* Same person/entity, so
you align records one-to-one and report **transitions** — findings newly present,
findings gone, flags escalated or cleared, new dated hits since the prior report.

**Cross-profile — different subjects, compared as peers.** Two or more distinct
profiles (or every profile in a project). Question: *what do they share, and where
do they diverge?* No time axis — you compute **set intersection and difference**:
shared employers, addresses, associates, companies, legal entities, and what's
unique to each. Overlap is usually the signal the analyst wants (hidden or
undisclosed connections).

**Deciding which:** same subject across both reports → Refresh. Different subjects
→ Cross-profile. A project, or "all profiles in X" → Cross-profile, N-way (a
project is just the input set; the 2-profile logic scales). If it's genuinely
ambiguous, state your inferred mode in one line and proceed — don't stall on a
question you can answer by checking whether the subject matches.

This skill compares reports the user already has in mind or that live in a named
project. It is **not** the account-wide "who is connected to X" screening search —
that's a separate operation.

## Report scope — background checks by default

Clarity profiles can hold several report types (background check, social media
analysis, credit check, others). **Compare background-check reports by default**;
when a profile or project has more than one type, pick the background check
without asking.

If the user explicitly asks for another type, don't silently ignore it and don't
refuse: tell them other types exist and that this skill is built around background
checks, then default to background checks unless they confirm they want the other
type — so they stay aware of what's being compared.

**Social media and credit reports are PDFs**, not structured data, so you can only
compare them if you can actually read the PDF content. If it isn't available, ask
the user to upload it (both for a refresh, all of them for a cross-comparison). If
you still can't read it, **stop — don't guess from a filename or metadata and
don't fabricate.** A missing PDF is a hard stop. Once you have the content, the
mode logic and facts-only output below apply unchanged.

## Tools

Relies on the Clarity MCP connector.

- **Resolving who/what the user means →** don't do your own lookup. Follow
  `references/profile-resolution.md`. It handles searching profiles and projects
  in parallel, the case where **one name matches both a profile and a project**,
  reusing a subject already resolved earlier in the conversation, disambiguating
  duplicates, and the never-silently-combine rule. It uses `get_profiles`,
  `get_projects`, and `get_profile`.
- **Fetching a report →** `get_report_content`, one call per report (the heavy
  call). The resolved profile/project objects tell you a profile's available
  reports and a project's members — rely on what the connector returns, never
  invent fields.

<!-- TODO-verify on first run: exact tool names/params and the report payload
shape — status values, section names, flag representation, and the date / level /
jurisdiction fields. Call each tool once, look at the real output, then proceed.
The workflow depends only on the capabilities, not the spellings. -->

## Workflow

1. **Resolve inputs** via `references/profile-resolution.md` — into one profile
   (Refresh) or several profiles / a project (Cross-profile).
2. **Select which reports** to compare — see the selection rules in each mode.
3. **Fetch** each report with `get_report_content`.
4. **Check status** before comparing (see Report status gate).
5. **Parse into sections** so you compare like with like. Expect areas such as:
   employment, education, legal/court records, regulatory/compliance,
   sanctions/watchlists, adverse media/news, personal background, and associated
   companies/people. Flags are red (material) and yellow (caution).
6. **Run the mode comparison** and **write the summary** (templates below). Output
   is a structured chat summary — no file unless asked.

## Report status gate (both modes)

A report is only safe to compare once it's final. Check every report's status
first:

- **In progress / pending submission** → **stop.** Not ready; a comparison would
  be meaningless. Say which report isn't ready.
- **Preliminary** → **get explicit user approval first.** Explain that a
  preliminary report may differ from the final and can carry unverified content
  that produces a **false positive**. If approved, label every preliminary-sourced
  finding `(preliminary — unverified)` and repeat the caveat in the summary.
- **Final / complete** → proceed.

## Mode A — Refresh (what changed)

### Which two reports

A profile can have **more than two** reports — don't assume "latest vs the one
before."

- Exactly two → newer = current, older = baseline.
- Three or more, user named which two → use those.
- Three or more, unspecified → list them with **date, level, and jurisdiction(s)**
  and ask before fetching. This is the one place in Refresh worth a question — the
  wrong baseline silently produces a misleading diff.

If the two reports differ in **level** (e.g. standard vs enhanced) or
**jurisdictions covered**, an apparent "new" or "removed" finding may just be
different coverage, not a real change. Note the mismatch at the top of the output
and flag coverage-driven differences as such, not as transitions.

### Judge meaning, not wording

A useful diff is about what changed *substantively*, not which words moved. Don't
flag rewordings; don't miss a real shift hidden behind similar wording. Match
records by a stable identifier (case number, employer, license, article) rather
than by position, then for each candidate change ask what it *means*:

- **A status resolved** — a legal case open → closed, a regulatory action
  resolved, a sanction lifted. Capture the outcome as stated (dismissed,
  acquitted, convicted, settled).
- **New substance on a rolling matter** — for things that develop over time (an
  investigation, ongoing litigation, an evolving story), the test isn't "is the
  text different" but "is there new substance on the same item."
- **Genuinely new details** — a new party, amount, role, or date on an item that
  already existed. New substance is worth surfacing; cosmetic restatement isn't.

### Classify each change

- **New** — present now, absent in baseline. Most important, especially new
  red/yellow flags and new legal/regulatory/sanctions hits.
- **Changed** — same record, moved state. Report as `[old state] → [new state]`,
  outcome as stated — one transition, not two findings.
- **Removed** — in baseline, gone now (source dropped it, record corrected,
  coverage changed). Note it; lower urgency.
- **Unchanged** — don't enumerate; just confirm the section was reviewed.

Lead with what's material. A refresh where nothing changed is a valid, valuable
answer — say so plainly rather than padding.

### News / adverse media — match on the event, not the article

A refresh almost always pulls in new articles, so news needs the legal lens: is
each new article a **genuinely new event**, or **another copy of one already in
the baseline?**

- New event → surface it like any new finding.
- Same event, different source → not a change by default. Surface it only if it
  **adds substance** (new facts, party, outcome, amount, correction — note as new
  detail on the existing event) or the **source itself carries weight** (coverage
  moving from an obscure blog to a major outlet can change prominence/credibility:
  "same event, now also reported by [outlet]"). Otherwise it's a duplicate — omit.

Group news by underlying event — "one event, N sources," not N findings. Signal,
not length.

### Output (a guide — adapt to what surfaced; drop empty blocks)

```
# Refresh comparison — [Subject name]
Baseline: [date, level, jurisdiction(s)]  →  Current: [date, level, jurisdiction(s)]

## What's new
- [section] [red/yellow flag if labeled]: [finding, stated factually]

## Changed
- [section]: [old state] → [new state], outcome: [as stated]

## Removed since baseline
- [section]: [finding]

## Summary of changes
[1–3 sentences, factual: what changed, e.g. counts by category and the notable
transitions. No verdict on whether risk rose or fell.]
```

## Mode B — Cross-profile (overlap and divergence)

### Which reports, and how many profiles

Use each profile's **most recent** report by default (no need to ask unless the
user names a specific one). When the input is a project:

- **Up to 12 profiles** → list them by name and ask whether to compare all or a
  subset; comparing all is fine, but let the user choose.
- **More than 12** → don't auto-compare. List the profiles and ask which to
  compare before fetching — an N-way comparison across many profiles is expensive
  and hard to read.
- **Very large (≈300+)** → show only the **30 most recent**, say how many total
  ("showing 30 of 312"), and let the user pick or name others. Don't dump the
  whole list.

### Compute overlap and divergence

Treat the profiles as peers: for each attribute type, take the intersection across
profiles and the per-profile remainder. The strongest connection signals: shared
employers/companies, addresses, associated people, overlapping legal entities or
case parties, shared directorships. Surface softer overlaps (same city, same
education) but rank them lower.

For a project (N profiles), report each overlap as "shared by [which profiles]" so
the analyst sees *who* is connected through *what*. Highlight overlaps involving a
red/yellow-flagged entity (the flag is the report's, a fact) so they're easy to
spot.

### Output (a guide, not a fixed form)

You can't predict what surfaces — employers and addresses one time, litigation and
directorships the next, or almost nothing. Organize around what you found: add,
drop, merge, or rename sections; group by the attribute types that actually came
up. Don't pad a thin result to fill the template or cram a rich one into three
headings. Keep constant: a header naming the profiles/project compared; overlaps
first (what's shared + which profiles + any flag); notable divergence where
useful; a short factual closing summary.

```
# Cross-profile comparison — [Profile A], [Profile B]  (or: Project [name], N profiles compared)

## Shared / overlapping
- [attribute type]: [shared value] — shared by [which profiles] [flag if any]
  (use as many groupings as the findings call for)

## Notable divergence
- [Profile]: [material attribute unique to them]

## Summary of overlap
[1–3 sentences, factual: what's shared and through what, where they diverge. No
strength rating or verdict.]
```

If there's no meaningful overlap, say so directly — "no shared employers,
addresses, associates, or legal entities found" is a clean, useful result.

### Optional internet expansion

After the Clarity comparison, you may offer to extend the search to the internet
for connections the reports don't capture (co-mentions in news, shared filings).
Opt-in — ask first. If the user accepts, state plainly why this data is weaker:
it is **not human-verified** the way Clarity content is, **and** an LLM searching
the open web is materially less accurate than Clarity's own automated data
collection — wrong-entity matches, stale or low-quality sources, and missed
context are all likely. So mark every non-Clarity finding **`[external data —
unverified]`**, keep it visually distinct, and treat such findings as leads to
verify, never as facts. Clarity data is the trusted baseline; internet results
are a lead, not a conclusion.

## Guardrails

- **Speak in human terms, never IDs.** Users don't recognize profile/report/
  project IDs — use them only for tool calls, never in output. Identify by name,
  and a report by its **date, level, and jurisdiction(s)** ("Jane Doe — enhanced
  check, US + UK, 12 Mar 2026"); a project by name. If two reports look identical
  in a list, add a distinguishing detail rather than an ID.
- **Facts, not opinions.** Present what the reports say and what changed or
  overlaps — never a verdict, recommendation, or risk opinion. State the concrete
  change ("status: open → closed, outcome: dismissed"), not a characterization
  ("reassuring" / "raises risk"). You may highlight Clarity's own red/yellow flags
  (those are facts); don't add your own risk read. If the user explicitly asks for
  your read, give it separately from the factual comparison.
- **Read-only.** Never create, edit, or write anything back to Clarity.
- **Sensitive data.** These reports hold sensitive personal data — keep it within
  the comparison, don't send it anywhere the user didn't ask, don't put it in URLs.
- **Don't invent findings.** If a section is missing, say it wasn't present rather
  than assuming it's clean.
