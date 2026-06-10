# Intelligo Profile Resolution

Shared reference for resolving a user's reference to a subject (by name or vague mention) to a single Intelligo Clarity Profile. Used by any Intelligo skill that operates on a specific profile — summary, finding-detail, flag-detail, comparison, etc.

This file defines the resolution logic only. The skill that loads it decides what to *do* with the resolved profile.

## Hard rules

- **Never silently combine profiles.** When multiple profiles look like duplicates, surface that pattern and let the user decide. Combining only happens on explicit user request and triggers a prominent caveat (see "Combining profiles" below).
- **Never invent fields.** Only surface what the connector returned.
- **Don't substitute summary for the user's actual ask.** This reference resolves *which* profile the user means — what to do with it (summarize, drill into a finding, compare, etc.) is up to the calling skill.

## Step 0 — Check if a profile is already in context

Before searching, check the conversation:

- Did a previous turn in this conversation resolve a profile? Look for: a prior call to `Get_profiles` followed by user selection (its result already carries the profile detail + report list), or an explicit profile_id surfaced earlier.
- If yes, and the user's current message is a follow-up that doesn't name a new subject (e.g. "tell me more about the bankruptcy finding," "what was the credit check?", "any red flags?", "compare with X"), **reuse the already-resolved profile.** Skip the rest of resolution.
- If the user names a different subject, or explicitly asks to start over, do fresh resolution.

This avoids forcing the user to re-identify the subject every time they ask a follow-up.

## Step 1 — Search profiles AND projects in parallel

Users don't always know whether they want a profile-level or project-level result. Search both.

**Call `Get_profiles` and `Get_projects` in parallel** with the user's query. (`Get_profiles` returns each candidate's full detail and report list, so no separate detail call is needed once the user picks.)

### Single match
- One profile match → use it. Continue to whatever the calling skill needs.
- One project match → the calling skill decides how to handle a project (typically: hand off to a project-handling skill if available, or offer profile-level alternatives from the project's `profiles` list).

### Multiple matches (any mix of profiles and projects)

Present everything in one unified list, labeled by type. Example:

> "I found a few matches for 'Acme':
>
> **Profiles** (subjects)
> 1. **Acme Holdings Inc** — Corp, Delaware US, project: Acme Series B
> 2. **Acme Asia Pte Ltd** — Pte Ltd, Singapore, project: Acme Series B
>
> **Projects** (investments)
> 3. **Acme Series B** — 3 profiles under it (Acme Holdings Inc, Acme Asia Pte Ltd, Jane Doe — CEO)
>
> Which one?"

Let the user pick by number or by describing one ("the company in Singapore," "the project one").

### User phrasing pre-disambiguates

Skip the mixed list when the user's words already pick a side:
- Phrasing that points at a person or company (e.g. "the **company** Acme," "the **person** named Acme," "the **subject** X") → only show profile matches.
- Phrasing that points at a deal (e.g. "the Acme **investment**," "the Acme **project**," "the **deal**") → only show project matches.

### No match

Say so plainly. Ask for additional identifying data the user might know: project name, company, jurisdiction, role. Don't guess.

## Step 2 — Disambiguating multiple profile matches

When 2+ profiles match, surface enough data per candidate that the user can pick correctly. **Show all available identifying fields.** The user can't go look at the system — they have to identify from what you show them.

For each candidate, show:

- **Persons**: display name (including suffix if set — Jr / Sr / III), DOB if known, current company + position, all jurisdictions, addresses (city/country at minimum), project name, labels, created date.
- **Companies**: official name, company type, all jurisdictions, addresses (city/country at minimum), project name, labels, created date.

One candidate per numbered block, with sub-bullets. The list will be longer than a one-liner — that's fine here.

## Step 3 — Recognize and flag common edge cases

When presenting candidates, call out the *pattern* the user is seeing so they know what to look for:

1. **Sr / Jr / generational suffix.** When two candidates share a name and one has a suffix (`Jr`, `Sr`, `III`), say: "These look like related people — note the suffixes."

2. **Likely duplicates (same subject, multiple profiles).** Duplicate detection is not exposed via MCP. Spot likely duplicates heuristically: same name + same DOB + same project, or same name + same primary jurisdiction + same primary company. When detected: "These may be duplicate profiles of the same subject — same DOB and project. Want me to use one of them, or you can ask me to combine (with caveats — see below)."

3. **Same-project companies (possibly subsidiary or locally-registered).** When 2+ company profiles share the same `project_id`, they're related to the same investment — could be loose (counterparty, advisor's firm) or strong (parent/subsidiary, locally-registered variant). There's no hard signal for the strong case, so use a name + jurisdiction heuristic:
   - Similar names (one is a substring of the other, share a common stem) **and** different jurisdictions → say: "Similar names, different jurisdictions — possibly parent/subsidiary or local registration of the same company."
   - Unrelated names → say: "Both connected to the same investment, but they look like distinct companies."
   - Always surface the same-project relationship explicitly so the user understands why they're seeing multiple results.

4. **Common name.** 3+ matches with nothing in common beyond name (different DOBs, different companies, different projects) → say: "Common name — these look like different people who share the name." Don't speculate further.

## Combining profiles (only on explicit user request)

**Default: never combine.** Always resolve to a single profile.

If the user explicitly asks to combine ("combine all the David Cohen profiles," "merge these," "treat these duplicates as one"), the calling skill proceeds — but its output must start with a prominent warning:

> ⚠ **Combined output across N profiles.** The information below was merged from multiple profiles in Intelligo. Combining sources increases the risk of mixing details that don't actually belong to the same person/company, and increases the risk of errors. Verify anything important against the individual profiles before acting on it.

For each merged item in the calling skill's output, tag the source profile in parentheses (e.g. "Bankruptcy filing 2019 (from profile 2 — Cohen Ventures)") so the user can trace anything back.

Don't combine without explicit user request. Don't offer combining proactively when duplicates are suspected — flag the suspicion, let the user decide.

## What this reference does NOT cover

- What to *do* with a resolved profile (summarize, fetch a specific finding, compare to another, drill into a flag, etc.) — that's the calling skill's job.
- The `org_id` parameter on tool calls — that's system-injected, calling skills don't think about it.
- Project-level operations — covered by whichever skill handles projects.
- Output formatting — the calling skill defines its own output structure.
