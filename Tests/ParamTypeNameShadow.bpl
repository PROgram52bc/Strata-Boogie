// Regression: a function parameter whose name equals a type name must be
// renamed in the emitted Core so it does not shadow the type. Here parameter
// `T` collides with type `T`; the translator must rename the parameter (to
// `p_T`) in the signature, the body, and the lifted definition axiom. This is
// the fix that made fix_core_st.py's shadow-rename pass unnecessary.
type T;

function f(T: int): int { T + 1 }

procedure main() returns ($r: int)
{
  $r := f(0);
  return;
}
