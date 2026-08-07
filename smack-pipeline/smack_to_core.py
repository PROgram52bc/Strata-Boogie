#!/usr/bin/env python3
"""Generate Strata Core (.core.st) from C sources via SMACK + BoogieToStrata.

Pipeline:

    .c  --SMACK-->  .bpl  --strip_smack_prelude-->  _stripped.bpl
        --BoogieToStrata --smack-->  .core.st

SMACK runs in a container (see Dockerfile). BoogieToStrata is the translator in
this repository; this script drives its `--smack` mode. One Python stage runs
before the translator:

  - strip_smack_prelude.py — remove SMACK prelude procedure bodies (unstructured
    multi-target gotos the translator cannot ingest) and inline __VERIFIER_assume.

The translator emits functions in dependency order and renames type-shadowing
parameters itself, so no post-processing of its output is needed. The output
`.core.st` files are ready for `strata verify`; running the verifier is out of
scope for this script (it lives in the main Strata package).

Usage:
    python3 smack_to_core.py [options] [program.c ...]

With no positional arguments, every .c under --programs-dir is processed.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STRIP = HERE / "strip_smack_prelude.py"
TRANSLATOR_PROJ = HERE.parent / "Source" / "BoogieToStrata.csproj"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def container_cli(preferred: str | None) -> str | None:
    for cli in ([preferred] if preferred else ["finch", "docker"]):
        if cli and shutil.which(cli):
            return cli
    return None


def smack_to_bpl(cli: str, image: str, programs_dir: Path, stems: list[str]) -> None:
    """Run SMACK inside the container over the whole programs dir (one mount).

    Emits <stem>.bpl next to each <stem>.c. Skips stems whose .bpl already exists.
    """
    todo = [s for s in stems if not (programs_dir / f"{s}.bpl").exists()]
    if not todo:
        print("  all .bpl already present; skipping SMACK", file=sys.stderr)
        return
    inner = (
        ". /home/user/smack.environment && cd /programs && "
        + " ".join(
            f'smack --no-verify -bpl "{s}.bpl" "{s}.c";' for s in todo
        )
    )
    print(f"  SMACK ({cli}, {len(todo)} program(s))...", file=sys.stderr)
    r = run([cli, "run", "--rm", "--entrypoint", "/bin/sh",
             "-v", f"{programs_dir}:/programs", image, "-c", inner])
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"SMACK failed (rc={r.returncode})")


def translate(dotnet: str, bpl: Path, out_core: Path) -> None:
    """strip -> BoogieToStrata --smack, producing out_core."""
    stripped = bpl.with_name(bpl.stem + "_stripped.bpl")
    r = run([sys.executable, str(STRIP), str(bpl), str(stripped)])
    if r.returncode != 0:
        raise SystemExit(f"strip failed on {bpl.name}: {r.stderr.strip()}")

    r = run([dotnet, "run", "--project", str(TRANSLATOR_PROJ), "--",
             "--smack", str(stripped)])
    if r.returncode != 0:
        raise SystemExit(f"BoogieToStrata failed on {bpl.name}: {r.stderr.strip()}")
    out_core.write_text(r.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("programs", nargs="*",
                    help="C source files (default: every .c under --programs-dir)")
    ap.add_argument("--programs-dir", type=Path, default=HERE / "programs",
                    help="directory of .c inputs and generated artifacts")
    ap.add_argument("--container-cli", default=None,
                    help="container CLI for SMACK (default: finch, then docker)")
    ap.add_argument("--image", default="smack",
                    help="SMACK container image tag (default: smack)")
    ap.add_argument("--dotnet", default="dotnet", help="dotnet executable")
    ap.add_argument("--skip-smack", action="store_true",
                    help="assume .bpl already generated; only translate")
    args = ap.parse_args()

    pdir = args.programs_dir
    if args.programs:
        stems = [Path(p).stem for p in args.programs]
    else:
        stems = sorted(p.stem for p in pdir.glob("*.c"))
    if not stems:
        print(f"No .c inputs found under {pdir}", file=sys.stderr)
        return 1

    if not args.skip_smack:
        cli = container_cli(args.container_cli)
        if cli is None:
            print("No container CLI (finch/docker) found; use --skip-smack if .bpl "
                  "files already exist, or install Finch.", file=sys.stderr)
            return 1
        smack_to_bpl(cli, args.image, pdir, stems)

    if not shutil.which(args.dotnet):
        print(f"dotnet not found ({args.dotnet}); install the .NET 8 SDK.", file=sys.stderr)
        return 1

    ok, failed = 0, []
    for stem in stems:
        bpl = pdir / f"{stem}.bpl"
        if not bpl.exists():
            print(f"  SKIP {stem}: no .bpl (SMACK did not emit it)", file=sys.stderr)
            failed.append(stem)
            continue
        out = pdir / f"{stem}.core.st"
        try:
            translate(args.dotnet, bpl, out)
            print(f"  OK {stem} -> {out.name}", file=sys.stderr)
            ok += 1
        except SystemExit as e:
            print(f"  FAIL {stem}: {e}", file=sys.stderr)
            failed.append(stem)

    print(f"\n{ok} succeeded, {len(failed)} failed"
          + (f": {', '.join(failed)}" if failed else ""), file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
