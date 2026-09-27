#!/usr/bin/env python3
"""
update_tracker.py

Deterministically updates two plain-text job-search tracking files -- a
company watch list (default name "List_of_targets") and an applications log
(default name "Applied_list") -- based on a single job-application event.
Never mutates the input files in place -- always writes fresh copies to
--out-dir so the originals (which may be read-only) are left untouched.
Standard library only; runs on Windows, macOS and Linux.

Usage:
    python3 update_tracker.py \
        --targets /path/to/List_of_targets \
        --applied /path/to/Applied_list \
        --out-dir /path/to/output \
        --company "Skydio" \
        [--title "Autonomy Engineer"] \
        [--status rejected|interview | --clear-status] \
        [--init]

Behavior:
  - Company only (no --title given):
        Ensures `company` exists in the targets file (case-insensitive
        match; also matches "Company (suffix)" style entries like
        "Dracoe (HQ)"). Appends it to the end of the targets file if it
        was missing. Applied_list is left completely untouched.
        --status / --clear-status are rejected in this mode.

  - Company + title:
        1. Ensures `company` exists in the targets file (append if missing),
           same as above.
        2. Looks for an existing "Company - Title" line in Applied_list
           (case-insensitive match on both company and title, ignoring any
           existing "(status)" tag on that line; company names may
           themselves contain " - ").
             - If found: --status replaces the tag, --clear-status removes
               it, and giving neither KEEPS the existing tag (re-reporting
               an application never erases its outcome).
             - If not found: appends a new "Company - Title (status)" line
               (or "Company - Title" with no parens if no status given) to
               the end of Applied_list, matching the file's existing style.

  - --init: treat a missing --targets / --applied file as empty instead of
    failing, so a first-time user can start from nothing.

  - Line endings: if an input file uses CRLF, the output copy does too.

Prints a short human-readable summary of exactly what changed (or didn't)
so the calling model can relay it to the user before they replace their
real files with the output. Exits 2 on usage/input errors.
"""
import argparse
import os
import re
import sys

VALID_STATUSES = {"rejected", "interview"}
TAG_RE = re.compile(r"\s*\(([^)]*)\)\s*$")


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def read_lines(path: str, init: bool):
    """Return (lines, newline) for `path`; newline is "\\r\\n" or "\\n"."""
    if not os.path.exists(path):
        if init:
            return [], "\n"
        fail(f"file not found: {path!r} (pass --init to start a new, empty file)")
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.splitlines(), newline


def write_lines(path: str, lines: list, newline: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(newline.join(lines) + newline if lines else "")


def strip_trailing_blanks(lines: list) -> list:
    while lines and lines[-1].strip() == "":
        lines.pop()
    return lines


def company_in_targets(company: str, target_lines: list) -> bool:
    norm_company = normalize(company)
    for line in target_lines:
        norm_line = normalize(line)
        if not norm_line:
            continue
        if norm_line == norm_company:
            return True
        # Handles entries like "Dracoe (HQ)" matching company="Dracoe"
        if norm_line.startswith(norm_company + " ("):
            return True
    return False


def split_tag(text: str):
    """Split 'Title (status)' into ('Title', 'status'); no tag -> (text, None)."""
    m = TAG_RE.search(text)
    if not m:
        return text.strip(), None
    return text[: m.start()].strip(), m.group(1).strip()


def find_applied_entry(company: str, title: str, applied_lines: list):
    """Return (index, existing_status) of a matching 'Company - Title (...)' line, or (None, None).

    Matches on the known company prefix rather than splitting on the first
    " - ", so company names that themselves contain " - " still match.
    """
    prefix = normalize(company) + " - "
    norm_title = normalize(title)
    for i, line in enumerate(applied_lines):
        norm_line = normalize(line)
        if not norm_line.startswith(prefix):
            continue
        line_title, line_status = split_tag(norm_line[len(prefix):])
        if line_title == norm_title:
            return i, line_status
    return None, None


def format_entry(company: str, title: str, status) -> str:
    base = f"{company} - {title}"
    if status:
        base += f" ({status})"
    return base


def main():
    parser = argparse.ArgumentParser(description="Update job-search tracker files.")
    parser.add_argument("--targets", required=True, help="Path to the watch-list file (e.g. List_of_targets)")
    parser.add_argument("--applied", required=True, help="Path to the applications file (e.g. Applied_list)")
    parser.add_argument("--out-dir", required=True, help="Directory to write updated files")
    parser.add_argument("--company", required=True, help="Company name, as it should appear")
    parser.add_argument("--title", default=None, help="Job title (omit for a target-list-only check)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", default=None, help="rejected | interview (case-insensitive)")
    group.add_argument("--clear-status", action="store_true", help="Remove an existing status tag")
    parser.add_argument("--init", action="store_true", help="Treat missing input files as empty")
    args = parser.parse_args()

    company = args.company.strip()
    title = args.title.strip() if args.title else None
    status = args.status.strip().lower() if args.status is not None else None

    if not company:
        fail("--company must not be empty")
    if status is not None and status not in VALID_STATUSES:
        fail(f"--status must be one of {sorted(VALID_STATUSES)}, got: {args.status!r}")
    if (status is not None or args.clear_status) and not title:
        fail("--status/--clear-status need --title (a status belongs to a specific application)")

    target_lines, targets_nl = read_lines(args.targets, args.init)
    applied_lines, applied_nl = read_lines(args.applied, args.init)
    summary = []

    # Step 1: ensure the company exists in the targets list, in every mode.
    if not company_in_targets(company, target_lines):
        strip_trailing_blanks(target_lines)
        target_lines.append(company)
        summary.append(f'Added "{company}" to the targets list (was missing).')
    else:
        summary.append(f'"{company}" already present in the targets list -- no change.')

    # Step 2: only touch the applications file if a job title was actually given.
    if title:
        idx, existing_status = find_applied_entry(company, title, applied_lines)
        if args.clear_status:
            new_status = None
        elif status is not None:
            new_status = status
        else:
            new_status = existing_status  # re-report: keep whatever outcome is recorded
        if idx is not None:
            old_line = applied_lines[idx]
            # Keep the line's own spelling/capitalization; only the tag changes.
            base, _ = split_tag(old_line)
            new_line = f"{base} ({new_status})" if new_status else base
            applied_lines[idx] = new_line
            if old_line != new_line:
                summary.append(f'Updated applications entry:\n    "{old_line}"\n    -> "{new_line}"')
            else:
                summary.append(f'Applications entry already up to date: "{new_line}"')
        else:
            new_line = format_entry(company, title, new_status)
            strip_trailing_blanks(applied_lines)
            applied_lines.append(new_line)
            summary.append(f'Added new applications entry: "{new_line}"')
    else:
        summary.append("No job title given -- applications file left untouched (target-list check only).")

    os.makedirs(args.out_dir, exist_ok=True)
    out_targets = os.path.join(args.out_dir, os.path.basename(args.targets))
    out_applied = os.path.join(args.out_dir, os.path.basename(args.applied))
    if os.path.abspath(out_targets) == os.path.abspath(out_applied):
        fail("--targets and --applied must have different file names")
    write_lines(out_targets, target_lines, targets_nl)
    write_lines(out_applied, applied_lines, applied_nl)

    print("\n".join(summary))
    print(f"\nUpdated files written to: {args.out_dir}")


if __name__ == "__main__":
    main()
