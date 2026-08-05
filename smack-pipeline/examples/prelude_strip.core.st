program Core;
type StrataHeap;
type StrataRef;
type StrataField (t: Type);

// Uninterpreted procedures
procedure __SMACK_and32(a : int, b : int, out r : int)
;

// Implementations
procedure main(out _r : int)

{
  var y : int;
  _exit: {
    anon0: {
      call __SMACK_and32(3, 3, out y);
      _r := 0;
      exit _exit;
    }
  }
};

