# Snippet Design Spec

Design goals and pattern catalog for the inline snippet canvas. The actual CSS, colors, and copy-clipboard handler live in `scripts/generate_snippets.py` — that's the source of truth for values. This doc is the why.

## Design goals

- **Match Clarity's light theme** so the widget feels native to the product brand (lavender page, white cards, indigo accents, Clarity flag pills for severity).
- **Paste cleanly into IC slide decks.** PowerPoint, Google Slides, Word, and Notion all preserve inline-styled HTML on paste. So snippets ship as styled HTML and the analyst's slide picks up the styling intact.
- **Each block stands alone.** Headers, content, and source attribution on every block — so the analyst can copy any one block independently and it makes sense in isolation.

## Widget mode and file mode

Both are produced by default — the analyst gets the inline widget for fast copy AND the standalone file for browser viewing / sharing / archive. Same content, two surfaces.

| | Widget mode | File mode |
|---|---|---|
| Wrapper | No DOCTYPE / html / head / body — styles scoped under `.intelligo-snippet-root` | Full HTML document |
| Width | Inherits from chat container | 720px centered |
| Surface | `show_widget` inline | `present_files` clickable card → opens in browser |
| Use | Fast in-chat copy to slide deck | Full-page view / share / archive |

## Pattern catalog

Subject-level patterns (any scope):

- **A. Headline finding** — one finding as a callout. Severity chip + title + summary + source.
- **B. Severity count summary** — red / yellow / info pills with one-line descriptors of red and yellow.
- **C. Disclosure delta** — two-column (disclosed | found) + red-accented gap callout below.
- **D. Executive paragraph** — narrative paragraph styled as a pull-quote with indigo accent.
- **E. Coverage map** — categories checked, with check or dash and brief detail.
- **I. Info findings detail** — Clarity-native circular teal "i" badge + explanation + titled item + meta line. Rendered only when the analyst elevates info findings.

Project-scope-only patterns:

- **F. Deal-level severity summary** — factual two-line block. Top line states what severity levels are present across the deal; second line names the highest-severity finding with subject and brief finding text. Neutral background — no verdict color coding.
- **G. Subject roster** — table, one row per subject. Name, role, report level, severity pills (red, yellow, info). No judgement column.
- **H. Findings across the deal** — every red and yellow finding from any subject, with subject attribution, severity, finding text, source. Entries without finding text are not rendered.

## Why HTML, not images

Images don't preserve text — the analyst can't edit a typo, the IC can't search. HTML pastes as styled rich text into every major slide/doc tool while staying editable.
