# Snippet HTML reference

How to write the IC snippet canvas. You write the HTML yourself, from a findings spec, following this file exactly. The styling, the markup and the rules here are the source of truth; do not invent other styling, cards or wording.

## 1. Build the findings spec first

Collect what you will show into this shape before writing any HTML. It keeps the two outputs (widget and file) identical in content.

```
{
  "scope": "subject" | "project" | "hybrid",   // drives which patterns render

  // --- Subject-scope fields (also used for hybrid deep-dive) ---
  "subject_name": "John Q. Sponsor",
  "subject_entity": "Acme Capital LP",
  "report_level": "Advantage Level 3",
  "report_date": "Nov 14, 2025",
  "prepared_by": "JD",
  "prepared_for": "Acme IC, Nov 18 mtg",
  "patterns": ["headline", "counts", "delta", "executive", "coverage"],

  // headline_findings: each entry MUST include `summary` (the underlying
  // finding text) and `source`. A flag with only severity + title is not a
  // finding and will be skipped by the renderer.
  "headline_findings": [
    {"severity": "red", "title": "Short label",
     "summary": "What was specifically found — full sentence with dates, amounts, what happened.",
     "source": "Source attribution + date"}
  ],

  "counts": {"red": 1, "yellow": 3, "info": 12,
             "red_detail": "...", "yellow_detail": "..."},
  "delta": {"disclosed": [...], "found": [...], "gap_summary": "..."},

  // info_flags: ONLY include when the analyst has explicitly elevated info
  // findings for the IC's attention. Info flags are skipped by default. When
  // included, each entry needs explanation + title; meta is optional.
  // Rendered in Intelligo's native style: circular teal 'i' badge + explanation
  // + titled item + meta line.
  "info_flags": [
    {"explanation": "Why this info flag was raised by Intelligo.",
     "title": "Citrin Cooperman LLP (1996 – 1999)",
     "meta": "Accountant · 1996–1999 · 3 years · Source: Previous version of LinkedIn"}
  ],

  "executive": "Narrative paragraph (factual, no verdict words)...",
  "coverage": [{"category": "Legal", "status": "checked", "detail": "15 yr"}, ...],

  // --- Project-scope fields (used when scope is "project" or "hybrid") ---
  "project_name": "Acme Acquisition",
  "deal_type": "PE buyout",

  // deal_headline: factual severity summary. NO verdict field. The IC
  // makes the verdict; the skill states what severity levels are present.
  "deal_headline": {
    "summary": "5 subjects reviewed at L3. 1 red, 4 yellow, 18 info.",
    "highest": "Highest-severity finding: [one-line finding + subject + source]."
  },

  // subjects: roster rows. NO judgement field — flag counts speak for
  // themselves. Verdicts like Clean/Material/Blocker are the IC's call.
  "subjects": [
    {"name": "...", "role": "...", "report_level": "3",
     "flags": {"red": 1, "yellow": 3, "info": 12}}
  ],

  // materials: each entry MUST include `summary` (the underlying finding).
  "materials": [
    {"subject": "John Q. Sponsor", "severity": "red",
     "title": "Short label",
     "summary": "Finding text — what was found, when, where, source."}
  ]
}
```

For hybrid scope, include both the project-level fields and the subject-level fields for the subject being looked at in depth.

Severity-only policy: Intelligo only assigns severity to findings (red / yellow / info). The spec has no verdict or judgement field, and the output never adds one. The skill states findings and severity; the committee decides what they mean.

## 2. Rules

**Which cards, in which order.** The order is fixed; `patterns` chooses among the subject-level cards but never reorders them.

1. Deal-level cards, only when `scope` is `project` or `hybrid`, and whatever `patterns` says:
   1. Deal-level severity summary, when `deal_headline` is present.
   2. Subject roster, when `subjects` is present.
   3. Findings across the deal, when `materials` is present.
2. Subject-level cards, each only when it is named in `patterns` and its data is present:
   1. `executive` → Executive paragraph
   2. `counts` → Severity count summary
   3. `headline` → one Headline finding card per entry in `headline_findings`
   4. `delta` → Disclosure delta
   5. `info_flags` → Info findings (elevated by analyst)
   6. `coverage` → Coverage map

When `patterns` is missing or empty, use `executive, counts, headline, delta, coverage` for subject scope and `coverage` alone for project or hybrid scope.

**What is left out.**

- A headline finding with no `summary` or no `source` is not rendered. A flag title alone is not a finding.
- A `materials` entry with no `summary` is not rendered.
- An info flag with no `explanation` or no `title` is not rendered; if none remain, the whole card is left out. Its `meta` line is optional.
- A roster pill is shown only for a count above zero. A subject with no flags at all keeps the `<div class="flag-pills">` wrapper and holds `<span style="color:#95A3B0;font-size:12px;">—</span>` inside it, where the pills would be.

**Values.**

- Escape `&`, `<`, `>`, `"` and `'` in every value you insert.
- Severity is written in lower case as the class name and capitalised in text: `red` → `Red severity`. A headline finding with no severity is `info`; a `materials` entry with no severity is `yellow`.
- The roster's report column is `L` followed by `report_level` (`L3`), or `L?` when it is missing.
- In the counts card, a missing count is `0` and a missing `red_detail` or `yellow_detail` is `—`.
- In the coverage card, `status: "checked"` (also the default) is `<span class="check">✓ {detail}</span>`; anything else is `<span class="dash">— {detail}</span>`, with `Not in scope` when there is no detail.

**Header.**

- Project or hybrid scope: title `IC Snippets — {project_name}` (`Deal` when missing); subtitle `{deal_type} · {number of subjects} subjects · Prepared by {prepared_by} · For {prepared_for}`.
- Subject scope: title `IC Snippets — {subject_name}`, followed by ` / {subject_entity}` when there is one; subtitle `Intelligo {report_level} · {report_date} · Prepared by {prepared_by} · For {prepared_for}`.

## 3. The two outputs

Both carry the same header and the same cards. Only the wrapper and the CSS differ.

### File mode (standalone page, for `present_files`)

```html
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>{FILE CSS}</style></head>
<body>

<div class="page-header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
<div class="instructions">
  Each block below is styled and ready to paste into PowerPoint, Google Slides, Word, or Notion. Click <strong>Copy</strong>, then paste into your slide — the formatting will be preserved.
</div>
{cards}
<script>{COPY SCRIPT}</script>
</body></html>
```

### Widget mode (inline, for `show_widget`)

No DOCTYPE, `html`, `head` or `body`, and no instructions block. Everything sits inside one `.intelligo-snippet-root` container so the styles stay scoped to it.

```html
<style>{WIDGET CSS}</style>
<div class="intelligo-snippet-root">

<div class="page-header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
{cards}
</div>
<script>{COPY SCRIPT}</script>
```

## 4. Card markup

Every card is a `.snippet` with a Copy button and a label. Copy the markup as written and fill in the values.

### Deal-level severity summary

The `<span class="highest">` is left out when there is no `highest` text.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Deal-level severity summary</div>
  <div class="deal-headline">
    <h3>Deal-level severity</h3>
    <div class="summary">{summary}<span class="highest">{highest}</span></div>
  </div>
</div>
```

### Subject roster

One `<tr>` per subject. Pills in this order, each only when its count is above zero.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Subject roster</div>
  <table class="roster-table">
    <thead><tr><th>Subject</th><th>Report</th><th>Flags</th></tr></thead>
    <tbody>
    <tr>
      <td><div class="name">{name}</div><div class="role">{role}</div></td>
      <td>L{report_level}</td>
      <td><div class="flag-pills"><span class="flag-pill r">{red}</span><span class="flag-pill y">{yellow}</span><span class="info-badge-pill"><span class="info-i">i</span>{info}</span></div></td>
    </tr></tbody>
  </table>
</div>
```

### Findings across the deal

One `.finding-item` per `materials` entry that has a summary.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Findings across the deal</div>
  <div class="findings-list">
    <div class="finding-item {severity}">
      <div class="subj">{subject} · {Severity} severity</div>
      <p class="ftitle">{title}</p>
      <p class="fsum">{summary}</p>
    </div></div>
</div>
```

### Executive paragraph

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Executive paragraph</div>
  <div class="exec-block">
    <h3>Executive summary</h3>
    <p class="pull">{executive}</p>
  </div>
</div>
```

### Severity count summary

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Severity count summary</div>
  <div class="count-block">
    <div class="count-pill red"><span class="num">{red}</span><span class="label">Red</span></div>
    <div class="count-pill yellow"><span class="num">{yellow}</span><span class="label">Yellow</span></div>
    <div class="count-pill info"><span class="num">{info}</span><span class="label">Info</span></div>
    <div class="count-detail">
      <strong>Red:</strong> {red_detail}<br>
      <strong>Yellow:</strong> {yellow_detail}
    </div>
  </div>
</div>
```

### Headline finding

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Headline finding</div>
  <div class="finding-block {severity}">
    <span class="severity-chip {severity}">{Severity} severity</span>
    <p class="finding-title">{title}</p>
    <p class="finding-summary">{summary}</p>
    <p class="finding-source">Source: {source}</p>
  </div>
</div>
```

### Disclosure delta

One `<li>` per item in each column.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Disclosure delta</div>
  <div class="delta-grid">
    <div class="delta-col">
      <h4>Disclosed by subject</h4>
      <ul><li>{disclosed item}</li></ul>
    </div>
    <div class="delta-col">
      <h4>Found by Intelligo</h4>
      <ul><li>{found item}</li></ul>
    </div>
  </div>
  <div class="delta-gap">
    <h4>Items found, not disclosed</h4>
    <p>{gap_summary}</p>
  </div>
</div>
```

### Info findings (elevated by analyst)

Only when the analyst has explicitly raised info findings for the committee. One `.info-flag-line` per flag; the `meta` paragraph is left out when there is no meta.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Info findings (elevated by analyst)</div>
  <div class="info-flag-line">
    <span class="info-icon">i</span>
    <div class="body">
      <p class="explain">{explanation}</p>
      <p class="title-row">{title}</p>
      <p class="meta">{meta}</p>
    </div>
  </div>
</div>
```

### Coverage map

One `.coverage-row` per category.

```html
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Coverage map</div>
  <div class="coverage-grid">
    <div class="coverage-row"><span>{category}</span><span class="check">✓ {detail}</span></div>
  </div>
</div>
```

## 5. File CSS

Copy it whole into the file-mode `<style>`.

```css
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; background: #FAFBFC; padding: 32px; color: #1B2631; }
.page-header { max-width: 720px; margin: 0 auto 24px; }
.page-header h1 { font-family: Georgia, "Times New Roman", serif; font-weight: 600; font-size: 22px; margin: 0 0 4px; }
.page-header p { color: #7F8C8D; margin: 0; font-size: 13px; }
.instructions { max-width: 720px; margin: 0 auto 32px; padding: 14px 18px; background: #EAF2F8; border-left: 3px solid #2E86C1; font-size: 13px; line-height: 1.5; }
.snippet { max-width: 720px; margin: 0 auto 28px; background: #FFFFFF; border: 1px solid #E5E8E8; border-radius: 4px; padding: 20px; position: relative; }
.copy-btn { position: absolute; top: 12px; right: 12px; font-size: 11px; padding: 5px 10px; cursor: pointer; border: 1px solid #BDC3C7; background: #FFFFFF; border-radius: 3px; color: #5D6D7E; }
.copy-btn:hover { background: #F4F6F7; }
.snippet-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #95A5A6; margin-bottom: 12px; }
.finding-block { padding: 16px 18px; border-left: 4px solid; background: #FDFEFE; }
.finding-block.red { border-color: #C0392B; }
.finding-block.yellow { border-color: #D68910; }
.finding-block.info { border-color: #5D6D7E; }
.severity-chip { display: inline-block; padding: 2px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 3px; color: #FFFFFF; margin-bottom: 8px; }
.severity-chip.red { background: #C0392B; }
.severity-chip.yellow { background: #D68910; }
.severity-chip.info { background: #5D6D7E; }
.finding-title { font-family: Georgia, serif; font-size: 16px; font-weight: 600; margin: 0 0 6px; }
.finding-summary { font-size: 12.5px; line-height: 1.55; margin: 0 0 8px; }
.finding-source { font-size: 11px; color: #7F8C8D; }
.count-block { display: flex; gap: 16px; align-items: center; }
.count-pill { padding: 10px 16px; border-radius: 6px; min-width: 70px; text-align: center; }
.count-pill .num { font-size: 22px; font-weight: 700; display: block; line-height: 1; }
.count-pill .label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; display: block; }
.count-pill.red { background: #FDEDEC; color: #922B21; }
.count-pill.yellow { background: #FDF2E9; color: #9C640C; }
.count-pill.info { background: #F2F4F4; color: #5D6D7E; }
.count-detail { font-size: 12px; line-height: 1.6; color: #1B2631; }
.count-detail strong { color: #C0392B; }
.delta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.delta-col { padding: 12px 14px; background: #F8F9F9; border-radius: 4px; }
.delta-col h4 { font-family: Georgia, serif; font-size: 13px; font-weight: 600; margin: 0 0 8px; color: #1B2631; }
.delta-col ul { margin: 0; padding-left: 16px; font-size: 12px; line-height: 1.6; }
.delta-gap { margin-top: 14px; padding: 12px 14px; background: #FDEDEC; border-left: 3px solid #C0392B; border-radius: 0 4px 4px 0; }
.delta-gap h4 { font-family: Georgia, serif; font-size: 13px; font-weight: 600; margin: 0 0 6px; color: #922B21; }
.delta-gap p { font-size: 12px; line-height: 1.55; margin: 0; }
.exec-block h3 { font-family: Georgia, serif; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #5D6D7E; margin: 0 0 10px; }
.exec-block .pull { font-family: Georgia, serif; font-size: 16px; line-height: 1.55; color: #1B2631; padding-left: 14px; border-left: 3px solid #2E86C1; }
.coverage-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 18px; font-size: 12px; }
.coverage-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dotted #E5E8E8; }
.coverage-row .check { font-weight: 600; color: #229954; }
.coverage-row .dash { color: #BDC3C7; }
.deal-headline h3 { font-family: Georgia, serif; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #5D6D7E; margin: 0 0 10px; }
.deal-headline .summary { font-family: Georgia, serif; font-size: 16px; line-height: 1.55; padding: 14px 18px; border-radius: 4px; background: #F8F9F9; border-left: 4px solid #5D6D7E; color: #1B2631; }
.deal-headline .summary .highest { display: block; margin-top: 8px; font-size: 14px; color: #5D6D7E; font-style: italic; }
.roster-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.roster-table th { text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #7F8C8D; padding: 8px 10px; border-bottom: 2px solid #E5E8E8; background: #F8F9F9; font-weight: 600; }
.roster-table td { padding: 10px; border-bottom: 1px solid #F4F6F7; vertical-align: top; }
.roster-table .name { font-weight: 600; }
.roster-table .role { color: #7F8C8D; font-size: 11px; }
.roster-table .flags-cell { font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 12px; }
.roster-table .flags-cell .r { color: #C0392B; font-weight: 700; }
.roster-table .flags-cell .y { color: #D68910; font-weight: 700; }
.roster-table .flags-cell .i { color: #7F8C8D; }
.findings-list .finding-item { padding: 12px 14px; margin-bottom: 8px; border-left: 3px solid; background: #FDFEFE; border-radius: 0 4px 4px 0; }
.findings-list .finding-item.red { border-color: #C0392B; }
.findings-list .finding-item.yellow { border-color: #D68910; }
.findings-list .finding-item .subj { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #7F8C8D; font-weight: 600; margin-bottom: 4px; }
.findings-list .finding-item .ftitle { font-family: Georgia, serif; font-size: 14px; font-weight: 600; margin: 0 0 4px; }
.findings-list .finding-item .fsum { font-size: 12px; line-height: 1.5; margin: 0; }
```

## 6. Widget CSS

Copy it whole into the widget-mode `<style>`.

```css
.intelligo-snippet-root { font-family: -apple-system, "Inter", "Segoe UI", Helvetica, Arial, sans-serif; background: #EAEAFF; padding: 22px; border-radius: 12px; color: #1B2631; }
.intelligo-snippet-root .page-header { margin: 0 0 18px; }
.intelligo-snippet-root .page-header h1 { font-weight: 500; font-size: 17px; margin: 0 0 4px; color: #1B2631; letter-spacing: -0.1px; }
.intelligo-snippet-root .page-header p { color: #6B7C8C; margin: 0; font-size: 12px; }
.intelligo-snippet-root .snippet { margin: 0 0 14px; background: #FFFFFF; border: 1px solid #E5E8F0; border-radius: 12px; padding: 18px; position: relative; }
.intelligo-snippet-root .copy-btn { position: absolute; top: 12px; right: 12px; font-size: 11px; padding: 7px 14px; cursor: pointer; border: 1px solid #3D3FE2; background: #FFFFFF; border-radius: 8px; color: #3D3FE2; font-weight: 500; }
.intelligo-snippet-root .copy-btn:hover { background: #3D3FE2; color: #FFFFFF; }
.intelligo-snippet-root .snippet-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; color: #95A3B0; margin-bottom: 12px; font-weight: 500; }
.intelligo-snippet-root .deal-headline .summary { font-size: 14px; line-height: 1.6; padding: 14px 16px; border-radius: 8px; background: #F4F5FF; border-left: 3px solid #3D3FE2; color: #1B2631; }
.intelligo-snippet-root .deal-headline .summary .highest { display: block; margin-top: 10px; font-size: 12.5px; color: #5A6878; }
.intelligo-snippet-root .roster-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.intelligo-snippet-root .roster-table th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #95A3B0; padding: 8px 12px 12px; border-bottom: 1px solid #ECEFF5; font-weight: 500; }
.intelligo-snippet-root .roster-table td { padding: 12px; border-bottom: 1px solid #ECEFF5; vertical-align: middle; color: #1B2631; }
.intelligo-snippet-root .roster-table tr:last-child td { border-bottom: none; }
.intelligo-snippet-root .roster-table .name { font-weight: 500; color: #1B2631; font-size: 13px; }
.intelligo-snippet-root .roster-table .role { color: #95A3B0; font-size: 11px; margin-top: 2px; }
.intelligo-snippet-root .flag-pills { display: inline-flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.intelligo-snippet-root .flag-pill { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; line-height: 1; }
.intelligo-snippet-root .flag-pill.r { background: #E94E64; color: #FFFFFF; }
.intelligo-snippet-root .flag-pill.y { background: #F0CE3F; color: #2A1F00; }
.intelligo-snippet-root .info-badge-pill { display: inline-flex; align-items: center; gap: 5px; padding: 2px 9px 2px 4px; border-radius: 999px; background: #E9F8F5; color: #0D8473; font-size: 11px; font-weight: 500; line-height: 1; }
.intelligo-snippet-root .info-badge-pill .info-i { width: 16px; height: 16px; border-radius: 50%; background: #FFFFFF; border: 1.5px solid #4FE3D0; color: #0D8473; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 600; font-style: italic; font-family: Georgia, serif; }
.intelligo-snippet-root .info-flag-line { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-top: 1px solid #ECEFF5; }
.intelligo-snippet-root .info-flag-line:first-child { border-top: none; padding-top: 0; }
.intelligo-snippet-root .info-icon { flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%; background: #FFFFFF; border: 2px solid #4FE3D0; color: #0D8473; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; font-style: italic; font-family: Georgia, serif; margin-top: 2px; }
.intelligo-snippet-root .info-flag-line .body { flex: 1; }
.intelligo-snippet-root .info-flag-line .body .explain { font-size: 13px; line-height: 1.5; color: #4A5868; margin: 0 0 6px; }
.intelligo-snippet-root .info-flag-line .body .title-row { font-size: 14px; font-weight: 500; color: #1B2631; margin: 0 0 2px; }
.intelligo-snippet-root .info-flag-line .body .meta { font-size: 11.5px; color: #95A3B0; margin: 0; }
.intelligo-snippet-root .count-block { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.intelligo-snippet-root .count-detail { font-size: 12.5px; line-height: 1.6; color: #1B2631; flex: 1; min-width: 200px; margin-top: 10px; }
.intelligo-snippet-root .severity-chip { display: inline-block; padding: 3px 10px; font-size: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; border-radius: 999px; margin-bottom: 8px; }
.intelligo-snippet-root .severity-chip.red { background: #E94E64; color: #FFFFFF; }
.intelligo-snippet-root .severity-chip.yellow { background: #F0CE3F; color: #2A1F00; }
.intelligo-snippet-root .severity-chip.info { background: #F0F2F7; color: #6B7C8C; }
.intelligo-snippet-root .findings-list .finding-item { padding: 14px 16px; margin-bottom: 10px; background: #F8F9FC; border-radius: 8px; border-left: 3px solid; }
.intelligo-snippet-root .findings-list .finding-item:last-child { margin-bottom: 0; }
.intelligo-snippet-root .findings-list .finding-item.red { border-left-color: #E94E64; }
.intelligo-snippet-root .findings-list .finding-item.yellow { border-left-color: #F0CE3F; }
.intelligo-snippet-root .findings-list .finding-item .subj { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #95A3B0; font-weight: 500; margin-bottom: 6px; }
.intelligo-snippet-root .findings-list .finding-item .ftitle { font-size: 14px; font-weight: 500; margin: 0 0 6px; color: #1B2631; }
.intelligo-snippet-root .findings-list .finding-item .fsum { font-size: 12.5px; line-height: 1.6; margin: 0; color: #4A5868; }
.intelligo-snippet-root .finding-block { padding: 0; background: transparent; }
.intelligo-snippet-root .finding-title { font-size: 15px; font-weight: 500; margin: 0 0 6px; color: #1B2631; }
.intelligo-snippet-root .finding-summary { font-size: 13px; line-height: 1.6; margin: 0 0 8px; color: #4A5868; }
.intelligo-snippet-root .finding-source { font-size: 11px; color: #95A3B0; margin: 0; }
.intelligo-snippet-root .delta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.intelligo-snippet-root .delta-col { padding: 12px 14px; background: #F8F9FC; border-radius: 8px; }
.intelligo-snippet-root .delta-col h4 { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 8px; color: #95A3B0; }
.intelligo-snippet-root .delta-col ul { margin: 0; padding-left: 16px; font-size: 12.5px; line-height: 1.7; color: #1B2631; }
.intelligo-snippet-root .delta-gap { margin-top: 12px; padding: 14px 16px; background: #FEF1F3; border-left: 3px solid #E94E64; border-radius: 0 8px 8px 0; }
.intelligo-snippet-root .delta-gap h4 { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 6px; color: #E94E64; }
.intelligo-snippet-root .delta-gap p { font-size: 12.5px; line-height: 1.55; margin: 0; color: #1B2631; }
.intelligo-snippet-root .exec-block h3 { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; color: #95A3B0; margin: 0 0 10px; }
.intelligo-snippet-root .exec-block .pull { font-size: 14px; line-height: 1.6; color: #1B2631; padding-left: 14px; border-left: 3px solid #3D3FE2; margin: 0; }
.intelligo-snippet-root .coverage-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 18px; font-size: 12.5px; }
.intelligo-snippet-root .coverage-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #ECEFF5; color: #1B2631; }
.intelligo-snippet-root .coverage-row:last-child { border-bottom: none; }
.intelligo-snippet-root .coverage-row .check { font-weight: 500; color: #1FA84F; }
.intelligo-snippet-root .coverage-row .dash { color: #95A3B0; }
```

## 7. Copy script

Copy it whole into the `<script>` at the end of either output. It copies one card to the clipboard as styled HTML, without the button and the label.

```js
function copyBlock(btn) {
  const block = btn.parentElement;
  const clone = block.cloneNode(true);
  const btnClone = clone.querySelector('.copy-btn');
  const labelClone = clone.querySelector('.snippet-label');
  if (btnClone) btnClone.remove();
  if (labelClone) labelClone.remove();
  const html = clone.innerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const data = [new ClipboardItem({ 'text/html': blob, 'text/plain': new Blob([clone.innerText], { type: 'text/plain' }) })];
  navigator.clipboard.write(data).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
  }).catch(() => {
    const range = document.createRange();
    range.selectNode(clone);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    document.execCommand('copy');
    sel.removeAllRanges();
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
  });
}
```
