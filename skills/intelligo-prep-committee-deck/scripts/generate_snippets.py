#!/usr/bin/env python3
"""
Generate styled IC snippets HTML from a JSON spec of findings.

Usage:
    python generate_snippets.py findings.json output.html

findings.json schema:
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

For hybrid scope, include BOTH the project-level fields and the subject-level
fields for the subject(s) being deep-dived. The script will render project
blocks first, then subject blocks.

Severity-only policy:
  Intelligo only assigns severity to findings (red / yellow / info). The
  schema deliberately omits any "verdict" or "judgement" field. The skill
  describes findings + severity; the IC interprets what they mean. This is
  enforced by the schema, not just convention.

The script writes a single self-contained HTML file with copy-to-clipboard
buttons on each block. The analyst opens the file in a browser and clicks
Copy on the blocks they want, then pastes into their IC slide deck.
"""

import json
import sys
import html as html_lib
from pathlib import Path

FILE_CSS = """
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
"""

# Widget-mode CSS: matches the Intelligo light-theme design system.
# Lavender page background, white cards with subtle borders and rounded
# corners, indigo (#3D3FE2) primary accent, Intelligo flag pills for severity
# (red / yellow / muted-info), no serif fonts. Designed to look native inside
# the Intelligo product AND to paste cleanly into light-themed IC slide decks.
WIDGET_CSS = """
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
"""

COPY_SCRIPT = """
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
"""


def esc(s):
    return html_lib.escape(str(s)) if s is not None else ""


def render_headline(finding):
    """Headline finding snippet. Requires finding summary + source.

    A flag without an underlying finding is meaningless — flag titles alone
    are too generic. If summary is missing, the renderer skips this entry
    and emits a comment so the caller knows.
    """
    summary = (finding.get("summary") or "").strip()
    source = (finding.get("source") or "").strip()
    if not summary or not source:
        return ("<!-- Skipped headline finding: missing summary or source. "
                "A flag without its underlying finding text and source is not "
                "shown — generic flag titles are not sufficient for IC output. -->")
    sev = finding.get("severity", "info").lower()
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Headline finding</div>
  <div class="finding-block {sev}">
    <span class="severity-chip {sev}">{sev.capitalize()} severity</span>
    <p class="finding-title">{esc(finding.get("title"))}</p>
    <p class="finding-summary">{esc(summary)}</p>
    <p class="finding-source">Source: {esc(source)}</p>
  </div>
</div>"""


def render_counts(counts):
    """Severity count summary. `red_detail` and `yellow_detail` should be
    short finding text (not just titles) — what was actually found, briefly.
    """
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Severity count summary</div>
  <div class="count-block">
    <div class="count-pill red"><span class="num">{esc(counts.get("red", 0))}</span><span class="label">Red</span></div>
    <div class="count-pill yellow"><span class="num">{esc(counts.get("yellow", 0))}</span><span class="label">Yellow</span></div>
    <div class="count-pill info"><span class="num">{esc(counts.get("info", 0))}</span><span class="label">Info</span></div>
    <div class="count-detail">
      <strong>Red:</strong> {esc(counts.get("red_detail", "—"))}<br>
      <strong>Yellow:</strong> {esc(counts.get("yellow_detail", "—"))}
    </div>
  </div>
</div>"""


def render_delta(delta):
    disclosed_items = "".join(f"<li>{esc(x)}</li>" for x in delta.get("disclosed", []))
    found_items = "".join(f"<li>{esc(x)}</li>" for x in delta.get("found", []))
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Disclosure delta</div>
  <div class="delta-grid">
    <div class="delta-col">
      <h4>Disclosed by subject</h4>
      <ul>{disclosed_items}</ul>
    </div>
    <div class="delta-col">
      <h4>Found by Intelligo</h4>
      <ul>{found_items}</ul>
    </div>
  </div>
  <div class="delta-gap">
    <h4>Items found, not disclosed</h4>
    <p>{esc(delta.get("gap_summary", ""))}</p>
  </div>
</div>"""


def render_executive(text):
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Executive paragraph</div>
  <div class="exec-block">
    <h3>Executive summary</h3>
    <p class="pull">{esc(text)}</p>
  </div>
</div>"""


def render_coverage(rows):
    out = []
    for r in rows:
        status = r.get("status", "checked")
        if status == "checked":
            mark = f'<span class="check">✓ {esc(r.get("detail", ""))}</span>'
        else:
            mark = f'<span class="dash">— {esc(r.get("detail", "Not in scope"))}</span>'
        out.append(f'<div class="coverage-row"><span>{esc(r["category"])}</span>{mark}</div>')
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Coverage map</div>
  <div class="coverage-grid">
    {"".join(out)}
  </div>
</div>"""


def render_deal_headline(headline):
    """Project-level: factual severity summary line. Never a verdict.

    Expected shape:
      {"summary": "5 subjects reviewed at L3. 1 red, 4 yellow, 18 info.",
       "highest": "Highest-severity finding: SEC consent order on John Sponsor (2019, $1.2M, undisclosed). See below."}

    Both fields are plain factual strings. No "clean / material / blocker"
    inputs are accepted — the schema deliberately excludes them.
    """
    summary = headline.get("summary", "")
    highest = headline.get("highest", "")
    highest_block = f'<span class="highest">{esc(highest)}</span>' if highest else ""
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Deal-level severity summary</div>
  <div class="deal-headline">
    <h3>Deal-level severity</h3>
    <div class="summary">{esc(summary)}{highest_block}</div>
  </div>
</div>"""


def render_roster(subjects):
    """Project-level: subject-by-subject roster table.

    Flag counts use Intelligo's visual language: red pill (#E94E64 on white),
    yellow pill (#F0CE3F on dark), info badge (teal circular i + count).
    Pills are only rendered when count > 0 — zero-count flags are omitted.

    No judgement column — flag counts speak for themselves. Verdicts like
    'Clean / Material / Blocker' are the IC's call, not the skill's.
    """
    rows = []
    for s in subjects:
        flags = s.get("flags", {})
        red = int(flags.get("red", 0) or 0)
        yellow = int(flags.get("yellow", 0) or 0)
        info = int(flags.get("info", 0) or 0)

        pills = []
        if red > 0:
            pills.append(f'<span class="flag-pill r">{red}</span>')
        if yellow > 0:
            pills.append(f'<span class="flag-pill y">{yellow}</span>')
        if info > 0:
            pills.append(f'<span class="info-badge-pill"><span class="info-i">i</span>{info}</span>')
        # If a subject has no flags at all, show an em-dash so the row isn't empty.
        pill_html = "".join(pills) if pills else '<span style="color:#95A3B0;font-size:12px;">—</span>'

        rows.append(f"""
    <tr>
      <td><div class="name">{esc(s.get("name"))}</div><div class="role">{esc(s.get("role", ""))}</div></td>
      <td>L{esc(s.get("report_level", "?"))}</td>
      <td><div class="flag-pills">{pill_html}</div></td>
    </tr>""")
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Subject roster</div>
  <table class="roster-table">
    <thead><tr><th>Subject</th><th>Report</th><th>Flags</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</div>"""


def render_info_flags(items):
    """Detail view of analyst-elevated info findings.

    Matches Intelligo's native info-flag layout: circular teal 'i' badge to the
    left of each finding, with the explanation text, the titled item, and a
    meta line (role/date/source). Use only when the analyst has explicitly
    elevated an info finding for the IC — info flags are skipped by default.

    Schema:
      {"explanation": "Why this info flag was raised.",
       "title": "Item title (e.g. company, school, court name)",
       "meta": "Role · dates · duration · source"}
    """
    if not items:
        return ""
    lines = []
    for it in items:
        explain = (it.get("explanation") or "").strip()
        title = (it.get("title") or "").strip()
        meta = (it.get("meta") or "").strip()
        if not explain or not title:
            continue
        lines.append(f"""
  <div class="info-flag-line">
    <span class="info-icon">i</span>
    <div class="body">
      <p class="explain">{esc(explain)}</p>
      <p class="title-row">{esc(title)}</p>
      {f'<p class="meta">{esc(meta)}</p>' if meta else ''}
    </div>
  </div>""")
    if not lines:
        return ""
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Info findings (elevated by analyst)</div>
  {"".join(lines)}
</div>"""


def render_materials_list(items):
    """Project-level: red/yellow findings across all subjects, attributed.

    Each entry must include `summary` (the underlying finding text). Entries
    without summary are skipped — flag titles alone are too generic for an IC.
    """
    out = []
    for item in items:
        summary = (item.get("summary") or "").strip()
        if not summary:
            out.append("<!-- Skipped entry: missing finding text. Flag title alone is not enough. -->")
            continue
        sev = item.get("severity", "yellow").lower()
        out.append(f"""
    <div class="finding-item {sev}">
      <div class="subj">{esc(item.get("subject", ""))} · {sev.capitalize()} severity</div>
      <p class="ftitle">{esc(item.get("title"))}</p>
      <p class="fsum">{esc(summary)}</p>
    </div>""")
    return f"""
<div class="snippet">
  <button class="copy-btn" onclick="copyBlock(this)">Copy</button>
  <div class="snippet-label">Findings across the deal</div>
  <div class="findings-list">{"".join(out)}</div>
</div>"""


def render(spec):
    blocks = []
    scope = spec.get("scope", "subject")  # subject / project / hybrid

    # Project-level patterns (only emit when scope is project or hybrid)
    if scope in ("project", "hybrid"):
        if spec.get("deal_headline"):
            blocks.append(render_deal_headline(spec["deal_headline"]))
        if spec.get("subjects"):
            blocks.append(render_roster(spec["subjects"]))
        if spec.get("materials"):
            blocks.append(render_materials_list(spec["materials"]))

    # Subject-level patterns (always available; emitted for subject scope or hybrid deep-dive)
    patterns = spec.get("patterns", [])
    if not patterns:
        # Sensible defaults per scope
        patterns = (["executive", "counts", "headline", "delta", "coverage"]
                    if scope == "subject" else ["coverage"])

    if "executive" in patterns and spec.get("executive"):
        blocks.append(render_executive(spec["executive"]))
    if "counts" in patterns and spec.get("counts"):
        blocks.append(render_counts(spec["counts"]))
    if "headline" in patterns:
        for f in spec.get("headline_findings", []):
            blocks.append(render_headline(f))
    if "delta" in patterns and spec.get("delta"):
        blocks.append(render_delta(spec["delta"]))
    if "info_flags" in patterns and spec.get("info_flags"):
        blocks.append(render_info_flags(spec["info_flags"]))
    if "coverage" in patterns and spec.get("coverage"):
        blocks.append(render_coverage(spec["coverage"]))

    # Header varies by scope
    if scope in ("project", "hybrid"):
        title = f"IC Snippets — {esc(spec.get('project_name', 'Deal'))}"
        subtitle = (f"{esc(spec.get('deal_type', ''))} · {esc(len(spec.get('subjects', [])))} subjects · "
                    f"Prepared by {esc(spec.get('prepared_by', ''))} · For {esc(spec.get('prepared_for', ''))}")
    else:
        subj = esc(spec.get("subject_name", ""))
        ent = f" / {esc(spec['subject_entity'])}" if spec.get("subject_entity") else ""
        title = f"IC Snippets — {subj}{ent}"
        subtitle = (f"Intelligo {esc(spec.get('report_level', ''))} · {esc(spec.get('report_date', ''))} · "
                    f"Prepared by {esc(spec.get('prepared_by', ''))} · For {esc(spec.get('prepared_for', ''))}")

    header = f"""
<div class="page-header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
<div class="instructions">
  Each block below is styled and ready to paste into PowerPoint, Google Slides, Word, or Notion. Click <strong>Copy</strong>, then paste into your slide — the formatting will be preserved.
</div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>{FILE_CSS}</style></head>
<body>
{header}
{"".join(blocks)}
<script>{COPY_SCRIPT}</script>
</body></html>"""


def render_for_widget(spec):
    """Render content suitable for the Cowork show_widget tool.

    Returns the inner content only — no DOCTYPE/html/head/body wrapper.
    Wrapped in a single .intelligo-snippet-root container so all styles are
    scoped (won't leak into the chat).
    scoped and won't bleed into the surrounding chat. Background is
    transparent and there's no top-level padding, per show_widget guidance.

    Use this when rendering the snippets inline in chat as a canvas. Use
    render() instead when producing a standalone .html file for download.
    """
    blocks = []
    scope = spec.get("scope", "subject")

    if scope in ("project", "hybrid"):
        if spec.get("deal_headline"):
            blocks.append(render_deal_headline(spec["deal_headline"]))
        if spec.get("subjects"):
            blocks.append(render_roster(spec["subjects"]))
        if spec.get("materials"):
            blocks.append(render_materials_list(spec["materials"]))

    patterns = spec.get("patterns", [])
    if not patterns:
        patterns = (["executive", "counts", "headline", "delta", "coverage"]
                    if scope == "subject" else ["coverage"])

    if "executive" in patterns and spec.get("executive"):
        blocks.append(render_executive(spec["executive"]))
    if "counts" in patterns and spec.get("counts"):
        blocks.append(render_counts(spec["counts"]))
    if "headline" in patterns:
        for f in spec.get("headline_findings", []):
            blocks.append(render_headline(f))
    if "delta" in patterns and spec.get("delta"):
        blocks.append(render_delta(spec["delta"]))
    if "info_flags" in patterns and spec.get("info_flags"):
        blocks.append(render_info_flags(spec["info_flags"]))
    if "coverage" in patterns and spec.get("coverage"):
        blocks.append(render_coverage(spec["coverage"]))

    if scope in ("project", "hybrid"):
        title = f"IC Snippets — {esc(spec.get('project_name', 'Deal'))}"
        subtitle = (f"{esc(spec.get('deal_type', ''))} · {esc(len(spec.get('subjects', [])))} subjects · "
                    f"Prepared by {esc(spec.get('prepared_by', ''))} · For {esc(spec.get('prepared_for', ''))}")
    else:
        subj = esc(spec.get("subject_name", ""))
        ent = f" / {esc(spec['subject_entity'])}" if spec.get("subject_entity") else ""
        title = f"IC Snippets — {subj}{ent}"
        subtitle = (f"Intelligo {esc(spec.get('report_level', ''))} · {esc(spec.get('report_date', ''))} · "
                    f"Prepared by {esc(spec.get('prepared_by', ''))} · For {esc(spec.get('prepared_for', ''))}")

    header = f"""
<div class="page-header">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>"""

    return f"""<style>{WIDGET_CSS}</style>
<div class="intelligo-snippet-root">
{header}
{"".join(blocks)}
</div>
<script>{COPY_SCRIPT}</script>"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) < 2:
        print("Usage: generate_snippets.py [--widget] findings.json output.html",
              file=sys.stderr)
        print("  --widget  Emit widget-mode content (for show_widget tool) instead of a full HTML document.",
              file=sys.stderr)
        sys.exit(1)
    spec = json.loads(Path(args[0]).read_text())
    out = render_for_widget(spec) if "--widget" in flags else render(spec)
    Path(args[1]).write_text(out)
    print(f"Wrote {args[1]}{' (widget mode)' if '--widget' in flags else ''}")


if __name__ == "__main__":
    main()
