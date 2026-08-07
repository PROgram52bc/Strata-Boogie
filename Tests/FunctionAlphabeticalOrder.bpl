// Regression: independent functions (no call dependency between them) are
// emitted in alphabetical order, matching the deterministic order the SMACK
// post-processing pipeline expected. `zebra` is declared before `alpha`; with
// no dependency to constrain them, the emitted Core must list `alpha` first.
function zebra(x: int): int { x + 1 }
function alpha(x: int): int { x + 2 }

procedure main() returns ($r: int)
{
  $r := 0;
  return;
}
