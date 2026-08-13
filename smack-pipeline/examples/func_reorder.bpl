// {:smack}
// Demonstrates BoogieToStrata's dependency-ordered function emission.
//
// Here `caller` is declared before the `callee` it references. BoogieToStrata
// topologically sorts the emitted function section so each definition precedes
// its uses, so the Core lists `callee` before `caller` — no forward reference.

function caller(x: int): int { callee(x) + 1 }
function callee(x: int): int { x * 2 }

procedure main() returns ($r: int)
{
  assert caller(3) == 7;
  $r := 0;
  return;
}
