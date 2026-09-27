---
name: "your-resume-cl-creator"
description: Builds ATS-tailored resumes and one-page cover letters for a specific job application, following a fixed format standard (mandatory Summary section, fixed four-paragraph cover-letter structure, exact header/address/salutation formatting, and a specific confident tone). Fully generic and anonymous — works for any applicant in any field; every identity detail (name, contact info, education, experience) is supplied fresh per use, never assumed or reused from a prior application. Always use this skill whenever the user asks to build, generate, update, or tailor a resume, CV, or cover letter for a job, company, or role — including as part of a "crack it" job-application workflow, a bare "cover letter" request, or "force crack it" — even if they don't say "use the skill" or name it explicitly. This is the required format for every resume/cover-letter output; do not fall back to ad-hoc formatting.
---

# Resume & Cover Letter Creator

This skill packages a fixed resume and cover letter format so every application looks consistent, no matter which job or which applicant it's for. **Nothing in this skill is tied to a specific person.** Every name, phone number, email, address, school, employer, job title, and achievement referenced anywhere in this skill's files is a bracketed placeholder or a generic pattern description — never real personal data. When you use this skill, you supply one specific applicant's real details fresh, every time; never carry over a name, contact detail, or achievement from a previous use of this skill into a new one.

## Before you start

You need three things before building anything:
1. **The job description** — title, company, location, and ideally the exact responsibility/skill keywords from the posting (for ATS keyword matching).
2. **This applicant's real source material** — their actual resume/CV content, or whatever background they've given you (work history, projects, education, skills), to draw truthful bullets from. Never invent experience, metrics, schools, or skills that aren't in their real source material — tailoring means re-emphasizing and rephrasing what's true for *this* applicant, not fabricating a better fit, and never means reusing another applicant's background.
3. **The company's mailing address** and, where findable, a recruiter/hiring-manager contact — the cover letter needs a real address, not a placeholder.

If the resume needs docx output, use `scripts/docx_helpers.js` (Node, requires the `docx` package) rather than hand-rolling formatting — it already implements every rule below correctly, and it will refuse to run if you forget to supply the applicant's real name/contact details (see "Using the script" below), so it can't silently produce a document with missing or wrong identity info.

## Resume format

Exactly these sections, **in this order**:

1. **Header** — full name, phone, email, and LinkedIn | GitHub | Personal Website as hyperlinks (not plain text URLs).
2. **Summary** — 2–3 sentences immediately after the header, before Education. Rewrite this per application — it should reflect the specific role's keywords and angle, not be a generic one-liner reused everywhere.
3. **Education**
4. **Experience**
5. **Projects**
6. **Technical Skills**

Everything else — publications, certifications, awards, leadership — is optional. Include it only when it strengthens this specific application; a resume is complete without it.

Reference format/style (bullet density, date-right-aligned header rows, degree/company line formatting): see `references/example-resume-format.md` — a fully placeholder-based template, not any real person's resume. The Summary section is the one addition on top of a typical resume's structure — many applicants' existing resumes won't already have one, but every resume built through this skill must add it. If you're hand-rolling a resume without the script (rare — prefer the script), keep the date/location column genuinely flush against the page's right margin, not just roughly right-of-center; `scripts/docx_helpers.js` computes this correctly from the document's real margins, so lean on it rather than approximating.

## Cover letter format

**Exactly four body paragraphs**, in this order — no more, no fewer:

1. **Intro** — name the role and company, and why this specific opportunity is exciting (not generic enthusiasm — tie it to something real about the company/mission).
2. **Expertise** — the evidence paragraph: specific projects, quantified outcomes, tools, direct mapping to the JD's language.
3. **Application** — how that expertise translates into value for *this particular role*. Don't just repeat paragraph 2's achievements; connect them explicitly to the responsibilities in the posting.
4. **Closing** — brief, confident, inviting a conversation.

**Header block, top to bottom, in this exact order:**
1. Name (bold)
2. Phone | Email
3. LinkedIn | Github | Personal Website — as hyperlinks, placed here near the top (not at the bottom of the letter).
4. Date
5. "Hiring Team" + company name + full mailing address (always address it to "Hiring Team" — never guess an individual's name unless the user has explicitly supplied one)
6. **"Re: Application for `<Position Title>`" — always bold.**
7. "Dear Hiring Team," salutation

One page. Tone: motivated, confident, high-spirited — see the Tone section below for exactly what that means in practice, since "confident" is easy to overdo into generic hype.

## Tone & sentence structure

Generic AI cover letters read stiff because they chop everything into short declarative sentences and list achievements like a resume in prose form. Avoid that. The template in `references/example-cover-letter.md` (placeholder-based, not any real person's letter) shows the target register:

- **Chain clauses with commas into one confident sentence** rather than breaking into three short ones — connect "what the role involves" → "why that work matters" → "why it's exactly this applicant's path" as one flowing thought, not a checklist.
- **Lead the expertise paragraph with a distinguishing claim, then back it with evidence** — a "what sets me apart" contrast beat before the supporting facts, not just a list of things done.
- **Warm, direct sign-off** that invites a conversation without repeating earlier content.
- Write in prose, not bullet-like sentence fragments strung together with periods.

Read the full reference file before writing a cover letter if the tone isn't clicking — it's short and worth matching closely rather than approximating from memory. Fill in this applicant's real, specific achievements where the template has placeholders — the pattern is reusable across any field or industry, the content never is.

## Using the script

`scripts/docx_helpers.js` exports two functions for Node + the `docx` npm package (already installed in this environment — `require("docx")` directly, don't `npm install` first). **Neither function has any default identity values — every identity field is required and must be this specific applicant's real information**; both throw a clear error if you omit one, so a resume or cover letter can never accidentally go out with placeholder or stale contact info still in it.

- `buildResume({ filename, name, phone, email, linkedin, github, website, summary, education, experience, experienceSectionTitle, projects, skills, publications, extraSections })` — `name`/`phone`/`email`/`linkedin`/`github`/`website` are this applicant's real details (all required); `summary` is a string (2-3 sentences, required); `education` is an array of `{ school, location, line, dates }`; `experienceSectionTitle` is an optional override for the Experience heading (e.g. "Relevant Experience — <domain>"); `experience` is an array of `{ title, dates, org, location, bullets }`; `projects` is `{ sectionTitle, items }`; `skills` is an array of `{ label, value }`; `publications` is an array of strings (optional, omit or pass `[]`); `extraSections` is an array of `{ title, items }` for any other optional section.
- `buildCoverLetter({ filename, name, phone, email, linkedin, github, website, date, companyLines, positionTitle, paragraphs })` — identity fields as above, now including `github` (all required — the cover letter header carries the same LinkedIn | GitHub | Personal Website links as the resume); `companyLines` is an array of address lines, e.g. `["Hiring Team", "Company Name", "Street", "City, State ZIP, Country"]` (first line rendered bold); `positionTitle` is the role title — the bold "Re: Application for `<positionTitle>`" line and the "Dear Hiring Team," salutation are both generated automatically, so don't pass them separately; `paragraphs` must be an array of exactly 4 strings, in intro/expertise/application/closing order.

Both write a `.docx` directly. After generating, render to PDF/JPG and look at it before delivering — see the docx skill's verification step (`soffice.py --convert-to pdf`, then `pdftoppm`) — to catch page overflow or broken hyperlinks before sending the file.

## Checklist before delivering

- [ ] Every identity field (name, phone, email, LinkedIn, GitHub, website, address) belongs to THIS applicant — nothing left over from a placeholder or a different person
- [ ] Resume: Summary section present, right after the header, tailored to this role
- [ ] Resume: section order is Header → Summary → Education → Experience → Projects → Technical Skills (+ optional extras after)
- [ ] Resume: LinkedIn, GitHub, Website all hyperlinked in the header
- [ ] Cover letter: LinkedIn, GitHub, and Website all hyperlinked near the top of the header block (same three links as the resume)
- [ ] Cover letter: "Re: Application for..." line is bold
- [ ] Cover letter: addressed "Dear Hiring Team,"
- [ ] Cover letter: exactly 4 body paragraphs in the intro/expertise/application/closing order
- [ ] Cover letter: one page
- [ ] Tone matches `references/example-cover-letter.md` — flowing sentences, not staccato bullet-prose
- [ ] Nothing fabricated — every claim traces back to this applicant's real source material
