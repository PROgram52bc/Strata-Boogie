# Pipeline examples

Three small, self-contained examples that demonstrate the pre/post-processing
stages of the SMACK → BoogieToStrata pipeline. Each starts from a hand-written
`.bpl` (shaped like SMACK output) so the examples run without SMACK or a
container — only the .NET 8 SDK is needed for the translator.

For each `<name>` the committed files are:

| File | Stage |
|---|---|
| `<name>.bpl` | input (SMACK-shaped Boogie) |
| `<name>.stripped.bpl` | after `strip_smack_prelude.py` |
| `<name>.core.st` | after `BoogieToStrata --smack` then `fix_core_st.py` |
| `<name>.raw.core.st` | translator output *before* `fix_core_st.py` (only where the fix changes it) |

## The three examples

### `assume_inline` — `strip_smack_prelude.py` inlines `__VERIFIER_assume`

`.bpl` → `.stripped.bpl` rewrites the call to an inline assume:

```
- call __VERIFIER_assume(x);
+ assume (x != $0);
```

A body-less `__VERIFIER_assume` is a no-op under body-evaluating call policies, so
inlining preserves the path-pruning constraint. The final `.core.st` carries the
`assume (x != _0)` directly ahead of the assertion.

### `prelude_strip` — `strip_smack_prelude.py` drops a prelude body

`__SMACK_and32` has a multi-target-goto body SMACK emits but the translator can't
ingest. Stripping turns it into a bodyless declaration while `main` keeps its body:

```
- procedure __SMACK_and32(a: int, b: int) returns (r: int) { ...goto then, else;... }
+ procedure __SMACK_and32(a: int, b: int) returns (r: int);
```

The `.core.st` shows it as an uninterpreted `procedure __SMACK_and32(...)` with no
implementation.

### `func_reorder` — `fix_core_st.py` topologically sorts functions

`caller` references `callee` but is declared first. The translator emits them in
source order (`.raw.core.st`), producing a forward reference; `fix_core_st.py`
reorders so each definition precedes its uses (`.core.st`):

```
  # .raw.core.st          # .core.st
  function caller(...)     function callee(...)
  function callee(...)     function caller(...)
```

## Regenerating / checking

`check_examples.py` re-runs each `.bpl` through the pipeline and diffs the result
against the committed `.stripped.bpl` / `.core.st`, so the examples double as a
regression test for the utilities:

```bash
python3 check_examples.py            # uses `dotnet` on PATH
python3 check_examples.py --dotnet /path/to/dotnet
```

Exits non-zero (with a unified diff) on any mismatch.
