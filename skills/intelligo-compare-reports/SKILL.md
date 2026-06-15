---
name: intelligo-compare-reports
description: >-
  Compare Intelligo background-check reports and report what changed or
  what overlaps. Use this skill whenever the user wants to compare, diff, or
  cross-reference Intelligo reports or profiles — including "what changed since the
  last report", "refresh comparison", "compare this profile's new and old
  report", "what's common between these two profiles", "do these subjects share
  anything", or comparing every profile in an Intelligo project against each other.
  Trigger on phrases like "compare reports", "what's new in this refresh",
  "diff these profiles", "shared connections between profiles", "what did the
  upgrade add", "compare the two report levels", and on any request that names
  two or more Intelligo profiles/reports and asks how they relate. Three modes:
  REFRESH (same profile over time, same level), LEVEL CHANGE (same profile, two
  different report levels — upgrade or interim), and CROSS-PROFILE (two or more
  distinct profiles, including a whole project). Read-only — never writes back
  to Intelligo.
---

# Compare Intelligo Reports

Compare Intelligo background-check reports and explain — in plain
language, facts only — what changed or what overlaps. Picking the right *kind* of
comparison is the first decision, so start there.

## The three modes

**Refresh — same subject, same level, different points in time.** One profile, a
newer report and an older one at the same report level. Question: *what changed
since last time?* Same person/entity and same coverage scope, so you align records
one-to-one and report **transitions** — findings newly present, findings gone,
flags escalated or cleared, new dated hits since the prior report.

**Level Change — same subject, two different report levels.** One profile, two
reports at different levels (e.g. Now → Advantage, Advantage L1 → Advantage L2/3).
This covers both **upgrades** (moving to a higher level for deeper coverage) and
**interim runs** (running a lower level to cover a time gap before the deal closes).
Question: *what did the level change add or remove — in coverage and in findings?*
Coverage scope changed, so findings can appear or disappear simply because the new
level covers more (or less) — not because the subject changed. You must separate
coverage-driven differences from genuine finding changes, and always run a coverage
diff via `compareCoverage`.

**Cross-profile — different subjects, compared as peers.** Two or more distinct
profiles (or every profile in a project). Question: *what do they share, and where
do they diverge?* No time axis — you compute **set intersection and difference**:
shared employers, addresses, associates, companies, legal entities, and what's
unique to each. Overlap is usually the signal the analyst wants (hidden or
undisclosed connections).

**Deciding which:**
- Same subject, same level → **Refresh**.
- Same subject, different levels → **Level Change** (see detection logic below).
- Different subjects → **Cross-profile**.
- A project, or "all profiles in X" → **Cross-profile**, N-way.

If genuinely ambiguous, state your inferred mode in one line and proceed — don't
stall on a question you can answer by checking whether the subject and level match.

This skill compares reports the user already has in mind or that live in a named
project. It is **not** the account-wide "who is connected to X" screening search —
that's a separate operation.

## Report scope — background checks by default

Intelligo profiles can hold several report types (background check, social media
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

Relies on the Intelligo MCP connector.

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
- **Fetching coverage diff →** `compareCoverage`, used in Level Change mode only.
  Call it with both report levels to get what coverage was added, removed, or
  changed between the two levels. Run this before fetching report content so the
  coverage picture is ready when you interpret findings.

<!-- TODO-verify on first run: exact tool names/params and the report payload
shape — status values, section names, flag representation, and the date / level /
jurisdiction fields. Call each tool once, look at the real output, then proceed.
The workflow depends only on the capabilities, not the spellings. -->


## How to identify reports when talking to the user

Every time you reference a report in a question, list, or output — use the three
things the user actually recognizes:

1. **Subject name** — the person or company name as it appears in the profile
   (e.g. "John Smith", "Acme Capital LLC"). Never substitute a profile ID.
2. **Report level** — the exact level name returned by the connector
   (e.g. "Now", "Advantage", "Advantage L2/3"). Never write "level 1" or "L2"
   unless that's literally what the connector returns.
3. **Published date** — the date the report was completed/published, not
   "latest" or "previous." Format as day-month-year (e.g. "14 Feb 2026").

Combine them like this whenever you list a report for the user to choose from or
reference one in output:

> **John Smith** — Advantage · 14 Feb 2026 · US + UK

This format applies everywhere: selection lists, confirmation dialogs, diff
headers, and any inline reference in a summary.

## Workflow

1. **Resolve inputs** via `references/profile-resolution.md` — into one profile
   (Refresh / Level Change) or several profiles / a project (Cross-profile).
2. **Select which reports** to compare — see the selection rules in each mode.
3. **Detect Level Change** — if the same profile has two reports at different
   levels, apply the Level Change detection logic before proceeding.
4. **Fetch coverage diff** (Level Change only) — call `compareCoverage` before
   fetching report content.
5. **Fetch** each report with `get_report_content`.
6. **Check status** before comparing (see Report status gate).
7. **Parse into sections** so you compare like with like. Expect areas such as:
   employment, education, legal/court records, regulatory/compliance,
   sanctions/watchlists, adverse media/news, personal background, and associated
   companies/people. Flags are red (material) and yellow (caution).
8. **Run the mode comparison** and **write the summary** (templates below). Output
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
- Three or more, unspecified → list them with subject name, level, published date,
  and jurisdiction(s) — one line per report — and ask before fetching. Use this
  exact format for each line:
  > **[Subject name]** — [Level name] · [Published date] · [Jurisdiction(s)]
  This is the one place in Refresh worth a question — the wrong baseline silently
  produces a misleading diff.

If the two reports differ in **level**, stop — this is a **Level Change** scenario,
not a Refresh. Apply the Level Change detection logic below before proceeding.

If the reports differ in **jurisdictions covered** (but same level), an apparent
"new" or "removed" finding may just be different coverage, not a real change. Note
the mismatch at the top of the output and flag coverage-driven differences as such.

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
  outcome as stated — one transition, not two findings. This includes **flag
  changes**: if a finding's flag level changed (e.g. 🟡 → 🔴, or 🔴 → cleared),
  that is a change and must be reported — it's often the most important signal
  in a refresh.
- **Removed** — in baseline, gone now (source dropped it, record corrected,
  coverage changed). Note it; lower urgency.
- **Unchanged** — don't enumerate; just confirm the section was reviewed.

**Always show the current flag** (🔴 / 🟡 / ⚪ unflagged) alongside every
finding in the output. Never omit the flag — even if the finding hasn't changed,
the flag is part of its identity.

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

### Output format

Use this structure. Drop any section that has nothing to show — don't include empty
headers. Every finding gets its own row or bullet; no prose blocks inside sections.

---

**🔄 Refresh — [Subject name]**
📅 Baseline: [date · level · jurisdiction(s)] → Current: [date · level · jurisdiction(s)]

---

**📊 Change summary**

| Category | New | Flag changed | Changed | Removed |
|---|---|---|---|---|
| Legal / Court | # | # | # | # |
| Regulatory | # | # | # | # |
| Sanctions / Watchlists | # | # | # | # |
| Adverse Media | # | # | # | # |
| Employment | # | # | # | # |
| [other sections with changes] | # | # | # | # |

_(Only include rows with at least one non-zero count. "Flag changed" counts findings
where only the flag level changed — escalated or cleared — with no other state change.
If nothing changed at all, replace the table with: "No changes found across all sections.")_

---

**🆕 New findings**
_(Present in current report, absent in baseline. Lead with red flags, then yellow.)_

🔴 **[Section]** — [finding, stated factually]
🟡 **[Section]** — [finding, stated factually]
⚪ **[Section]** — [finding with no flag]

---

**🔀 Changed**
_(Same record, moved state — including flag escalations and clearances.)_

- **[Section]** 🟡→🔴 — [finding] · [old state] → [new state] · Outcome: [as stated]
- **[Section]** 🔴→⚪ — [finding] · [old state] → [new state] · Outcome: [as stated]

_(Show the flag transition as `[old flag]→[new flag]` before the finding text when the flag changed. If the flag didn't change, show only the current flag: `🔴 **[Section]** — ...`)_

---

**🗑 Removed since baseline**
_(In baseline, gone now — lower urgency.)_

- **[Section]** — [finding]

---

**📝 What this means**
[2–3 factual sentences: counts by category, the notable transitions. No risk
verdict unless the user explicitly asks.]

---

## Mode A2 — Level Change (upgrade or interim)

### Detection

When a profile has two background-check reports at **different levels**, detect
this automatically and ask the user to confirm the intent before proceeding:

> "I can see two reports for **[Subject name]** at different levels:
> - **[Exact level name A]** — published [date] · [jurisdiction(s)]
> - **[Exact level name B]** — published [date] · [jurisdiction(s)]
>
> Was this an **upgrade** (moving to a higher level for deeper coverage) or an
> **interim run** (running a lower level to cover the time gap before the deal)?
> This affects how I frame the comparison."

Use the subject's actual name and the exact level names from the connector — never
"level 1 / level 2" or "old / new." Wait for the user's answer. Do not infer intent from the level order alone — a
lower-level report dated *after* a higher one is a strong signal for interim, but
still ask. Once confirmed, label the mode clearly in the output header.

### Coverage diff — always run it

Call `compareCoverage` with both report levels before fetching report content.
Present the coverage diff as its own section in the output, before findings.
Organize it as:

- **Coverage added** — data sources, check types, or jurisdictions present in the
  new level but not the old.
- **Coverage removed** — present in the old level but not the new (relevant for
  interim runs; rare for upgrades).
- **Coverage unchanged** — briefly confirm what was the same, so the analyst
  knows the shared baseline.

This section is factual and mechanical — list what changed, not why it matters.
The findings section below is where coverage changes get applied.

### Separating coverage-driven findings from genuine changes

A finding that appears only in the higher-level report may exist because:
1. The new level covers a source or jurisdiction the old one didn't, **or**
2. Something genuinely changed about the subject in the intervening period.

You must distinguish these. For every new finding in the higher-level report, ask:
*"Is this in a section or jurisdiction that `compareCoverage` shows was added?"*

- If yes → label it `[new coverage]`. It's a real finding, but its absence from
  the prior report means nothing about the subject's history — it was simply
  outside scope before.
- If no (same coverage scope) → treat it as a genuine change, same as Refresh
  mode. Label it `[new finding]`.
- If a finding from the lower-level report is **absent** from the higher-level
  report and the coverage is the same → label it `[removed]` and note it; may
  warrant checking.

For **interim runs** (lower level run after a higher one): the lower level will
naturally have fewer findings. Don't treat missing findings as "removed" — they're
outside the interim report's scope. Focus on what the interim period *added*:
new findings present in the lower-level report that weren't in the higher-level
baseline, within the overlapping coverage.

### Output format

Use this structure. Drop any section with nothing to show. Every item gets its own
line — no prose blocks inside sections.

---

**⬆️ Level Change — [Subject name]** · [Upgrade / Interim run]
📅 Baseline: [date · level · jurisdiction(s)] → New report: [date · level · jurisdiction(s)]

---

**📦 Coverage changes**

| | Details |
|---|---|
| ➕ Added | [source / check type / jurisdiction], [source / check type / jurisdiction] |
| ➖ Removed | [source / check type / jurisdiction] _(mainly interim runs)_ |
| ✅ Unchanged | [brief list of shared baseline checks] |

---

**📊 Findings summary**

| Category | New coverage 🆕 | Genuine new | Changed | Removed |
|---|---|---|---|---|
| Legal / Court | # | # | # | # |
| Regulatory | # | # | # | # |
| Sanctions / Watchlists | # | # | # | # |
| Adverse Media | # | # | # | # |
| Employment | # | # | # | # |
| [other sections with changes] | # | # | # | # |

---

**🆕 New findings — expanded coverage**
_(Findings that appear because the new level covers sources/jurisdictions the old one didn't.
Their absence from the prior report says nothing about the subject — they were simply out of scope.)_

🔴 **[Section]** — [finding] `· new coverage: [source/jurisdiction]`
🟡 **[Section]** — [finding] `· new coverage: [source/jurisdiction]`
⚪ **[Section]** — [finding] `· new coverage: [source/jurisdiction]`

---

**⚠️ Genuine changes** _(within overlapping coverage)_

**Added**
🔴 **[Section]** — [finding, stated factually]
🟡 **[Section]** — [finding, stated factually]

**Flag escalated / cleared**
- **[Section]** 🟡→🔴 — [finding] _(flag escalated)_
- **[Section]** 🔴→⚪ — [finding] · Outcome: [as stated] _(flag cleared)_

**Changed**
- **[Section]** — [old state] → [new state] · Outcome: [as stated]

**Removed**
- **[Section]** — [finding]

---

**📝 What this means**
[2–4 factual sentences: what the level change added in scope, count of new-coverage
findings vs genuine changes, and any notable genuine transitions. No risk verdict.]

---

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
  outcome as stated — one transition, not two findings. This includes **flag
  changes**: if a finding's flag level changed (e.g. 🟡 → 🔴, or 🔴 → cleared),
  report it — flag escalations are often the most actionable signal.
- **Removed** — in baseline, gone now (source dropped it, record corrected,
  coverage changed). Note it; lower urgency.
- **Unchanged** — don't enumerate; just confirm the section was reviewed.

**Always show the current flag** (🔴 / 🟡 / ⚪ unflagged) alongside every
finding in the output. Never omit the flag.

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

### Output format

Organize around what you found — add, drop, or rename sections based on what
actually surfaced. Every item gets its own line. No prose blocks inside sections.
Keep constant: the header, overlaps first, divergence second, summary last.

---

**🔗 Cross-profile — [Profile A] · [Profile B]** _(or: Project [name] · N profiles)_

---

**📊 Overlap summary**

| Attribute | Shared value | Profiles | Flag |
|---|---|---|---|
| Employer | [company name] | A, B | 🔴 / 🟡 / — |
| Address | [city, country] | A, C | — |
| Associate | [name] | A, B | 🟡 |
| Legal entity | [entity name] | B, C | 🔴 |
| [other attribute] | [value] | [which] | — |

_(Only include attribute types that actually surfaced. If no meaningful overlap:
"No shared employers, addresses, associates, or legal entities found.")_

---

**↔️ Notable divergence**

| Profile | Attribute | Flag | Detail |
|---|---|---|---|
| [Profile A] | [type] | 🔴/🟡/— | [unique finding] |
| [Profile B] | [type] | 🔴/🟡/— | [unique finding] |

---

**📝 What this means**
[2–3 factual sentences: what's shared and through what, where they diverge. No
strength rating or verdict.]

---

_(If internet expansion was accepted, add a clearly separated section:)_

**🌐 External leads** `[unverified — not Intelligo data]`
- [co-mention / shared filing / other web finding] · Source: [outlet/URL]
_(Treat as leads to verify, not facts.)_

---

### Optional internet expansion

After the Intelligo comparison, you may offer to extend the search to the internet
for connections the reports don't capture (co-mentions in news, shared filings).
Opt-in — ask first. If the user accepts, state plainly why this data is weaker:
it is **not human-verified** the way Intelligo content is, **and** an LLM searching
the open web is materially less accurate than Intelligo's own automated data
collection — wrong-entity matches, stale or low-quality sources, and missed
context are all likely. So mark every non-Intelligo finding **`[external data —
unverified]`**, keep it visually distinct, and treat such findings as leads to
verify, never as facts. Intelligo data is the trusted baseline; internet results
are a lead, not a conclusion.

## Guardrails

- **Structured output, always.** Every comparison result must use the mode's
  output format — headers, tables, labeled bullets, emoji status markers. Never
  return findings as a block of prose. If a section is empty, drop it entirely
  rather than writing "nothing to report here." The goal is a result the analyst
  can scan in 30 seconds, not read in 5 minutes.
- **Speak in human terms, never IDs.** Users don't recognize profile/report/
  project IDs — use them only for tool calls, never in output. Identify a subject
  by their actual name, a report by its **exact level name, published date, and
  jurisdiction(s)**, and a project by its project name.
  - ✅ "**Jane Doe** — Advantage L2/3 · 12 Mar 2026 · US + UK"
  - ❌ "profile_abc123 · report_789 · level 2"
  - ❌ "the latest report" or "the previous report" (always use the actual date)
  If two reports look identical in a list, add a distinguishing detail rather than
  falling back to an ID.
- **Facts, not opinions.** Present what the reports say and what changed or
  overlaps — never a verdict, recommendation, or risk opinion. State the concrete
  change ("status: open → closed, outcome: dismissed"), not a characterization
  ("reassuring" / "raises risk"). You may highlight Intelligo's own red/yellow flags
  (those are facts); don't add your own risk read. If the user explicitly asks for
  your read, give it separately from the factual comparison.
- **Read-only.** Never create, edit, or write anything back to Intelligo.
- **Sensitive data.** These reports hold sensitive personal data — keep it within
  the comparison, don't send it anywhere the user didn't ask, don't put it in URLs.
- **Don't invent findings.** If a section is missing, say it wasn't present rather
  than assuming it's clean.
