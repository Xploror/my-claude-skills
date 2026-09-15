---
name: job-tracker
description: Updates the user's job-search tracking files -- "List_of_targets" (companies being watched) and "Applied_list" (company - job title, tagged rejected/interview when applicable) -- whenever the user reports applying to a role, getting rejected, landing an interview, or just wants a company added to their watch list. Trigger this any time the user says things like "I applied to X for Y", "add X to my applied list", "mark X as rejected/interview", "I got an interview with X", "I got rejected from X", or gives just a bare company name to add/check. Handles correct "Company - Job Title (status)" formatting, avoids duplicate entries by updating status in place, and appends new companies to the target list automatically when they're missing.
---

# Job Tracker

Keeps two plain-text project files in sync with the user's real-world job search:

- **List_of_targets** -- one company name per line. The watch list.
- **Applied_list** -- one line per application, format `Company - Job Title` or
  `Company - Job Title (rejected)` or `Company - Job Title (interview)`. No tag
  means "applied, no outcome yet."

All the actual matching/formatting logic lives in `scripts/update_tracker.py`
so results are deterministic -- don't hand-edit the files yourself, always
go through the script.

## Step 1: Work out what the user is telling you

From the user's message, extract:

| Field | Required? | Notes |
|---|---|---|
| `company` | always | Use their capitalization/naming as given. |
| `title` | only if they mention a role | If they gave **only a company name**, leave this out entirely -- see "Company-only mode" below. |
| `status` | only if implied | Map their language to exactly `rejected` or `interview`. "Got rejected", "didn't move forward", "rejected" -> `rejected`. "Got an interview", "phone screen scheduled", "moving to interview" -> `interview`. If they just say "I applied to X for Y" with no outcome yet, leave status unset -- do not guess. |

If the user's message is genuinely ambiguous about which company or role they
mean (e.g., they've applied to the same company for multiple roles and it's
unclear which one just got the update), ask a single clarifying question
before running the script rather than guessing.

## Step 2: Locate the source files

These are normally Claude Project knowledge files mounted read-only, e.g.
`/mnt/project/List_of_targets` and `/mnt/project/Applied_list`. Locate them
(check the project files list / uploaded files for the current conversation).
If you can't find them, ask the user to point you to them or paste their
current contents.

## Step 3: Run the script

```bash
python3 scripts/update_tracker.py \
  --targets "/mnt/project/List_of_targets" \
  --applied "/mnt/project/Applied_list" \
  --out-dir "/home/claude/tracker_update" \
  --company "Skydio" \
  --title "Autonomy Engineer" \
  --status interview
```

- **Company-only mode**: omit `--title` entirely (and therefore `--status`).
  The script will only touch `List_of_targets` and leave `Applied_list`
  completely alone.
- **Applied with no outcome yet**: give `--company` and `--title`, omit
  `--status`.
- **Rejected / interview**: give all three flags.
- The script never edits the input files in place -- it always writes fresh
  copies to `--out-dir`. This is safe to run even though the source files
  under `/mnt/project/` are typically read-only.
- The script already handles: not creating a duplicate target-list entry,
  not creating a duplicate Applied_list line for the same company + title
  (it updates the status on the existing line instead), and matching
  "Company (suffix)" style target entries like "Dracoe (HQ)".

## Step 4: Report back and hand off the files

1. Read the script's printed summary and relay it to the user in plain
   language -- what got added, what got updated, what was already there.
2. Use your file-presentation tool to surface the two updated files from
   `--out-dir`.
3. **Always remind the user of this**: Project knowledge files are read-only
   copies. These updated files need to replace the old ones in their Project
   (delete the old `List_of_targets` / `Applied_list` from Project knowledge,
   upload the new ones) for the change to actually persist -- running this
   skill does not silently update the Project on its own.

## Edge cases

- **Company not found, only a company name given**: append it to
  `List_of_targets`, say so plainly, don't touch `Applied_list`.
- **Company + title already exists in Applied_list with a different or no
  status**: the script updates that line's status in place rather than
  adding a second line for the same role. Point this out in your summary
  (e.g. "moved Skydio - Autonomy Engineer from no tag to (interview)").
- **User gives a status word that isn't "rejected" or "interview"** (e.g.
  "ghosted", "withdrew", "offer"): ask them whether it should map to one of
  the two supported tags, or be left untagged, rather than inventing a new
  tag style the rest of the file doesn't use.
- **Multiple roles at the same company in one message**: run the script
  once per role.
