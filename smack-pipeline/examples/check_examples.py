#!/usr/bin/env python3
"""Regenerate each example through the pipeline and check it matches the committed output.

For every <name>.bpl in this directory, runs strip_smack_prelude -> BoogieToStrata
--smack -> fix_core_st and compares the regenerated .stripped.bpl and .core.st
against the committed expected files. Exits non-zero on any mismatch or failure.

Usage:
    python3 check_examples.py [--dotnet /path/to/dotnet]

Requires the .NET 8 SDK (to run the translator). No container / SMACK needed —
these examples start from hand-written .bpl, so the SMACK stage is not exercised.
"""
import argparse
import difflib
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
STRIP = PIPE / "strip_smack_prelude.py"
FIX = PIPE / "fix_core_st.py"
PROJ = PIPE.parent / "Source" / "BoogieToStrata.csproj"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def show_diff(expected: str, actual: str, label: str) -> None:
    for line in difflib.unified_diff(
        expected.splitlines(), actual.splitlines(),
        fromfile=f"{label} (committed)", tofile=f"{label} (regenerated)", lineterm=""):
        print("    " + line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dotnet", default="dotnet")
    args = ap.parse_args()

    bpls = sorted(b for b in HERE.glob("*.bpl") if not b.name.endswith(".stripped.bpl"))
    if not bpls:
        print("no example .bpl files found", file=sys.stderr)
        return 1

    failures = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for bpl in bpls:
            name = bpl.stem
            ok = True

            got_stripped = tmp / f"{name}.stripped.bpl"
            r = run([sys.executable, str(STRIP), str(bpl), str(got_stripped)])
            if r.returncode != 0:
                print(f"FAIL {name}: strip: {r.stderr.strip()}"); failures += 1; continue

            exp_stripped = HERE / f"{name}.stripped.bpl"
            if exp_stripped.exists():
                if got_stripped.read_text() != exp_stripped.read_text():
                    print(f"FAIL {name}: .stripped.bpl mismatch"); ok = False
                    show_diff(exp_stripped.read_text(), got_stripped.read_text(), ".stripped.bpl")

            r = run([args.dotnet, "run", "--project", str(PROJ), "--", "--smack", str(got_stripped)])
            if r.returncode != 0:
                print(f"FAIL {name}: translate: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'rc!=0'}")
                failures += 1; continue
            raw = tmp / f"{name}.raw.core.st"
            raw.write_text(r.stdout)

            got_core = tmp / f"{name}.core.st"
            r = run([sys.executable, str(FIX), str(raw), str(got_core)])
            if r.returncode != 0:
                print(f"FAIL {name}: fix: {r.stderr.strip()}"); failures += 1; continue

            exp_core = HERE / f"{name}.core.st"
            if exp_core.exists():
                if got_core.read_text() != exp_core.read_text():
                    print(f"FAIL {name}: .core.st mismatch"); ok = False
                    show_diff(exp_core.read_text(), got_core.read_text(), ".core.st")

            if ok:
                print(f"OK   {name}")
            else:
                failures += 1

    print(f"\n{len(bpls) - failures}/{len(bpls)} examples match")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
