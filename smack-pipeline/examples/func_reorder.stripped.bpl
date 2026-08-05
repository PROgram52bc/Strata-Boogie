// {:smack}
// Demonstrates fix_core_st.py's function toposort (post-translation).
//
// BoogieToStrata emits functions in source order. Here `caller` is declared
// before the `callee` it references, producing a forward reference in the
// emitted Core. fix_core_st.py topologically sorts the function section so each
// definition precedes its uses.

function caller(x: int): int { callee(x) + 1 }
function callee(x: int): int { x * 2 }

procedure main() returns ($r: int)
{
  assert caller(3) == 7;
  $r := 0;
  return;
}
