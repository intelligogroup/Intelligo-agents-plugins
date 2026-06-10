# IC Flavors

Each flavor is a starting point — a default structure, length, tone, and emphasis. Pick the one that matches the analyst's intake answers, then adjust. Flavors are not exclusive; you can blend.

Flavors are named by behavior, not by firm type. Firm type doesn't reliably predict IC format. What predicts format: who's reading and what the output should lead with. The mapping table at the bottom shows how to pick.

The no-judgement and no-flag-without-finding rules from SKILL.md apply to every flavor. Where a flavor says "severity summary" it means a factual one-line description of what flag levels are present — never a verdict like "clean" or "material".

## Flavor 1 — Severity-first compact (lead-with: highest-severity flag)

**When:** Audience needs to decide in seconds. Lead-with answer was "highest-severity flag + finding".

**Length:** Strictly compact. ~150–300 words. One page max.

**Structure:**

1. **Top bar:** subject (or deal), report level, date, flag count summary (e.g. "1 red · 3 yellow · 12 info").
2. **The highest-severity finding** (1 short paragraph, 2–3 sentences): the actual finding behind the most severe flag, including what specifically was found, source, date.
3. **Other red and yellow flags** (1 line each): severity + finding text + source.
4. **Footer:** Clarity report link, analyst initials.

**Tone:** Telegraphic. Bullets and short sentences only. Verbs, not adjectives. Factual, no judgement adjectives ("major", "critical", "serious") — let the severity level and the finding text do the work.

**Template:** `assets/templates/one-pager-tear-sheet.md`

---

## Flavor 2 — Narrative memo (lead-with: narrative)

**When:** Audience is investment partners who want a story they can follow and weigh. Lead-with answer was "narrative".

**Length:** 1–2 pages worth, ~400–800 words.

**Structure:**

1. **Severity summary** (1 sentence): factual, describes what flag levels are present. "Background review surfaced 1 red flag and 3 yellow flags" or "No red flags; 2 yellow flags; otherwise clean coverage." No verdict words.
2. **Subject snapshot** (2–3 sentences): who, role, entity, jurisdictions checked, report level.
3. **Findings** (narrative paragraphs): each finding written as 1–3 sentences. Lead each with its severity level (Red / Yellow), then the underlying finding text — what was specifically found, when, where — and source attribution. Group by severity (red first, then yellow). Skip info flags unless analyst flagged them.
4. **Disclosure delta** (if applicable): what the subject disclosed vs. what we found. Highlight gaps.
5. **Coverage and confidence** (1 paragraph): what was checked, gaps, why this report level was chosen.

**Tone:** Professional, declarative. No hedging language. No "may indicate" — say what was found and what wasn't. No verdict adjectives.

**Template:** `assets/templates/narrative-memo.md`

---

## Flavor 3 — Disclosure delta (lead-with: disclosure delta)

**When:** Lead-with answer was "disclosure delta". The IC's actual question is whether the subject was honest, not whether the finding itself is bad. Common when working with sponsors / counterparties who may not have a perfect record but are expected to disclose upfront.

**Length:** 1 page, ~300–500 words.

**Structure:**

1. **Headline:** factual description of the delta, no judgement words. "All disclosed items confirmed by Clarity" / "Items found that were not disclosed: [count]" / "Subject disclosed [X]; Clarity found [Y additional items]."
2. **What was disclosed by the subject** (table or list).
3. **What we found** (parallel table or list).
4. **Gaps** (red box): items found that weren't disclosed. Each gap rated material / non-material with reasoning.
5. **Matches** (smaller section): items found that were also disclosed by the subject. Just list them — no commentary on what it means about the subject.
6. **Coverage:** what was checked.

**Tone:** Factual, side-by-side. Don't editorialize on motive — show the delta.

**Template:** `assets/templates/disclosure-delta.md`

---

## Flavor 4 — Flags-first forensic (lead-with: all red/yellow + audience: risk/GC)

**When:** Audience is risk / compliance / legal. They want every red and yellow flag with the underlying finding and source documents. Lead-with answer was "all red and yellow flags upfront".

**Length:** As long as needed, structured for scanning.

**Structure:**

1. **Header:** subject, report level, scope, coverage map.
2. **Red flags** (full detail each): severity level, finding title, finding text (what was found, when, where), source link, jurisdiction, analyst note (verbatim from Clarity if present), suggested IC question.
3. **Yellow flags** (same format, shorter).
4. **Info flags** (summarized in a table — title + source).
5. **Methodology and limits.**

**Tone:** Forensic and neutral. State what was found. Never characterize the finding ("alarming", "concerning", "serious") — risk/GC reads the finding text themselves.

**Template:** `assets/templates/flags-by-severity.md`

---

## Flavor 5 — Plain-language brief (audience: board / non-technical)

**When:** Audience is board members, university trustees, non-technical IC seats. Audience answer was "board / non-technical".

**Length:** ~250–400 words.

**Structure:**

1. **Plain-English summary:** what we checked, and what was found at each severity level. Describe the findings, not a verdict. Avoid jargon (no "PEP", no "OFAC", no "UCC" without explanation).
2. **Red and yellow findings** (if any): each in 2 sentences max, plain language. State the finding, not how to feel about it.
3. **Coverage and confidence** in the result (1 paragraph).
4. **What the IC should ask** (3 suggested questions tied to specific findings).

**Tone:** Plain English. No jargon. No verdict adjectives. Use analogies where helpful but never to characterize how bad something is.

**Template:** `assets/templates/executive-narrative.md`

---

## Flavor 6 — Project rollup (scope: project or hybrid)

**When:** Scope is project or hybrid (always — regardless of audience or lead-with). Picks up tone from whichever single-subject flavor matches the audience and lead-with answers.

**Length:** 1–2 pages. Length scales with subject count, not with the volume of findings.

**Structure:**

1. **Deal header:** project name, deal type, subjects in scope, report levels used, date prepared.
2. **Deal-level severity summary:** one factual sentence describing what's present across the deal. Examples: "5 subjects reviewed: 1 with red flag, 1 with yellow flags only, 3 with no flags." or "All 4 subjects: no red flags; 2 with yellow flags." Then a single line naming the most severe finding and which subject it's on. This is the most-read line — keep it factual.
3. **Subject roster:** small table or list, one row per subject. Columns: subject name, role, report level, flag counts (R/Y/I). No verdict column — flag counts speak for themselves. If the analyst wants to highlight a specific subject, use a star or marker, not a verdict.
4. **Findings across the deal:** every red flag and yellow flag, attributed to its subject, with the underlying finding text and source. Don't show flag titles alone — always pair with finding. Group by subject when there are many; otherwise group by severity.
5. **Deal-wide disclosure picture** (if Q3 was disclosure delta): did the deal's principals disclose what we found? List gaps factually.
6. **Coverage and confidence:** what was checked across subjects, any gaps. If different subjects got different report levels, explain why.
7. **Subjects with no flags:** brief mention so IC knows they weren't skipped — "Reports on [X, Y, Z] had no flags raised."

**Tone:** Inherited from the matching single-subject flavor (1–5) based on audience and lead-with answers. Never includes deal-level verdict language.

**Template:** `assets/templates/project-rollup.md`

**Hybrid use:** for hybrid scope, use this template as the spine, then embed the relevant single-subject flavor template inline at the right point (typically after the material findings list, before coverage).

---

## Choosing the flavor

**Scope wins first.** If scope is project or hybrid, always use Flavor 6 (project rollup) as the structural spine. Then look up the single-subject flavor below for tone and any embedded deep-dive sections.

**For single-subject scope (or to set the tone for project rollup), pick by audience + lead-with:**

| Audience ↓ / Lead-with → | Highest-severity flag | All red/yellow flags | Disclosure delta | Narrative |
|---|---|---|---|---|
| Investment partners | F1 Severity-first compact | F2 Narrative *(elevated)* | F3 Disclosure delta | F2 Narrative |
| Risk / GC | F1 Severity-first *(compact)* | F4 Flags forensic | F3 Disclosure delta | F4 Flags forensic |
| Board / non-technical | F5 Plain-language | F5 Plain-language | F5 Plain-language | F5 Plain-language |
| Mixed | F1 Severity-first compact | F2 Narrative | F3 Disclosure delta | F2 Narrative |

**Audience override:** if audience is board/non-technical, Flavor 5 always wins regardless of lead-with — the board can't handle the others. Translate the lead-with preference into the structure inside Flavor 5 (lead the plain-language summary with the relevant angle).

**Format override:** the format answer (Q2 — slides / memo / one-pager / PDF) sets the OUTPUT mode, not the flavor. The flavor still maps from audience + lead-with. So "narrative memo as slide-ready snippets" is valid — Flavor 2 structure rendered as snippet blocks.

## Blending flavors

It's common to blend. Examples:

- Partners audience + flags lead → Flavor 2 (narrative) with a Flavor 4 appendix for risk-curious partners.
- Project rollup for a board → Flavor 6 structure with Flavor 5 plain-language tone throughout.
- Disclosure-delta-led project rollup → Flavor 6 with Flavor 3 as the deep-dive embed for any subject with a disclosure gap.

When blending, keep the lead consistent (whatever the user picked in Q3 of intake).
