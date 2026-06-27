# Refactor constraints — `pricing.py`

> **Note:** This file captures the **initial constrained pass** (readability-only,
> no new helpers or module-level names) and was written before any refactor.
> The shipped `after/pricing.py` is the **modular variant** that intentionally
> goes beyond constraints #1 and #10 — extracting an `_item_subtotal` helper and
> `_TAX_RATES` / `_COUPON_FACTORS` lookup tables. See `HANDOFF.md` / `ARCHITECTURE.md`.

Readability only. Written **before** the refactor.

## Hard constraints (must not break)

1. **No new files. No new dependencies. No new module-level imports.**
2. **Public surface unchanged:** `calc(items, country, customer)` keeps the same
   name, parameters, and return type (`float` rounded to 2 dp).
3. **Behavior byte-identical:** every existing test in `after/test_pricing.py`
   must pass with the same results — same rounding, same discount/tax/shipping
   math, same handling of invalid items.
4. Tax rates, shipping thresholds, and discount codes keep their exact values
   and precedence (VIP before coupon; `SAVE10`=0.9, `SAVE20`=0.8; unknown=none).

## Readability changes (allowed / expected)

5. **Flatten nested conditionals with early returns / guard clauses.** In the
   item loop, skip invalid entries with `continue` instead of pyramiding
   (`None`, wrong length, `qty <= 0`, `unit_price <= 0`).
6. **Delete dead branches** — every `else: pass` and other no-op block.
7. **Idiomatic comparisons:** `is None` (not `== None`), truthiness for booleans
   (not `== True`), `.get(...)` without redundant `!= None` guards.
8. **Rename locals only when materially clearer**, e.g. `t→total`,
   `it→item`, `q→qty`, `p→unit_price`, `sub→line_total`, `ship→shipping`.
   Leave already-clear names alone.

## Style limits

9. **No comments** except to explain a non-obvious *why* (not *what*).
10. Don't reorder the tax/shipping logic or extract helpers unless a constraint
    above requires it — keep the diff minimal and reviewable.

## Output

11. When refactoring, output a **unified diff only**, no prose around it.
