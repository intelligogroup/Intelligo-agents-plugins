---
name: intelligo-legal-explainer
description: >
  Explains legal and regulatory findings from Intelligo reports — individuals and companies.
  Four layers: definition, jurisdiction/issuing body context, pattern assessment, internet research.
  Trigger on: "explain this finding", "what does this mean", "is this serious", "is this common in [country]",
  "what does the internet say", "is this a red flag", "explain this lawsuit", "what is a lien",
  "what is a bankruptcy filing", "explain this sanction", "what does this watchlist mean",
  "is this PEP significant", "what does SECO mean", "what is OFAC", "what does CAATSA listing mean",
  "what is OFSI", "explain this enforcement action", "what does sanctions list mean",
  "I want to know more on the regulatory findings", "how significant is this watchlist hit",
  "what does this designation mean".
  Do NOT auto-trigger. Do NOT mix Intelligo data with internet data.
---

# Intelligo Legal & Regulatory Explainer

## Purpose
Explain and contextualize legal and regulatory findings from Intelligo reports.
Covers individuals and companies. User may need one layer or all four — only present what is relevant and supported.

## Scope
**Legal findings:** judgments, liens, bankruptcies, garnishments, civil suits, criminal charges, court orders, debt recovery actions
**Regulatory findings:** sanctions lists (OFAC, SECO, OFSI, EU, UN, CAATSA, etc.), watchlist hits, PEP designations, enforcement actions, debarment, regulatory bans, disqualifications

---

## Four Layers

### Layer 1 — Definition
What is this type of finding?

**Legal terms:**
- For **US findings**: Claude may define standard legal terms without a citation. Use plain language.
- For **non-US findings**: If the term or implications differ from the US equivalent, a citation is required. If the meaning is genuinely universal, no citation needed. When in doubt, cite.

**Regulatory terms:**
- Claude may define well-established regulatory bodies and list types (OFAC, OFSI, EU sanctions, UN sanctions, PEP) without a citation — these are internationally standardized.
- For lesser-known or country-specific bodies (e.g. SECO, CAATSA oligarch list), provide a plain language explanation. Citation required if making claims about what listing on that specific list implies legally or operationally.
- Explain what the designation means practically: what does being on this list mean for the subject, their counterparties, and financial relationships?
- If Claude is not certain of the definition — say so. Do not guess.

### Layer 2 — Jurisdiction & Issuing Body Context
What does this finding mean given where it comes from?

- For legal findings: is this type of case routine or significant in this jurisdiction?
- For regulatory findings: what is the authority and reach of the issuing body? Is this a primary sanctions list, secondary, or advisory? What are the practical consequences of this designation?
- Are there geopolitical or systemic factors that affect how seriously this should be taken?
- **Citation required** for any jurisdiction-specific or body-specific claim.
- If no reliable source is found — say so. Do not present the insight.

### Layer 3 — Pattern Assessment
Does this finding stand alone or reflect a pattern?

- Look across all legal and regulatory findings mentioned in the conversation/report
- Assess: single incident vs. repeated behavior vs. cross-jurisdictional pattern vs. escalating designations
- Note if findings conflict with the subject's professional role
- For regulatory findings: multiple sanctions lists from different jurisdictions is a stronger signal than a single listing
- This layer uses only what is present in the conversation — no internet research needed
- If there is only one finding and no pattern to assess — skip this layer entirely

### Layer 4 — Internet Research
What do publicly available internet sources say about this specific finding or subject?

**Strict rules — no exceptions:**
- Every claim must have a source URL. No source = claim is dropped entirely.
- Never reference, repeat, or paraphrase Intelligo data in this section
- Never mix internet findings with Intelligo findings — hard separation always
- If search returns nothing useful — say so explicitly. Do not fill the gap with inference.
- It is acceptable (and preferred) to say "no additional information found online"

---

## Execution Steps

### Step 1 — Identify the Finding
Extract from the Intelligo report or conversation:
- Subject name and type (individual / company)
- Finding type (legal or regulatory — specify)
- Issuing body or jurisdiction (country, court, sanctions authority)
- Details (list name, designation date, case details, outcome if known)

### Step 2 — Determine Which Layers Are Needed
- User asked "what is X" → Layer 1
- User asked "is this significant" / "what does this body mean" → Layer 2
- Multiple findings visible in the report → Layer 3
- User asked "what does the internet say", "research this", "tell me more", "I want to know more" → Layer 4
- User asked a broad question like "explain this finding" → all applicable layers

### Step 3 — Execute Each Relevant Layer
Run web searches for Layers 2 and 4 as needed.

**Search queries:**
- Layer 2 (legal): `[finding type] [country] legal system significance`
- Layer 2 (regulatory): `[sanctions body] what does listing mean` / `[list name] designation criteria consequences`
- Layer 4: `"[Subject Name]" "[list name or case details]"` / `"[Subject Name]" sanctions watchlist [year]`

### Step 4 — Output

Only include layers that have something to say. If a layer has no supported content — omit it entirely.

---

#### Output Format:

**📋 [Legal / Regulatory] Finding: [Finding Type] — [Jurisdiction / Issuing Body]**

**What it is:**
[Layer 1 — plain language definition. Cite if non-US legal term differs, or if making specific claims about a regulatory body's reach.]

**Context:**
[Layer 2 — jurisdiction or issuing body context with inline citations. Omit if no reliable source found.]

**Pattern:**
[Layer 3 — pattern assessment using report data only. Omit if single finding with nothing to compare.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 **INTERNET CONTEXT** — *Unverified. Independent of the Intelligo report.*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Layer 4 — internet research only. Each claim has a source. If nothing found, state it and close the section.]

**Sources:**
- [Source name — URL]

⚠️ *Internet context is based solely on publicly available sources. It is independent of and not equivalent to verified Intelligo findings.*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## Non-Negotiable Rules
1. **No source = no claim** — for internet findings, if there is no URL to back it, it does not appear
2. **No mixing** — Intelligo data and internet data are always in separate, visually distinct sections
3. **No guessing** — if Claude is uncertain, say so explicitly
4. **No padding** — omit any layer that has nothing supported to say
5. **Citations required** for non-US jurisdiction claims and regulatory body-specific claims in Layers 1 and 2
6. **Both individuals and companies** are in scope
