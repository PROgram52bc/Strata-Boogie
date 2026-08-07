// Regression: inline function bodies must be emitted in dependency order so a
// callee precedes its caller. Here `caller` is declared before the `callee` it
// references; the translator must topologically sort the function section so
// `callee` comes first (no forward reference in the emitted Core).
function {:inline} caller(x: int): int { callee(x) + 1 }
function {:inline} callee(x: int): int { x * 2 }

procedure main() returns ($r: int)
{
  assert caller(3) == 7;
  $r := 0;
  return;
}
