# SMACK → BoogieToStrata pre-processing pipeline

Utilities for turning C sources into Strata Core (`.core.st`) inputs by way of
[SMACK](https://smackers.github.io/) and the BoogieToStrata translator in this
repository. These are the pre/post-processing steps that bracket the translator's
`--smack` mode; they exist so SMACK-generated benchmarks are reproducible from
their C sources.

```
.c  ──SMACK──▶  .bpl  ──strip_smack_prelude──▶  _stripped.bpl
    ──BoogieToStrata --smack──▶  .core.st  ──fix_core_st──▶  _fixed.core.st
```

The `_fixed.core.st` output is ready for `strata verify`. Running the verifier
itself is out of scope here — it lives in the main Strata package.

## Contents

| File | Role |
|---|---|
| `Dockerfile` | Builds a container image with SMACK installed. |
| `smack_to_core.py` | End-to-end driver: `.c` → `.bpl` (SMACK) → `.core.st` (translate) → `_fixed.core.st`. |
| `strip_smack_prelude.py` | Removes SMACK prelude procedure bodies and inlines `__VERIFIER_assume`. |
| `fix_core_st.py` | Post-processes translator output: sorts function definitions, resolves parameter/type name shadowing. |

The C sources are not included here; point the driver at your own `.c` inputs
(see *Usage*).

## Why the pre/post steps are needed

- **`strip_smack_prelude.py`.** SMACK emits ~14 prelude procedures (`__SMACK_and32`,
  `__SMACK_or64`, …) whose bodies use unstructured multi-target gotos that the
  translator does not support. The script drops those bodies, leaving uninterpreted
  declarations, while keeping all user code. It also rewrites each
  `call __VERIFIER_assume(e)` to `assume (e != $0)` inline: a body-less
  `__VERIFIER_assume` is analysed as a no-op under body-evaluating call policies, so
  inlining preserves the path-pruning the assume was meant to express.
- **`fix_core_st.py`.** The translator emits functions in source order and may name a
  parameter identically to a type. This step topologically sorts function definitions
  to remove forward references and renames shadowing parameters (`p_<name>`).

## Prerequisites

- [Finch](https://github.com/runfinch/finch) (`finch vm init`) or Docker, to run SMACK.
- The [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0), to run the
  translator (`Source/BoogieToStrata.csproj`).
- Python 3.

## Building the SMACK image

```bash
cd smack-pipeline
finch build --platform linux/amd64 -t smack .
```

`--platform linux/amd64` is required: SMACK's dependencies (dotnet-sdk-5.0, Z3
x86_64 binaries) are not available for ARM64.

## Usage

Put your C sources in a directory (default `smack-pipeline/programs/`) and run:

```bash
# Whole directory
python3 smack_to_core.py --programs-dir /path/to/programs

# Specific files
python3 smack_to_core.py --programs-dir /path/to/programs foo.c bar.c

# Already have .bpl files? Skip the SMACK stage:
python3 smack_to_core.py --programs-dir /path/to/programs --skip-smack
```

Each stage can also be run standalone:

```bash
# 1. SMACK: .c -> .bpl  (inside the container)
finch run --rm --entrypoint /bin/sh -v "$PWD/programs:/programs" smack \
  -c '. /home/user/smack.environment && cd /programs && smack --no-verify -bpl foo.bpl foo.c'

# 2. strip prelude
python3 strip_smack_prelude.py programs/foo.bpl programs/foo_stripped.bpl

# 3. translate (--smack)
dotnet run --project ../Source -- --smack programs/foo_stripped.bpl > programs/foo.core.st

# 4. fix
python3 fix_core_st.py programs/foo.core.st programs/foo_fixed.core.st
```

## Generated artifacts

All intermediates (`.bpl`, `_stripped.bpl`, `.core.st`, `_fixed.core.st`, and the
LLVM/SMACK by-products) are generated and git-ignored (see `.gitignore`). Only the
utilities are tracked.

## License

Apache-2.0 OR MIT (matching the repository).
