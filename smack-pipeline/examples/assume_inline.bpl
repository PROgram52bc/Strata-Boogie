// {:smack}
// Demonstrates strip_smack_prelude.py's __VERIFIER_assume inlining.
//
// SMACK lowers C `assume(e)` to `call __VERIFIER_assume(e)`, whose body is
// `assume e != $0`. Because a body-less procedure is analysed as a no-op under
// body-evaluating call policies, the pre-processor rewrites each such call to an
// inline `assume (e != $0)` so the path-pruning constraint survives translation.
// The __VERIFIER_assume declaration itself is a prelude stub and is left as a
// bodyless declaration.

const $0: int;
axiom $0 == 0;

procedure __VERIFIER_assume(p.0: int);

procedure main() returns ($r: int)
{
  var x: int;
  havoc x;
  call __VERIFIER_assume(x);
  assert x != $0;
  $r := 0;
  return;
}
