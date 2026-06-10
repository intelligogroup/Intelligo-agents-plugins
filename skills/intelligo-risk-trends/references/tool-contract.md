# Clarity tool contract (assumed)

This is the interface the skill is written against. Treat it as a target, not
ground truth — at runtime, read the live tool schemas and adapt names/shapes.
The two tools marked **PROPOSE** don't exist yet; the specs below are written so
they can be handed to R&D as build requirements.

## Conventions

- Tools are scoped to the calling user's own organization. **Single-org only** — never span or compare other orgs (cross-org benchmarking is a separate skill).
- Dates are ISO-8601. Time windows are inclusive of `from`, exclusive of `to`.
- **Finding vs flag:** a *finding* is any item in a report; a *flag* is a finding the system marked (Red/Yellow/Info). **Most findings are unflagged** (`flag_level = none`). Analyse over findings, not only flags — unflagged ≠ unimportant. State whether a count covers flagged findings or all findings.
- A "flag" is a single flagged finding. What's stored vs not:
  - **level** (stored) ∈ {`Red`, `Yellow`, `Info`}. Info is informational (~40%+ of all flags) — keep it separate from adverse/"risk" totals.
  - **config name** (stored, internal) = a system constant like `FOUND_ADVERSE_MEDIA`, `COMPANY_PEP`. NOT user-facing and NOT a reliable category — many are generic (esp. analyst-entered).
  - **finding text/description** (stored) = where a flag's actual meaning lives. **Read this to understand or categorize a flag.**
  - **category / theme** = **NOT stored.** The `Reputational/Professional/Behavioral/Financial/Unknown` grouping was a *manual human aggregation* for a dashboard — do not assume the data carries it. Derive themes from finding content.
- Other dimensions: `product` (`NOW`, `A3`, `A2`, `A1`, `SMA`, `MONITORING`…),
  `product_type` (`Analyst`, `Automated`, `Monitoring`, `PDF`), `account_manager`,
  `entity_type` (`individual` | `company`). **Not every org subscribes to every
  product** — distinguish "zero flags" from "not subscribed".
- **Levels / grain:** `organization` (fixed to the user's own) → `report` (one ordered check ≈ one project/report) → `profile` → `flag`. Counts can be at **flag** grain (raw flag counts) or **report** grain (reports-with-flags). A report holds many flags, so the two differ — always state which grain a number uses.

---

## 1. get_projects — EXISTS

Lists investigations/cases. One project ≈ one ordered background check.

Assumed input:
```
{ "from": "2025-06-01", "to": "2026-06-01",
  "status": "completed|in_progress|all",
  "product": "NOW", "entity_type": "individual",
  "subject_id": "...", "limit": 500, "cursor": "..." }
```
Assumed output (per item): `project_id`, `subject_id`, `subject_name`, `entity_type`,
`created_at`, `completed_at`, `status`, `organization`, `product`, `product_type`,
`account_manager`, `flag_summary` { `red`, `yellow`, `info` } if cheaply available.

Used for: the universe of reports in a window (backbone of every trend).

## 2. get_profiles — EXISTS

The subjects behind projects.

Assumed input: `{ "profile_ids": [...] }` or filter `{ "entity_type": "...", "organization": "..." }`.
Assumed output: `profile_id`, `name`, `entity_type` (`individual|company`),
`organization`, `aliases`, linked `project_ids`.

Used for: identity resolution, entity-type/org grouping, subject rollups.

## 3. get_report_content — EXISTS

Full findings for one report.

Assumed input: `{ "project_id": "..." }` (or `report_id`).
Assumed output: `sections[]` each with `findings[]` where a finding has
`flag_level` (`Red|Yellow|Info|none`), `flag_config_name` (internal constant),
`title`, **`text`/`description`** (the human meaning), `entities[]`, `source`, `date`.

Used for: **reading the finding text to understand and theme a flag** (the only
reliable source of meaning), plus keyword-scanning when the search tool is absent.
There is no category field — derive themes from `text`/`description`.

---

## 4. search_findings — PROPOSE (build me)

**Why:** Intent 5 (cross-profile search) and emerging-risk detection both need
to find *which profiles mention X* without pulling and scanning every report
client-side. This is the single highest-leverage tool to build.

Proposed input:
```
{ "query": "Epstein",            // entity / keyword / phrase
  "match": "any|phrase|entity",  // loose vs exact vs resolved-entity
  "from": "...", "to": "...",     // optional window
  "flag_level": "Red|Yellow|Info|any",  // omit / "any" to search unflagged findings too
  "include_unflagged": true,      // default true — search ALL findings, not just flagged
  "product": "...", "entity_type": "...",
  "limit": 100 }
```
Proposed output (per match):
```
{ "profile_id", "subject_name", "entity_type", "project_id", "report_date",
  "flag_level", "flag_config_name",
  "snippet", "source", "score" }
```
Notes: return a supporting `snippet` (the finding text) so the user can judge
relevance and so themes can be derived from content; include a relevance `score`;
resolve obvious aliases when `match=entity`. No category field — don't invent one.

## 5. aggregate_flags — PROPOSE (build me)

**Why:** Intents 1–4 are counting problems. Doing the count server-side keeps
report bodies out of context and scales past a few hundred reports.

Proposed input:
```
{ "from": "...", "to": "...",
  "group_by": ["month","flag_level"], // any of: month, week, flag_level,
                                       //   flag_config_name, report, product, product_type,
                                       //   entity_type, subject, category(*derived — see below)
  "count": "flags|reports",            // flag-level vs report-level grain (e.g. reports-with-flags)
  "unit": "flags|findings",            // flags = flagged only; findings = all findings incl. unflagged
  "filters": { "flag_level": "Red", "product_type": "Analyst", "category": "...",
               "report_id": "...", "product": "...", "entity_type": "..." } }
```
Proposed output:
```
{ "buckets": [ { "month": "2026-01", "flag_level": "Red", "count": 12 }, ... ],
  "totals": { "red": 1477, "yellow": 24507, "info": 19090 } }
```
Notes: `group_by` should accept multiple dimensions; always return the
Red/Yellow/Info totals; allow a prior-period comparison flag or let the caller
make two calls and diff.

**`category` is a DERIVED field, not stored** (*). The dashboard's Flag Type chart
calls `group_by:["category"]` and filters on `category`; to make that real, R&D
must add a derived category by classifying each finding's text (a fixed label set
or an LLM/rules classifier), then expose it for group_by **and** as a filter.
Until that exists, the chart falls back to an empty state and theme grouping is
done client-side after reading `get_report_content` / `search_findings` snippets.

**Filtering / cross-filter:** `filters` must support `flag_level`, `product_type`,
`product`, `entity_type`, `report_id`, and (once built) `category`. The dashboard's
click-to-filter on the Flag Level and Product Type donuts simply re-calls
`aggregate_flags` with these filters set — so they need to be honored on every
group_by, including `month`/time buckets and the reports `count`.

---

## Mapping user language → action

Themes are **derived from finding content**, not selected from a filter. The
example themes below are a *starting vocabulary* a human used once — confirm each
against the actual finding text before applying it.

- "serious / actionable only" → filter `flag_level: Red` (optionally Red+Yellow); exclude Info — this one IS a real filter.
- "this year" → last 12 months; "this quarter" → current calendar quarter.
- a country/company/person name with no other intent → `search_findings` (Intent 5).
- "lawsuits", "fraud", "bankruptcy / PEP", "adverse media / watchlist", etc. → these are *themes to look for in the finding text*, not stored categories. Read content (or `search_findings` snippets), group what genuinely matches, and label in plain language.
