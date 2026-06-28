# Step-4 JSON edit cookbook

**You own the returned JSON from here on.** All edits happen in conversation, not via another tool call — re-calling `get_scoping_profiles` rebuilds from scratch, losing your edits and burning a fresh Workforce lookup.

The response gives you `companies` (fixed) + a `candidates` pool (≤15) + `recommendedPersonCount`. You SELECT `recommendedPersonCount` key persons from `candidates` to run; the rest stay the pool. "Editing" = moving people between your selected set and the pool, adding user-named people, and relabeling roles. Rank the pool by tenure (`roleStartDate` / `companyJoinDate`), role seniority, `isFounder`, and the client's layer pattern — and drop obvious wrong-person matches.

## Row shapes

> These mirror the `ScopingProfile` type (`container/scoping/types/scoping-profiles.ifc.ts`) and the `get_scoping_profiles` `outputSchema`. If a field is added or renamed there, update it here too — the shape lives in three places.

**Key person:**
```json
{ "kind": "key_person", "role": "CFO", "name": "Mike",
  "source": "client_input", "confidence": 1.0,
  "linkedEntity": "<primarySubjectName>", "depth": "<area.depth>",
  "jurisdictions": ["US"] }
```

**Entity (subsidiary, parent, affiliate):**
```json
{ "kind": "entity", "role": "subsidiary", "name": "Embark IP Holdings",
  "sector": "<classified>", "depth": "<area.depth>",
  "source": "client_input", "confidence": 1.0,
  "jurisdictions": ["US"] }
```

> **`jurisdictions` is ALWAYS an array of ISO 3166-1 alpha-2 codes — never a bare string.** Even a single jurisdiction is `["US"]`, not `"US"`. The field name is plural (`jurisdictions`), matching the pool you received; do **not** rename it to `jurisdiction` or collapse it to a scalar. Carry the array through verbatim from each selected candidate (a person who has worked across countries arrives as e.g. `["GB","US"]` — keep all of them). For person rows it comes from enrichment; for entity rows set the company's operating countries (HQ first) — when you only know the HQ country, use a one-element array. Omit the field only when you genuinely have no jurisdiction at all.

User-named persons you add get `source: "client_input"`, `confidence: 1.0`. The `candidates` pool contains only real people (no `<…-to-resolve>` placeholders) — if it's shorter than `recommendedPersonCount`, that's the cue to ask the user for names, not a row to invent. You may still *author* a placeholder yourself when adding officers at a related entity (see the Embark recipe) — use `source: "recommendation"`, `confidence: 0.5`.

## Per-request recipes

- **Initial selection** → from `candidates`, pick `recommendedPersonCount` to run (your selected set); leave the rest as the pool. Choose by tenure / role seniority / `isFounder` / the client's pattern, and skip wrong-person matches (enriched career shows no tie to the subject).

- **"Add Mike, the CFO"** → add a key-person row to your selected set (shape below). To stay at `recommendedPersonCount`, move your weakest current pick back to the pool.

- **"Drop the CIO" / "Remove [Name]"** → move that person from the selected set back to the pool; promote the next-best pool candidate to hold the count.

- **"Show me other options"** → present the strongest unselected `candidates` (you already hold their enriched detail). A swap = move one in, one out.

- **"Skip the board" / "No operators" / "Exclude [role]"** → drop selected people whose `role` matches; backfill from the pool with non-matching candidates until back at `recommendedPersonCount` or the pool is exhausted. If you run out, tell the user the count came in low (e.g. "only 3 non-board candidates in the pool — widen to KP_FULL_OFFICERS?").

- **"Change Mike from C-suite to founder" / relabel a role** → update the `role` field on that entry in place.

- **"Include Embark IP Holdings, the subsidiary, with 2 officers"** →
  1. Optionally call `classify_subject_sector` on "Embark IP Holdings" to get its sector.
  2. Append an entity row (shape above).
  3. Append 2 key-person rows with `linkedEntity: "Embark IP Holdings"` — either placeholders or user-named persons.

- **"Include the parent Acme Inc., no officers there"** → just the entity row, no person rows.

## The one rule that's easy to get wrong

When the user says "Mike, the CFO" or "the founders Alice and David", extract `{name, role}` as **separate fields** — never collapse the phrase into `name`. The backend uses `role` as a structured field feeding the kpLevel-priority sort and entity-assembly logic; a merged `"Mike, the CFO"` string lands in the name column with no role to sort on, degrading the recommendation. For "the founders Alice and David", broadcast the role: two rows, both `role: "founder"`.

## After any edit

Show the user the updated list briefly (name + role + linkedEntity is enough) and confirm the count vs the area target.
