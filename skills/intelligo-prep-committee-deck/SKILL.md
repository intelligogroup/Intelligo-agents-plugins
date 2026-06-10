---
name: intelligo-prep-committee-deck
description: Convert Intelligo Clarity background-check findings into Investment Committee (IC) ready materials — narrative summaries, slide-ready snippets, polished PDFs, or PPTX decks. Works at any scope — single subject report, full deal/project rollup, or hybrid (project overview with one subject in depth). Use whenever an analyst asks to "prepare for IC", "summarize the deal for committee", "roll up findings for project X", "build IC slides", "make an IC summary", "format Clarity findings", "create a project one-pager", "write the IC memo section", or wants to share Clarity output with partners, board, GC, or risk committee. Different funds have very different IC styles, so this skill always conducts a short intake before generating output. Trigger generously — analysts often describe the destination (their IC, their deal, their project) rather than naming the format.
---

# IC Formatter

## What this skill does

Clarity findings live inside the Intelligo platform in a structure optimized for review. Investment Committees want something different: a tight summary, the right level of detail for their audience, and findings framed against what the subject disclosed. Analysts currently copy-paste, screenshot, and hand-rewrite Clarity output to make it IC-ready. This skill replaces that manual work.

Two things vary across uses and the skill handles both:

1. **Scope** — single subject, full project rollup, or hybrid (project overview + deep dive on specific subjects). Scope changes what data is pulled and how the output is structured.
2. **Style** — even within the same firm type, ICs behave very differently. What actually predicts format is **who reads it** and **what they need to see first**. Intake asks behavioral questions, not "what kind of firm are you?".

## Core flow

1. **Establish scope** — single subject, project, or hybrid. Identify which.
2. **Offer the analyst to share an example** (optional) — a screenshot, prior deck, or sample memo. If provided, infer style and short-circuit later questions.
3. **Pull Clarity data, including automatic internal comparisons** — fetch the project, subjects, reports, flags, notes, sources. Automatically also compute a refresh-delta if a prior report exists, and cross-subject patterns for project/hybrid scope. These are Clarity-internal and free — included in the data layer; rendered only if they surface something interesting.
4. **Profile the IC** — ask the remaining intake questions (see `references/intake-flow.md`).
5. **Offer external enrichment** (optional, Q4) — recent news, public filings, internal CRM/docs, industry context. Non-Clarity sources only. Probe what's available before offering.
6. **Pick a flavor** — map intake answers to a flavor (see `references/flavors.md`).
7. **Generate output** — default is the inline snippet canvas via `show_widget`. PDF, PPTX, or downloadable HTML on request. Always preview in chat first.

## Resolving the subject / project in Clarity

Use the shared **`references/profile-resolution.md`** reference for the full resolution logic — context reuse, parallel profile/project search, disambiguation, duplicate detection, suffix handling, and the rules for combining profiles. That reference is shared across all Intelligo skills; this skill follows it.

What's specific to this skill on top of the shared logic:

- When the analyst's intent is project rollup or hybrid (Q0), prefer a project match if both a profile and a project are found under the same name. Confirm with the analyst when ambiguous.
- For hybrid scope, after resolving the project, ask which subject(s) to deep-dive — show the project's profile list and let the analyst pick.

**If Clarity MCP isn't available at all** (no Clarity tools loaded in the session), don't try to resolve. Offer three fallbacks: paste report content as text, attach a PDF export, or describe findings from memory (top-line flavors only). Then proceed with intake.

## Pulling the data

What to fetch depends on scope:

**Single subject:** subject identity (name, role, entity, jurisdictions), report metadata (level, dates, scope, coverage), flags by section with severity / title / finding text / source / date / review state / analyst notes, disclosure delta if available, coverage summary.

**Project rollup:** all of the above for every subject in the project, plus project identity, subject roster with per-subject flag counts, aggregate flag profile across the deal, red + analyst-elevated yellow findings attributed to subjects, deal-wide disclosure picture if applicable.

**Hybrid:** project rollup + full single-subject data for the deep-dived subject(s).

If a tool returns a different shape than expected, work with what you get; explain what's missing rather than fail.

## Generating output

### Mode A — Inline canvas + browser-openable file (default)

Always produce both in this mode:

1. **Inline canvas in chat (`show_widget`)** — the analyst sees the snippets next to the conversation and clicks Copy on each block to paste into their slide deck. Primary copy surface.
2. **Standalone HTML file presented as a clickable card (`present_files`)** — the analyst can click to open the same content in their browser for a full-page view, to share with a teammate, or to archive.

Both are generated from the same findings spec — same content, two surfaces. The widget is for fast copy; the file is for view / share / archive. The analyst doesn't have to pick — both are there.

Workflow:

1. Build the findings spec (JSON shape documented in `scripts/generate_snippets.py`).
2. Generate **both** outputs:
   ```bash
   # widget version (no html/head/body wrapper, for show_widget)
   python3 scripts/generate_snippets.py --widget findings.json /tmp/widget.html
   # standalone version (full HTML document, for present_files)
   python3 scripts/generate_snippets.py findings.json outputs/ic-snippets-<subject_slug>-<date>.html
   ```
3. Render the widget version via `show_widget` with a descriptive title like `ic_snippets_<subject_slug>`.
4. Present the file version via `present_files` so the analyst gets a clickable card pointing to the HTML file.
5. Tell the analyst: Copy buttons in the widget paste with formatting preserved; the card opens the same content in the browser if they want a full-page view or to share the file.

### Mode B — PPTX deck

Use the `pptx` skill. 1–4 slides per flavor: executive summary + flag counts, findings by severity, disclosure delta (if relevant), coverage + IC questions. Match the snippet visual style.

### Mode C — PDF

Use the `pdf` skill. Single document per the chosen flavor. Always include: cover/header with subject + report level + date, executive narrative, findings by severity, disclosure delta if applicable, coverage + Clarity link as appendix.

## Principles

- **Lead with severity + finding.** The IC reads the first paragraph. It must contain subject, highest-severity flag level present, and the underlying finding behind it — what was found, briefly, with source.
- **Pair every flag with its underlying finding.** A flag title alone is meaningless. If you don't have the finding text, leave the flag out.
- **Describe at severity level; the IC renders the verdict.** Intelligo assigns severity (red / yellow / info). Words like "clean", "material", "blocker", "high risk", "low risk", "concerning", "deal-breaker" are verdicts, and the verdict is the IC's call. Stick to describing what was found and at what severity; let the IC decide what severity means.
- **Preserve severity exactly as Clarity assigned it.** Don't reclassify yellow as red, or vice versa.
- **Clarity doesn't make investment recommendations** — don't fabricate or restate one.
- **Surface the disclosure delta when present.** If disclosed status is available, show found-but-not-disclosed items separately — often the IC's real question.
- **Cite every finding.** Source link or attribution per item.
- **Only describe what Clarity returned.** Gaps get marked as "not checked" or "no findings" — no speculation.
- **Use the analyst's language.** Deal names, sponsor names, fund vehicles. Profile resolution is in `references/profile-resolution.md` — no internal IDs in conversation.
- **Stay within the flavor's length budget.** A one-pager is one page; an executive summary is 4–8 sentences.
- **For snippets, return styled HTML.** Plain text loses the design intent that makes paste-into-slides work.

## Reference files

- `references/profile-resolution.md` — shared logic for resolving the user's reference to a single Clarity profile (used by all Intelligo skills)
- `references/intake-flow.md` — the question tree
- `references/flavors.md` — flavor catalog + audience × lead-with mapping table
- `references/snippet-design.md` — visual spec for snippets
- `assets/templates/` — markdown skeletons per flavor (for PDF/PPTX rendering)
- `scripts/generate_snippets.py` — widget renderer; canonical source for snippet HTML structure and JSON schema
