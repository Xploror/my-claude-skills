#!/usr/bin/env python3
"""
update_tracker.py

Deterministically updates the "List_of_targets" and "Applied_list" job-search
tracking files based on a single job-application event. Never mutates the
input files in place -- always writes fresh copies to --out-dir so the
originals (which may be read-only project files) are left untouched.

Usage:
    python update_tracker.py \
        --targets /path/to/List_of_targets \
        --applied /path/to/Applied_list \
        --out-dir /path/to/output \
        --company "Skydio" \
        [--title "Autonomy Engineer"] \
        [--status rejected|interview]

Behavior:
  - Company only (no --title given):
        Ensures `company` exists in the targets file (case-insensitive
        match; also matches "Company (suffix)" style entries like
        "Dracoe (HQ)"). Appends it to the end of the targets file if it
        was missing. Applied_list is left completely untouched.

  - Company + title (status optional):
        1. Ensures `company` exists in the targets file (append if missing),
           same as above.
        2. Looks for an existing "Company - Title" line in Applied_list
           (case-insensitive match on both company and title, ignoring any
           existing "(status)" tag on that line).
             - If found: replaces its status tag with the new one (or
               removes the tag entirely if --status is omitted).
             - If not found: appends a new "Company - Title (status)" line
               (or "Company - Title" with no parens if no status given) to
               the end of Applied_list, matching the file's existing style.

Prints a short human-readable summary of exactly what changed (or didn't)
so the calling model can relay it to the user before they overwrite their
real project files with the output.
"""
import argparse
import os
import re
import sys

VALID_STATUSES = {"rejected", "interview"}


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def read_lines(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f.readlines()]


def write_lines(path: str, lines: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        content = "\n".join(lines)
        f.write(content + ("\n" if content and not content.endswith("\n") else "\n"))


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


def find_applied_entry(company: str, title: str, applied_lines: list):
    """Return the index of a matching 'Company - Title (...)' line, or None."""
    norm_company = normalize(company)
    norm_title = normalize(title)
    for i, line in enumerate(applied_lines):
        if not line.strip() or " - " not in line:
            continue
        left, right = line.split(" - ", 1)
        line_company = normalize(left)
        # Strip a trailing "(status)" tag off the title part before comparing
        right_no_tag = re.sub(r"\s*\([^)]*\)\s*$", "", right).strip()
        line_title = normalize(right_no_tag)
        if line_company == norm_company and line_title == norm_title:
            return i
    return None


def format_entry(company: str, title: str, status: str) -> str:
    base = f"{company} - {title}"
    if status:
        base += f" ({status})"
    return base


def main():
    parser = argparse.ArgumentParser(description="Update job-search tracker files.")
    parser.add_argument("--targets", required=True, help="Path to List_of_targets")
    parser.add_argument("--applied", required=True, help="Path to Applied_list")
    parser.add_argument("--out-dir", required=True, help="Directory to write updated files")
    parser.add_argument("--company", required=True, help="Company name, as it should appear")
    parser.add_argument("--title", default=None, help="Job title (omit for a target-list-only check)")
    parser.add_argument("--status", default=None, help="rejected | interview (omit for no tag)")
    args = parser.parse_args()

    if args.status is not None and args.status not in VALID_STATUSES:
        sys.exit(f"--status must be one of {sorted(VALID_STATUSES)}, got: {args.status!r}")

    target_lines = read_lines(args.targets)
    applied_lines = read_lines(args.applied)
    summary = []

    # Step 1: ensure the company exists in the targets list, in every mode.
    if not company_in_targets(args.company, target_lines):
        strip_trailing_blanks(target_lines)
        target_lines.append(args.company)
        summary.append(f'Added "{args.company}" to List_of_targets (was missing).')
    else:
        summary.append(f'"{args.company}" already present in List_of_targets -- no change.')

    # Step 2: only touch Applied_list if a job title was actually given.
    if args.title:
        idx = find_applied_entry(args.company, args.title, applied_lines)
        new_line = format_entry(args.company, args.title, args.status)
        if idx is not None:
            old_line = applied_lines[idx]
            applied_lines[idx] = new_line
            if old_line != new_line:
                summary.append(f'Updated Applied_list entry:\n    "{old_line}"\n    -> "{new_line}"')
            else:
                summary.append(f'Applied_list entry already up to date: "{new_line}"')
        else:
            strip_trailing_blanks(applied_lines)
            applied_lines.append(new_line)
            summary.append(f'Added new Applied_list entry: "{new_line}"')
    else:
        summary.append("No job title given -- Applied_list left untouched (target-list check only).")

    os.makedirs(args.out_dir, exist_ok=True)
    out_targets = os.path.join(args.out_dir, "List_of_targets")
    out_applied = os.path.join(args.out_dir, "Applied_list")
    write_lines(out_targets, target_lines)
    write_lines(out_applied, applied_lines)

    print("\n".join(summary))
    print(f"\nUpdated files written to: {args.out_dir}")


if __name__ == "__main__":
    main()
