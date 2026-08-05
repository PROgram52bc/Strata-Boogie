program Core;
type StrataHeap;
type StrataRef;
type StrataField (t: Type);

// Functions
function callee(x : int) : (int);
function caller(x : int) : (int);
// Axioms
axiom [ax_l9c10]: (forall x: int :: {caller(x)} (caller(x) == (callee(x) + 1)));
axiom [ax_l10c10]: (forall x: int :: {callee(x)} (callee(x) == (x * 2)));

// Uninterpreted procedures
// Implementations
procedure main(out _r : int)

{
  _exit: {
    anon0: {
      assert (caller(3) == 7);
      _r := 0;
      exit _exit;
    }
  }
};

