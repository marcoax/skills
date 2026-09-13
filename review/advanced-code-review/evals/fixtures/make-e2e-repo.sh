#!/usr/bin/env bash
# Rebuilds the throwaway fixture for eval case e2e-1-real-repo.
# Usage: bash evals/fixtures/make-e2e-repo.sh [target-dir]   (default: /tmp/acr-e2e)
#
# The fixture is a git repo whose UNCOMMITTED changes contain, by construction:
#   - a missing spec requirement (no range validation)      -> expect BLOCKER
#   - a function the spec never asked for (applyAll)        -> expect scope creep
#   - a skipped test covering a spec requirement            -> expect test_audit + finding
#   - a genuinely failing test (float precision: 0.63 vs 0.6299999999999999)
# Spec text for the review is in SPEC.md at the repo root.
set -euo pipefail

DIR="${1:-/tmp/acr-e2e}"
rm -rf "$DIR"
mkdir -p "$DIR/src" "$DIR/test"
cd "$DIR"

git init -q
git config user.email fixture@example.com
git config user.name Fixture

cat > SPEC.md <<'EOF'
# Task: percentage discount

## Acceptance criteria

1. `applyDiscount(price, percent)` returns the price with `percent` deducted.
2. A `percent` outside the range 0–100 is rejected with an error.
3. Money must not drift: a discounted price is exact to the cent.
EOF

# --- committed baseline: the module does not exist yet ---
cat > src/discount.mjs <<'EOF'
// discount helpers
EOF
cat > test/discount.test.mjs <<'EOF'
import test from "node:test";
EOF
git add -A
git commit -qm "baseline"

# --- uncommitted change under review ---
cat > src/discount.mjs <<'EOF'
// discount helpers

export function applyDiscount(price, percent) {
  return price - (price * percent) / 100;
}

export function applyAll(prices, percent) {
  return prices.map((p) => applyDiscount(p, percent));
}
EOF

cat > test/discount.test.mjs <<'EOF'
import test from "node:test";
import assert from "node:assert";
import { applyDiscount } from "../src/discount.mjs";

test("deducts the percentage", () => {
  assert.strictEqual(applyDiscount(200, 10), 180);
});

test("keeps money exact to the cent", () => {
  assert.strictEqual(applyDiscount(0.7, 10), 0.63);
});

test("rejects a percent above 100", { skip: "not implemented yet" }, () => {
  assert.throws(() => applyDiscount(100, 120));
});
EOF

echo "fixture ready: $DIR"
echo "spec:   $DIR/SPEC.md"
echo "diff:   git -C $DIR diff"
echo "tests:  cd $DIR && node --test 'test/*.test.mjs'"
