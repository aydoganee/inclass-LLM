"""
US-T7: Submission — Prepare ZIP package with all evidence files
Owner: Oğuzhan Elmas

Usage:
    python prepare_submission.py

Builds submission/G12_SUBMISSION_YYYY-MM-DD.zip and prints a checklist
of all 33 rubric evidence items, marking which ones are present.

Place all evidence files in the docs/ folder with filenames following
the convention:  G12_S{1|2}_<EVIDENCE_TYPE>_YYYY-MM-DD.<ext>

Before running, ensure:
  - docs/ contains all collected evidence files
  - REPO_INFO.txt is up-to-date
  - sprint-1 and sprint-2 git tags have been pushed
"""

import os
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path

TEAM_ID = "G12"
REPO_ROOT = Path(__file__).parent
DOCS_DIR = REPO_ROOT / "docs"
OUTPUT_DIR = REPO_ROOT / "submission"

# Files and directories to include in source_code/
SOURCE_INCLUDES = [
    "app",
    "tests",
    "instructor_tests",
    "requirements.txt",
    "README.md",
    ".gitignore",
    "conftest.py",
    "seed_demo_data.py",
    ".env.example",
]

# Rubric evidence items: (code, sprint, description, pattern_hint)
# pattern_hint is a regex matched against filenames in docs/
EVIDENCE_ITEMS = [
    ("E01", "-",  "Product Goal",                              r"PRODUCT.GOAL"),
    ("E02", "-",  "Product Backlog (initial SP)",              r"PRODUCT.BACKLOG"),
    ("E03", "S1", "Planning Poker Sprint 1",                   r"S1.*(POKER|PLANNING.POKER|PLANNING)"),
    ("E04", "S2", "Planning Poker Sprint 2",                   r"S2.*(POKER|PLANNING.POKER|PLANNING)"),
    ("E05", "S1", "Sprint Goal Sprint 1",                      r"S1.*SPRINT.GOAL"),
    ("E06", "S2", "Sprint Goal Sprint 2",                      r"S2.*SPRINT.GOAL"),
    ("E07", "S1", "Sprint Planning record Sprint 1",           r"S1.*SPRINT.PLANNING"),
    ("E08", "S2", "Sprint Planning record Sprint 2",           r"S2.*SPRINT.PLANNING"),
    ("E09", "S1", "Sprint Backlog task breakdown Sprint 1",    r"S1.*SPRINT.BACKLOG"),
    ("E10", "S2", "Sprint Backlog task breakdown Sprint 2",    r"S2.*SPRINT.BACKLOG"),
    ("E11", "S1", "ClickUp baseline screenshot Sprint 1",      r"S1.*BASELINE"),
    ("E12", "S2", "ClickUp baseline screenshot Sprint 2",      r"S2.*BASELINE"),
    ("E13", "S1", "Daily Scrum records Sprint 1 (min 2)",      r"S1.*DAILY"),
    ("E14", "S2", "Daily Scrum records Sprint 2 (min 2)",      r"S2.*DAILY"),
    ("E15", "S1", "Post-daily board screenshots Sprint 1 (min 2)", r"S1.*POST.DAILY"),
    ("E16", "S2", "Post-daily board screenshots Sprint 2 (min 2)", r"S2.*POST.DAILY"),
    ("E17", "S1", "Sprint Review Sprint 1",                    r"S1.*REVIEW"),
    ("E18", "S2", "Sprint Review Sprint 2",                    r"S2.*REVIEW"),
    ("E19", "S1", "Sprint Retrospective Sprint 1",             r"S1.*RETRO"),
    ("E20", "S2", "Sprint Retrospective Sprint 2",             r"S2.*RETRO"),
    ("E21", "S1", "Burndown chart Sprint 1",                   r"S1.*BURNDOWN"),
    ("E22", "S2", "Burndown chart Sprint 2",                   r"S2.*BURNDOWN"),
    ("E23", "S1", "Scope Change Log Sprint 1",                 r"S1.*SCOPE"),
    ("E24", "S2", "Scope Change Log Sprint 2",                 r"S2.*SCOPE"),
    ("E25", "-",  "ClickUp Task History export",               r"TASK.HISTORY"),
    ("E26", "-",  "ClickUp Activity Log export",               r"ACTIVITY.LOG"),
    ("E27", "-",  "Acceptance criteria & tutoring-flow test matrix", r"TEST.MATRIX"),
    ("E28", "-",  "GitHub commit traceability evidence",       r"COMMIT"),
    ("E29", "-",  "GitHub PR evidence",                        r"(GITHUB.*PR|PULL.REQUEST|PR.EVIDENCE)"),
    ("E30", "-",  "GitHub code review evidence",               r"(CODE.REVIEW|REVIEW.EVIDENCE)"),
    ("E31", "-",  "Meeting attendance per person",             r"(ATTENDANCE|MEETING)"),
    ("E32", "-",  "Git tags sprint-1, sprint-2",               r"(GIT.TAG|TAG)"),
    ("E33", "-",  "ZIP structure compliance",                  None),  # checked by this script
]


def _docs_files():
    if not DOCS_DIR.exists():
        return []
    return [f.name.upper() for f in DOCS_DIR.iterdir() if f.is_file()]


def _matches(pattern, filenames):
    if pattern is None:
        return True  # auto-satisfied by this script building the ZIP
    rx = re.compile(pattern, re.IGNORECASE)
    return any(rx.search(name) for name in filenames)


def check_evidence():
    filenames = _docs_files()
    print("\n" + "=" * 70)
    print(f"  Evidence Checklist — Team {TEAM_ID}")
    print("=" * 70)
    missing = []
    for code, sprint, desc, pattern in EVIDENCE_ITEMS:
        found = _matches(pattern, filenames)
        status = "OK" if found else "MISSING"
        label = f"[{status:7s}]"
        tag = f"{code} ({sprint})" if sprint != "-" else f"{code}     "
        print(f"  {label} {tag}  {desc}")
        if not found:
            missing.append((code, sprint, desc))
    print("=" * 70)
    if missing:
        print(f"\n  {len(missing)} item(s) MISSING — add files to docs/ and re-run.")
    else:
        print("\n  All evidence items present.")
    return missing


def build_zip():
    today = date.today().strftime("%Y-%m-%d")
    zip_name = f"{TEAM_ID}_SUBMISSION_{today}.zip"
    zip_path = OUTPUT_DIR / zip_name

    OUTPUT_DIR.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # REPO_INFO.txt
        repo_info = REPO_ROOT / "REPO_INFO.txt"
        if repo_info.exists():
            zf.write(repo_info, "REPO_INFO.txt")

        # PROMPT_CHANGES.md (optional)
        prompt_changes = REPO_ROOT / "PROMPT_CHANGES.md"
        if prompt_changes.exists():
            zf.write(prompt_changes, "PROMPT_CHANGES.md")

        # source_code/
        for item in SOURCE_INCLUDES:
            src = REPO_ROOT / item
            if src.is_dir():
                for file in src.rglob("*"):
                    if file.is_file() and "__pycache__" not in str(file) and ".venv" not in str(file):
                        arcname = "source_code/" + str(file.relative_to(REPO_ROOT))
                        zf.write(file, arcname)
            elif src.is_file():
                zf.write(src, "source_code/" + item)

        # Evidence files from docs/
        if DOCS_DIR.exists():
            for f in DOCS_DIR.iterdir():
                if f.is_file():
                    zf.write(f, f.name)

    print(f"\n  ZIP created: {zip_path}")
    print(f"  Size: {zip_path.stat().st_size / 1024:.1f} KB")
    return zip_path


if __name__ == "__main__":
    missing = check_evidence()
    if missing:
        answer = input("\nBuild ZIP anyway (missing items will be absent)? [y/N]: ").strip().lower()
        if answer != "y":
            print("Aborted. Add missing files to docs/ and re-run.")
            raise SystemExit(1)
    build_zip()
    print("\nDone. Upload the ZIP to the course submission portal.")
