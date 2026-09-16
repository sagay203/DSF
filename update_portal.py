#!/usr/bin/env python3
"""
update_portal.py  —  DSF Scholarship Portal

Takes your updated DSF_scholarships.json and rewrites the scheme data
inside both HTML files, so the live site matches your edited data.

USAGE:  python update_portal.py

Put this script in the same folder as:
    DSF_scholarships.json          (your updated data)
    DSF_Scholarship_Portal.html
    DSF_Scholarship_Editor.html

It makes a dated backup of each HTML file before touching it.
"""

import json
import os
import shutil
import sys
from datetime import datetime

DATA = "DSF_scholarships.json"
TARGETS = ["DSF_Scholarship_Portal.html", "DSF_Scholarship_Editor.html"]
MARKER = "const SCHEMES = "


def find_array(text, start):
    """Return (start, end) of the JSON array beginning at `start`.

    Walks the text tracking bracket depth, correctly skipping over
    brackets that appear inside strings or as escaped characters.
    """
    if text[start] != "[":
        raise ValueError("expected '[' at array start")
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise ValueError("array never closed — file may be corrupted")


def check(records):
    """Refuse to write anything that would break the portal."""
    problems = []
    if not isinstance(records, list):
        problems.append("top level of the JSON is not a list")
        return problems
    if not records:
        problems.append("the list is empty")
        return problems

    seen = {}
    for n, r in enumerate(records, 1):
        if not isinstance(r, dict):
            problems.append(f"record {n} is not an object")
            continue
        rid = r.get("id")
        if not rid:
            problems.append(f"record {n} has no 'id'")
        elif rid in seen:
            problems.append(f"duplicate id '{rid}' (records {seen[rid]} and {n})")
        else:
            seen[rid] = n
        if not r.get("name"):
            problems.append(f"record {n} (id '{rid}') has no 'name'")
    return problems


def main():
    here = os.getcwd()

    missing = [f for f in [DATA] + TARGETS if not os.path.exists(f)]
    if missing:
        print("Could not find these files in this folder:")
        for f in missing:
            print("   -", f)
        print(f"\nCurrent folder: {here}")
        print("Move this script into the folder holding those files and run it again.")
        return 1

    try:
        with open(DATA, encoding="utf-8") as fh:
            records = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"{DATA} is not valid JSON.")
        print(f"   Error on line {e.lineno}, column {e.colno}: {e.msg}")
        print("\nNothing was changed. Re-export from the editor and try again.")
        return 1

    problems = check(records)
    if problems:
        print("Problems found in the data — nothing was changed:\n")
        for p in problems[:15]:
            print("   -", p)
        if len(problems) > 15:
            print(f"   ... and {len(problems) - 15} more")
        return 1

    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")

    print(f"Loaded {len(records)} schemes from {DATA}\n")

    for target in TARGETS:
        with open(target, encoding="utf-8") as fh:
            html = fh.read()

        pos = html.find(MARKER)
        if pos == -1:
            print(f"! {target}: could not find the scheme data — skipped")
            continue

        astart = html.index("[", pos)
        try:
            astart, aend = find_array(html, astart)
        except ValueError as e:
            print(f"! {target}: {e} — skipped")
            continue

        old_count = len(json.loads(html[astart:aend]))

        backup = f"{target}.backup_{stamp}"
        shutil.copy2(target, backup)

        new_html = html[:astart] + payload + html[aend:]
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(new_html)

        delta = len(records) - old_count
        note = "no change in count" if delta == 0 else f"{delta:+d}"
        print(f"  updated {target}")
        print(f"      {old_count} -> {len(records)} schemes ({note})")
        print(f"      backup saved as {backup}")

    print("\nDone. Next step: upload the two updated HTML files to GitHub.")
    print("Vercel will redeploy them automatically within a minute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
