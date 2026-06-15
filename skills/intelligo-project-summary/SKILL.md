---
name: intelligo-project-summary
description: >-
  Deal/project-level summary across every profile in an Intelligo project — a synthesized
  project executive summary plus a short risk summary per subject (mini exec summary + red/yellow
  flags). Summarizes a whole investment (a project with multiple profiles), not a single subject; if
  the query is ambiguous it searches projects and profiles and hands a single profile off to the
  profile-summary skill. Can return the whole summary or just one part on request — the subject
  roster, the project overview, or the per-subject risk summaries. Triggers: "summarize the X
  project/investment/deal", "roll up X", "risk across the X deal", "red flags across X", "what did we
  find on the X investment", "what should I know about the X deal", "who's in the X deal", "list the
  subjects/companies in X", "the gist of the X deal", "break the X deal down by subject". Do NOT use
  for a single person/company (that's profile-summary), web research, monitoring, action items, or
  comparisons.
---

# Intelligo Project Summary

Turn an Intelligo **project** (an investment holding multiple subjects) into a deal-level summary the user can read quickly: a short synthesized project overview, then a per-subject risk summary.

This skill is the project-level counterpart to **intelligo-profile-summary**. It reuses that skill's report selection and per-profile rendering, then composes the results into a deal-level view. Read profile-summary's SKILL.md alongside this one — the per-subject logic lives there and is not duplicated here.

## Data model (overview)

Hierarchy: `Project → Profile → Report → Card → Flag`. A **Project** is the investment (the deal). It holds one or more **Profiles** (the DD subjects — persons and/or companies). Everything below the Profile level (Reports, Cards, Flags, statuses, formats, PDF handling) is exactly as defined in **intelligo-profile-summary** — this skill does not redefine it. What it adds on top is project resolution, full-roster enumeration, scale handling, and roll-up composition (Steps 1–5).

### In/out of scope (inherited from profile-summary)

- **In scope:** the Project (for ID), every Profile under it, each profile's DD reports (most recent per product), their cards, flags, and linked notes.
- **Out of scope:** Monitoring, all Action items, Comments — same exclusions as profile-summary.
- **No opinions:** no investment recommendations, no risk verdicts, no "this is the deal-breaker" / ranking which subject matters most. Severity ordering (red → yellow) and "this subject carries flags, this one is clean" are the only allowed prioritization signals. The skill reports what was flagged; it does not advise whether to do the deal.

## Connector tools

Same connector as profile-summary: `Get_projects`, `Get_profiles`, `Get_report_content`. This skill leans on `Get_projects` for resolution and the **full project roster**, then drops into the profile-summary flow per subject.

### `Get_projects` — resolve a project name; returns project detail + full profile roster

Given a query (project/deal name, partial name, or company that maps to a deal), return matching project candidates. Each candidate carries:

- Enough identifying metadata to disambiguate one project from another with the same or similar name — e.g. project name, an internal id/code if present, created date, and the count of profiles under it. The skill surfaces these when more than one project matches (see Step 1).
- The project's **full profile list** — every subject attached to the project (id, name, person/company type, and the minimum identifying fields), not just a preview. This is what the roll-up iterates. (The profile-summary skill only uses the short preview; this skill requires the full list.)

> **Connector dependency:** this skill assumes `Get_projects` can return the complete profile roster for a project. If only a preview is returned, the skill cannot guarantee completeness — in that case, render what's available, and state plainly that the roster may be incomplete.

### `Get_profiles` and `Get_report_content`

Used per subject, exactly as in profile-summary: `Get_profiles` resolves any single subject and returns its report list (already available from the project roster where the connector includes report metadata); `Get_report_content` fetches one report's content (cards + flags merged). Fetch reports in parallel across subjects and products wherever possible.

### Behavior if a tool is missing or returns nothing

- `Get_projects` unavailable → can't resolve or enumerate a project; tell the user and stop (or offer to summarize a single named profile via profile-summary instead).
- `Get_projects` returns a project but an empty roster → tell the user the project has no profiles attached; nothing to summarize.
- `Get_report_content` unavailable/empty for a given subject → note that subject as "report content unavailable" in the roll-up and continue with the others; never fabricate.

Never invent content the connector didn't return.

## Step 1 — Resolve to a Project (disambiguate first)

The resolution logic is embedded below so this skill is self-contained.

### Hard rules

- **Never invent fields.** Only surface what the connector returned.
- **Disambiguate before summarizing.** When more than one project (or a project and profiles) match, ask the user which one — don't pick silently.
- **Resolution only decides *which* project.** What to do with it is Steps 2–5.

### Step 1a — Check if a project is already in context

Before searching, check the conversation. If an earlier turn already resolved this project (a prior `Get_projects` call + user selection), and the current message is a follow-up that doesn't name a new deal or subject ("now the flagged ones", "go deeper on the parent company", "what about the credit checks") → **reuse the already-resolved project.** Skip the rest of Step 1. This avoids forcing the user to re-identify the deal on every follow-up.

If the user names a different deal/subject or asks to start over, do fresh resolution.

### Step 1b — Search projects AND profiles in parallel

Users don't always know whether they mean a deal or a single subject. **Call `Get_projects` and `Get_profiles` in parallel** with the user's query. The user asked for a deal, but their term might also name a company that *is* a subject.

This skill's resolution priority is the **project**:

1. **Exactly one project matches** → use it. Proceed to Step 2.
2. **More than one project shares the name** → **always disambiguate.** Present the matching projects with enough to tell them apart (project name, an internal id/code if present, subject count, created date / vintage), and ask which one:

   > "More than one project matches 'Acme':
   > 1. **Acme Series B** — 4 subjects, created Jan 2026
   > 2. **Acme Growth Round** — 2 subjects, created Aug 2025
   > Which one?"

3. **A project and one-or-more profiles match** → show one unified list, labeled by type, and let the user pick by number or description:

   > "I found a few matches for 'Acme':
   >
   > **Projects** (investments)
   > 1. **Acme Series B** — 3 subjects (Acme Holdings, Jane Doe — CEO, John Smith — CFO)
   >
   > **Profiles** (subjects)
   > 2. **Acme Holdings Inc** — Corp, Delaware US, project: Acme Series B
   >
   > Which one?"

   If the user picks a single profile, **hand off to intelligo-profile-summary**.
4. **User phrasing pre-disambiguates** → skip the mixed list. "The Acme **deal/investment/project**" → only show project matches; "the **company/person/subject** Acme" → that's a profile request, hand to profile-summary.
5. **No project match, only a single profile** → not a project request; hand off to intelligo-profile-summary.
6. **No match at all** → say so plainly; ask for an identifying detail (deal name, lead company, jurisdiction, vintage). Don't guess.

## Step 2 — Enumerate the full roster

From the resolved project, take the **full profile list** `Get_projects` returned. For each subject capture: profile id, name, person/company type, and the minimum identifying fields. This roster drives both the scale decision (Step 3) and the composition (Step 5).

Count the subjects — that count selects the scale path.

## Step 3 — Scale handling

The output adapts to roster size so a large deal stays readable. In all cases, **lead with the subjects that carry flags**; clean subjects are acknowledged, never silently dropped.

| Roster size | Behavior |
|---|---|
| **1–5 subjects** | Summarize every subject. Flagged subjects in full risk-summary form; clean subjects get a one-line "no flags" entry. |
| **6–20 subjects** | Render the risk summary in full for every **flagged** subject. Collapse the **clean** subjects into a single line listing their names (e.g. "No flags: Jane Doe, John Smith, Acme Asia Pte Ltd"). Note the clean count in the project exec summary. |
| **More than 20 subjects** | Do **not** auto-render Part B for all. Give Part A in full (the Subjects index already lists everyone with their flag counts, plus the narrative), then ask how the user wants to proceed — e.g. "20+ subjects in this deal. Want the full risk summary for just the flagged ones, a specific subset, or all of them?" Render Part B details only after they choose. |

If the user explicitly overrides ("give me all of them", "just the flagged ones", "only Jane Doe and the parent company") → honor it regardless of roster size.

## Step 4 — Per subject: select reports and fetch content

For **each subject to be rendered** (per the Step 3 path), run the **profile-summary report-selection logic** unchanged:

1. Filter out monitoring entries.
2. Group remaining reports by product type (Background Check, Credit Check, Social Media Analysis).
3. Per product, pick the right report with the **status-aware rules** (Ready/Reviewed → use; Preliminary → use + caveat; In progress / Pending consent → fall back to an older Ready/Reviewed with a caveat, else skip + note).
4. Call `Get_report_content` per selected report (parallelize across subjects and products).

Status caveats from profile-summary apply per subject and surface in that subject's block (see Output).

## Step 5 — Compose the project summary

The summary is built from **three independent components**. Deliver exactly what the user's request calls for — one, some, or all — combining them in a single response when the request spans several. Default to all three for a plain "summarize the deal." Don't ask which when the phrasing already picks; only ask if the request is genuinely ambiguous about scope.

| Component | What it gives | Triggered by |
|---|---|---|
| **A1 · Subjects index** | The full-roster table (see Part A1). | "who's in the deal", "list the subjects", "the roster", "which companies/people are in X", "how many flags on each" |
| **A2 · Project overview** | The narrative roll-up (see Part A2). | "the gist", "tl;dr", "what should I know about the deal", "high-level read", "headline" |
| **B · Per-subject risk summaries** | Exec text + flags per subject (see Part B). | "break it down by subject", "summary of each one", "the per-subject detail", "risk on each subject" |

- **Plain "summarize / roll up the X deal", "everything", "full picture"** → all three, in order A1 → A2 → B. No picker.
- **A narrower ask** → deliver only that component (e.g. "who's in the Acme deal" → A1 alone; "what's the gist of the deal" → A2, with A1 if it aids the read).
- **Several named** → combine those, canonical order.
- **A single subject named within the project** → not this skill's job; hand off to intelligo-profile-summary.
- After delivering a subset, close by offering the components not yet shown (e.g. after A1 + A2 → "Want the per-subject risk summaries too?").

### Part A — Project executive summary (synthesized)

There is no analyst-written project-level summary in Intelligo, so synthesize one from the subjects' reports and flags. It should let an analyst grasp the whole deal at a glance, in two components:

**1. Subjects index** — a **table** covering the **full roster** regardless of size (columns and rendering in "Output format"). This is the at-a-glance roster; the deeper text + flags per subject come in Part B (for large rosters, Part B follows the Step 3 scale path, but the index still lists everyone).

**2. Narrative summary** — a few factual sentences on what's important to know about the project:

- Composition: how many subjects, how many carry flags vs. are clean.
- Aggregate flag gauge across the deal: total red / total yellow.
- The cross-cutting themes actually present in the flags (e.g. "litigation on two subjects, an AML hit on one, adverse media on one") — derived from flag content, not invented categories.
- Any deal-wide caveats (e.g. "two subjects' background checks are still in progress; summaries below use prior reports").

States facts, not verdicts: no ranking of which subject matters most, no recommendation. Severity and flagged-vs-clean are the only signals.

### Part B — Per-subject risk summary

For each rendered subject, produce a **short risk summary** = a 2–3 sentence exec summary + that subject's red/yellow flags. This is the profile-summary **Executive summary view**, applied per subject:

- Per product on the subject: the analyst exec-summary text if present (verbatim / light edit), else a synthesized 2–3 sentence overview from its cards and flags; PDF products summarized from the document if available, else flag counts + link.
- Followed by the subject's flags as finding lines: `🔴 RED · [flag name] — [flag description]` / `🟡 YELLOW · [flag name] — [flag description]`. Icon color must match severity.
- Subject's status caveats (`⚠`) render at the top of its block.
- Non-flagged, non-material cards are omitted (this is the exec-level lens, not the full findings list).

Use profile-summary's finding-line format, ordering (red → yellow), and findings filter verbatim. Do not re-derive them.

### Going deeper

The default deliverable stops at the exec level. Close with a one-line offer to drill down via profile-summary on a specific subject:

> "Want the full flags + findings, or a per-tab breakdown, for any subject? (I can go deep on, e.g., Acme Holdings.)"

When the user picks a subject, hand that subject off to **intelligo-profile-summary** — the shared resolution rule means they don't need to re-identify it.

## Output format

The output must be **structured and scannable** — never a wall of text. Use headers, a table for the roster, and short bulleted lines. Reserve prose for the one short Overview paragraph; everything else is structured.

Formatting rules:

- **Header** — project name as an H2, with a one-line stat strip beneath it.
- **Deal-wide alerts** — each `⚠` on its own line, directly under the header.
- **A1 Subjects index** — render as a **markdown table**, one row per subject. Columns: Subject · Type · Report levels · Jurisdiction · Flags. The Flags cell uses `🔴 2 / 🟡 1` or `clean`. A table is far easier to scan than stacked lines.
- **A2 Overview** — one short paragraph (2–4 sentences), under an "Overview" header. This is the only prose block; keep it tight.
- **B Per-subject summaries** — one block per subject, each opening with an H3 header (name + ID line). Within a block: optional `⚠` caveat line, 1–3 sentence exec text, then a **Flags** list (one bullet per flag). Separate subjects with a horizontal rule (`---`) so blocks don't run together.
- **Collapsed clean subjects** (6–20 rosters) — a single labeled line, not a block.
- **Close** — a one-line offer on its own line.

### Skeleton

```
## [Project name]
**N subjects · 🔴 X red / 🟡 Y yellow · Z flagged subjects** · [vintage if useful]

⚠ [Deal-wide alert line — only if applicable.]

### Subjects
| Subject | Type | Report levels | Jurisdiction | Flags |
|---|---|---|---|---|
| Acme Holdings | Company | BG: A3 L3, Credit | Delaware US | 🔴 2 |
| Jane Doe — CEO | Person | BG | UK | 🟡 1 |
| John Smith — CFO | Person | BG | UK | clean |

### Overview
[2–4 sentence narrative: composition, aggregate gauge, cross-cutting themes, deal-wide caveats.]

---

### Acme Holdings — Company · Delaware US
⚠ [subject caveat, if any]
[1–3 sentence exec text.]

**Flags**
- 🔴 RED · [flag name] — [flag description]
- 🟡 YELLOW · [flag name] — [flag description]

---

### Jane Doe — CEO @ Acme · UK
[1–3 sentence exec text.]

**Flags**
- 🟡 YELLOW · [flag name] — [flag description]

---

**No flags:** John Smith — CFO   ← collapsed clean subjects (6–20 rosters)

---
Want the full flags + findings, or a per-tab breakdown, for any subject?
```

When only one component was requested (Step 5), render just that piece with its own header — e.g. an A1-only response is the header + the Subjects table + the close.

Length is short by default but not capped — extend a subject's block when its content is genuinely substantial.

## Examples

**Example 1 — straightforward small deal:**
> User: "Summarize the Acme Series B project."
> [One project match → roster of 3 subjects: Acme Holdings (2 red), Jane Doe — CEO (1 yellow), John Smith — CFO (clean).]
> Project header, then the **Subjects index** as a table (rows: Acme Holdings · Company · BG: A3 L3, Credit · Delaware US · 🔴 2; Jane Doe — CEO · Person · BG · UK · 🟡 1; John Smith — CFO · Person · BG · UK · clean), then a 3-sentence **Overview** ("3 subjects; 2 carry flags; 2 red total on the parent company — litigation and an AML hit — plus a yellow on the CEO; the CFO is clean."). Then per-subject blocks: Acme Holdings and Jane Doe in full, John Smith collapsed to a one-line "no flags." Close with the go-deeper offer.

**Example 2 — name shared by two projects (disambiguate first):**
> User: "Roll up the Acme deal."
> [Two project matches.] "More than one project matches 'Acme': 1. Acme Series B — 4 subjects, Jan 2026 · 2. Acme Growth Round — 2 subjects, Aug 2025. Which one?" → proceed once the user picks.

**Example 3 — medium roster (6–20), collapse clean:**
> User: "What should I know about the Meridian Fund II investment?"
> [Roster of 11 subjects; 3 flagged, 8 clean.]
> Overview notes 11 subjects, 3 flagged, 8 clean, aggregate gauge and themes. Full risk summaries for the 3 flagged subjects. Clean subjects collapsed: "**No flags:** [8 names]." Go-deeper offer.

**Example 4 — large roster (>20), ask before rendering:**
> User: "Summarize the Horizon Platform rollup."
> [Roster of 27 subjects.]
> Render Part A in full — the Subjects index lists all 27 (name · report levels · jurisdiction · flag count) plus the narrative — then ask: "27 subjects here; 6 carry flags. Rendering every risk summary in full would be long. Want the full write-up for just the flagged subjects, a specific subset, or everything?" Render Part B after they choose.

**Example 5 — user picked a single profile from a mixed list:**
> User: "Summarize Acme." → [project Acme Series B + profile Acme Holdings both match] → user picks Acme Holdings (the company).
> Hand off to intelligo-profile-summary; this skill does not fire.

**Example 6 — deal-wide caveat:**
> [Two subjects' background checks are In progress with prior Reviewed reports; one subject's is Preliminary.]
> Overview includes: "⚠ Two subjects' background checks are still in progress — those summaries use the prior reports; one subject's report is preliminary." Each affected subject's block repeats its own caveat.

**Example 7 — drill down after the roll-up:**
> Earlier: skill summarized the Acme Series B project.
> User (now): "Give me the full findings on Acme Holdings."
> Hand off to intelligo-profile-summary (Flags + findings view) for that subject — already resolved, no re-identification needed.

**Example 8 — empty or report-less project:**
> [Project resolves but roster is empty, or every subject has only monitoring / no summarizable reports.]
> Say plainly what exists: "The Acme Series B project has 3 subjects but none have a completed due-diligence report to summarize yet (2 pending consent, 1 monitoring-only)." No fabrication.

**Example 9 — single product across the deal:**
> User: "Just the background checks across the Acme deal."
> Apply the per-subject selection to the Background Check product only; the overview and per-subject blocks cover BG checks alone.

**Example 10 — partial request (one component only):**
> User A: "Who's in the Acme Series B deal?" → deliver **A1 (Subjects index)** alone, then offer: "Want the overview or the per-subject risk summaries?"
> User B: "Give me the gist of the Acme deal." → deliver **A2 (Overview)** (with A1 if it aids the read); offer the per-subject detail.
> User C: "Break the Acme deal down subject by subject." → deliver **B (Per-subject risk summaries)**, headed by the index. A plain "summarize the Acme deal" still returns all three.
