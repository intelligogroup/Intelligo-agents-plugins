---
name: intelligo-export-pdf
description: >
  Guided PDF export from Intelligo — walks the user through scope and content options before calling exportPdf. 
  Trigger whenever the user wants to download, export, or get a PDF of a report or project in Intelligo, 
  or says things like "download this report", "export to PDF", "get me the PDF for this project", 
  "download all profiles", "export the report for [name]", or anything implying they want a PDF out of Intelligo.
  Always use this skill instead of calling exportPdf directly — it ensures the right scope and options are chosen first.
---

# Intelligo PDF Export — Guided Flow

Your job is to guide the user to a correctly configured `exportPdf` call by asking focused, sequential questions. Don't overwhelm them — ask one topic at a time, in order.

---

## Step 1 — Determine the starting point

Figure out whether the user is starting from a **profile** or a **project**. This is usually clear from context (what they mentioned, what's on screen, prior conversation). If it's ambiguous, ask: "Are you starting from a specific profile, or from a project?"

---

## Step 2 — Scope selection

The scope question differs based on the starting point.

### If starting from a profile:

**Default assumption: export just this profile.** Do NOT ask about the whole project unless the user has explicitly indicated they want multiple reports (e.g., "all reports in this project", "export everything", "download all profiles").

- **Single profile (default)** → pass `profileIds: [<this profile's id>]`. Skip to Step 3.
- **Multiple profiles from the same project (only if user explicitly asked)** → treat this as a project-level export. Resolve the `projectId`, then go to Step 2b.

### If starting from a project:

Ask: "Do you want all profiles in the project, or just one specific profile?"

- **All profiles** → you'll use `projectId`. Then ask the format question (Step 2b).
- **A specific profile** → ask which one (name or ID), resolve to `profileIds: [<id>]`. Skip to Step 3.

### Step 2b — Format (project-level exports only)

When exporting a whole project, ask:
"Do you want all profiles merged into **one PDF**, or as **separate PDFs in a zip**?"

- One PDF → `exportMode: SINGLE_PDF`
- Separate files → `exportMode: MULTI_PDF`

---

## Step 3 — Content flags

Always show the user all options with their defaults and ask them to confirm or change before exporting. Never silently apply defaults.

The defaults differ depending on the export scope:

**Single profile export:**
> Here are the export options — these match the Intelligo defaults. Let me know if you want to change anything:
> - ✅ **Include user comments** (on)
> - ✅ **Include links to view report in Intelligo** (on)
> - ✅ **Include links to original sources** (on)
> - ☐ **Include flag review statuses / action items** (off)
> - ☐ **Include historical versions of the reports** (off)

**Project-level export:**
> Here are the export options — these match the Intelligo defaults. Let me know if you want to change anything:
> - ✅ **Include user comments** (on)
> - ☐ **Include links to view report in Intelligo** (off)
> - ✅ **Include links to original sources** (on)
> - ☐ **Include flag review statuses / action items** (off)
> - ☐ **Include historical versions of the reports** (off)

Wait for the user to confirm or adjust. Map their answer to the five flags:
- `includeComments`
- `includeLinks`
- `includeSources`
- `includeActionItems`
- `includeAllVersions`

---

## Step 4 — Storage preference

Before calling the export, ask:

> Once the PDF is ready, would you like to:
> - **Just get a download link** (expires in ~30 minutes)
> - **Save it somewhere** — e.g., Google Drive, email it, upload to Slack

If they want to save it somewhere, note the destination so you can act on it after the export completes. If they just want the link, proceed.

---

## Step 5 — Confirm and export

Before calling the tool, give a one-line summary:

> Exporting [scope description] as [format] with [flags or "default settings"]. Calling export now…

Then call `exportPdf` with the resolved parameters.

---

## Step 6 — Surface the result

The tool returns a `downloadUrl` (presigned, valid ~30 minutes).

- **If the user just wants a link**, present it clearly:
  > Your export is ready: **[Download PDF / Download ZIP]** _(link expires in ~30 minutes)_

- **If the user wants to save it somewhere**, download the file from the URL and then use the appropriate tool to store or send it (e.g., upload to Google Drive, attach to an email, send via Slack). Confirm once done.

If the export is a zip (multiple profiles or MULTI_PDF), note that.

---

## Tips

- You often already know the profile ID or project ID from earlier in the conversation — use that context and skip asking for it.
- If the user says something like "download the whole thing" from a project context, that's MULTI or SINGLE — ask which format they prefer.
- Keep the flow brisk. The goal is 2-3 quick exchanges before calling the tool, not an interrogation.
