program Core;
type StrataHeap;
type StrataRef;
type StrataField (t: Type);

// Constants
const _0 : int;

// Axioms
axiom [ax_l12c1]: (_0 == 0);

// Uninterpreted procedures
procedure __VERIFIER_assume(p_0 : int)
;

// Implementations
procedure main(out _r : int)

{
  var x : int;
  _exit: {
    anon0: {
      havoc x;
      assume (x != _0);
      assert (x != _0);
      _r := 0;
      exit _exit;
    }
  }
};

