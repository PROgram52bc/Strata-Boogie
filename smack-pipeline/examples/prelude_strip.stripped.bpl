// {:smack}
// Demonstrates strip_smack_prelude.py's prelude-body removal.
//
// SMACK emits bitwise-decompose prelude procedures (e.g. __SMACK_and32) whose
// bodies use unstructured multi-target gotos that BoogieToStrata cannot ingest.
// The pre-processor drops the body, leaving an uninterpreted declaration, while
// user procedures (main and user functions) keep their bodies.

procedure __SMACK_and32(a: int, b: int) returns (r: int);

procedure main() returns ($r: int)
{
  var y: int;
  call y := __SMACK_and32(3, 3);
  $r := 0;
  return;
}
