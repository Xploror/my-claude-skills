---
name: "profile-manager"
description: "Audits a LinkedIn profile against its owner's goals and produces a downloadable report: positive/negative tables, justified priorities, a gradual two-week action timeline, and (only if a post is planned) post recommendations. Use when asked to review, audit, improve or optimise a LinkedIn profile for visibility to recruiters, researchers or collaborators, or to plan what to post on LinkedIn. Read-only: it never edits the profile or posts anything."
allowed-tools: Read, Glob, Grep
---

# LinkedIn Profile Manager

Audit a LinkedIn profile and produce an action plan that maximises its engagement and visibility to the people its owner wants to reach (recruiters, researchers, potential collaborators). Written for any profile owner - nothing here is tied to a specific person.

## Hard rules (read-only, human in the loop)

- **Read only.** Never edit the profile, never post, schedule, comment, connect or message anyone. Everything you produce is a recommendation or a draft for the owner to act on.
- If a LinkedIn (or other social) connector or tool is available, use it only to *read* the profile, and only if the user asks. Any action beyond reading needs the user's explicit approval for that specific action, every time - a general "go ahead" is not approval to post.
- Never invent profile content, achievements or metrics. Recommendations may suggest what to add; they must not claim things the owner hasn't told you are true.

## Inputs

1. **The profile.** Best: a LinkedIn "Save to PDF" export of the profile. Also fine: pasted profile text, or a profile file in the uploaded files, project files or working directory - look there first.
2. **The owner's context:** current status (e.g. student, job seeker, researcher), goals and priorities (target roles, fields, audience), and any supporting documents (resume, CV, goals notes) in the same places.

If either is missing, ask for everything missing in **one** question. Don't start the audit without the profile.

## Process

1. **Extract once.** Pull every section of the current profile - headline, about/summary, experience, projects, publications, volunteering, featured, skills, education, certifications, recommendations - into a compact structured summary. Work from that summary from here on rather than re-reading the raw export.
2. **Define the yardstick.** From the owner's context, write down in a few lines what "good" means for this profile (who must find it, what they should conclude). Every judgement below is measured against this.
3. **Write the report** with the sections below, in order.

## Report sections

### 1. Positive / Negative points
Two separate, comprehensive tables: one for positive aspects, one for negative aspects. Each row: the aspect, the profile section it's in, and why it helps or hurts *against the yardstick from step 2* (the owner's characteristics, current status and priorities).

### 2. Priorities
JUSTIFIED priorities derived from the TODOs found in section 1. Point-wise, ordered by impact, with a one-line justification each.

### 3. Next Steps
Coherent with the previous sections. A professional timeline of milestones for the **next 2 weeks**, e.g. "update the Experience entry for X - tomorrow", "add project Y - day 3", "publish a post about Z - next week", "add a missing skill". Pace: gradual - a few manageable actions per week, not everything on day one. JUSTIFY every step.

Present it as a flowchart/timeline visual. If the `flowchart-designer` skill is available, follow its visual style rules; otherwise use a clean, white-background timeline or a table (Day / Action / Section / Why).

### 4. Post recommendations (only if applicable)
Include this section **only if** Next Steps contains a scheduled post. Give a few recommendations for that post (topic, angle, format, hook, hashtags/mentions, timing) and JUSTIFY each. These are drafts for the owner to publish themselves - see the hard rules.

## Output

- Deliver the report as a **downloadable PDF**. Use a PDF skill if one is available, or a local library (e.g. `reportlab`, `weasyprint`) if code execution is available.
- If no PDF route exists in this environment, deliver an HTML or Markdown file instead and say why, so the owner can print it to PDF.
- In chat, give only a short summary (top 3 priorities and the first step), not the whole report.
