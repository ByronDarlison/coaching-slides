#!/usr/bin/env python3
"""Check that every drawing script reproduces the committed pictures.

A drawing script that has fallen behind its pictures silently replaces approved artwork the next
time someone runs it (coaching-slides issue 86, 25-Nov-2026). This runs each script and fails if
any file under source/libraries changes. It restores the files it touched before it exits.

Run from the repository root, with a clean source/libraries:
    /usr/bin/python3 source/tools/check_drawings.py
"""
import pathlib
import subprocess
import sys

SOURCE = pathlib.Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
SKIP = {"q4_common.py"}  # shared helpers, not a script


def scripts():
    found = sorted((SOURCE / "artwork").glob("*/drawings/*.py")) + sorted((SOURCE / "libraries" / "kickoff" / "generators").glob("*.py"))
    return [p for p in found if p.name not in SKIP]


def changed():
    out = subprocess.run(["git", "status", "--porcelain", "--", "source/libraries"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [line[3:] for line in out.splitlines()]


def restore():
    subprocess.run(["git", "checkout", "-q", "--", "source/libraries"], cwd=ROOT, check=True)
    subprocess.run(["git", "clean", "-qfd", "--", "source/libraries"], cwd=ROOT, check=True)


def main():
    if changed():
        print("source/libraries has uncommitted changes. Commit or stash them first.")
        return 2
    failures = []
    for script in scripts():
        name = str(script.relative_to(ROOT))
        run = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
        if run.returncode != 0:
            failures.append(f"{name}: failed to run: {run.stderr.strip().splitlines()[-1] if run.stderr.strip() else 'no message'}")
        else:
            files = changed()
            if files:
                failures.append(f"{name}: changes {len(files)} committed file(s): " + ", ".join(pathlib.Path(f).name for f in files[:6]))
        restore()
    if failures:
        print("FAIL: a drawing script no longer matches its pictures.")
        for line in failures:
            print(" -", line)
        return 1
    print(f"PASS: {len(scripts())} drawing scripts reproduce the committed pictures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
