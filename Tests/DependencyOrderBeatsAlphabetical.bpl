// Regression: when dependency order and alphabetical order disagree, dependency
// order wins. `alpha`'s inline body calls `zebra`, so `zebra` must be emitted
// first even though `alpha` < `zebra` alphabetically. A sort that ignored
// dependency edges and fell back to alphabetical would wrongly emit `alpha`
// first, so this discriminates the two orderings (unlike an independent pair,
// where they coincide).
function {:inline} alpha(x: int): int { zebra(x) + 1 }
function {:inline} zebra(x: int): int { x * 2 }

procedure main() returns ($r: int)
{
  $r := 0;
  return;
}
