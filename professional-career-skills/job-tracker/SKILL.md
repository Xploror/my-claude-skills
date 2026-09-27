---
name: job-tracker
description: Maintains two plain-text job-search tracking files -- a company watch list (one company per line) and an applications log (one "Company - Job Title (status)" line per application, status rejected/interview or none). Use whenever someone reports applying to a role, getting rejected, landing an interview, or wants a company added to or checked against their watch list -- e.g. "I applied to X for Y", "mark X as rejected", "I got an interview with X", "add X to my targets". Updates status in place, never duplicates entries, and never erases a recorded outcome.
---

# Job Tracker

Keeps two plain-text files in sync with someone's real-world job search:

- **Targets file** (default name `List_of_targets`) -- one company name per
  line. The watch list.
- **Applications file** (default name `Applied_list`) -- one line per
  application, format `Company - Job Title`, `Company - Job Title (rejected)`
  or `Company - Job Title (interview)`. No tag means "applied, no outcome yet."

All matching/formatting logic lives in `scripts/update_tracker.py` in this
skill's folder so results are deterministic -- don't hand-edit the files
yourself, always go through the script. It needs only Python 3's standard
library (`python3` on macOS/Linux; `python` or `py` on Windows).

## Inputs

1. **The two files.** The names can be anything -- use whatever the user
   has. They may come from uploaded files, a project's knowledge files, the
   current working directory, or text the user pastes. Look for them first;
   if you can't find them, ask once where they are or to paste them.
   - Pasted text: write it to two files in a scratch/output folder first,
     then run the script on those.
   - The user has no files yet: run with `--init` to start from empty ones.
2. **The event**, extracted from the user's message:

| Field | Required? | Notes |
|---|---|---|
| `company` | always | Use their capitalization/naming as given. |
| `title` | only if they mention a role | If they gave **only a company name**, leave this out entirely -- see "Company-only mode" below. |
| `status` | only if implied | Map their language to exactly `rejected` or `interview`. "Got rejected", "didn't move forward" -> `rejected`. "Got an interview", "phone screen scheduled" -> `interview`. If they just say "I applied to X for Y", leave status unset -- do not guess. |

If the message is genuinely ambiguous about which company or role they
mean (e.g., several roles at the same company and it's unclear which one
got the update), ask a single clarifying question before running the
script rather than guessing.

## Run the script

```bash
python3 <this-skill-folder>/scripts/update_tracker.py \
  --targets "<path to targets file>" \
  --applied "<path to applications file>" \
  --out-dir "<any writable output folder>" \
  --company "Skydio" \
  --title "Autonomy Engineer" \
  --status interview
```

- **Company-only mode**: omit `--title` (and therefore `--status`). Only the
  targets file can change; the applications file is left alone.
- **Applied, no outcome yet**: give `--company` and `--title`, omit
  `--status`. If that role is already logged, its existing status is
  **kept** -- re-reporting an application never erases an outcome.
- **Rejected / interview**: give all three flags. `--status` is
  case-insensitive.
- **Remove a status on purpose** (the user says the tag was a mistake):
  `--clear-status` instead of `--status`.
- **No files yet**: add `--init`; missing input files are treated as empty.
- The script never edits its inputs -- it writes fresh copies (same file
  names) to `--out-dir`. It keeps each file's line endings (CRLF stays CRLF)
  and exits with code 2 and a one-line error on bad input or a missing file.
- It already handles: no duplicate target entries, no duplicate application
  line for the same company + title (the status is updated in place),
  "Company (suffix)" target entries like "Dracoe (HQ)", and company names
  that themselves contain " - ".

## Report back and hand off

1. Relay the script's printed summary in plain language -- what got added,
   what got updated, what was already there.
2. Deliver the result the way that fits where the files came from:
   - **Read-only source** (e.g. project knowledge files): hand back the two
     updated files and **always remind the user** that the originals are
     read-only copies -- they must replace the old files themselves for the
     change to persist.
   - **Writable source** (e.g. files in the working directory): show the
     before -> after lines and **ask before overwriting** the originals with
     the copies from `--out-dir`. Never overwrite without a yes.
   - **Pasted text**: reply with the full updated contents of both files.

## Edge cases

- **Company not found, only a company name given**: it's appended to the
  targets file; say so plainly. The applications file is untouched.
- **Company + title already logged with a different status**: the line's
  tag is replaced in place, not duplicated. Point this out (e.g. "moved
  Skydio - Autonomy Engineer from (rejected) to (interview)").
- **Company + title already logged, no new status given**: nothing changes;
  say the entry was already there and what its status is.
- **A status word that isn't "rejected" or "interview"** (e.g. "ghosted",
  "withdrew", "offer"): ask whether it should map to one of the two
  supported tags or be left untagged, rather than inventing a new tag.
- **Multiple roles or companies in one message**: run the script once per
  role, feeding each run's output files into the next run.
