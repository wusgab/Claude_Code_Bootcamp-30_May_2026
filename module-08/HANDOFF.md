# HANDOFF — `pricing.py` refactor (modular)

## What changed
- Extracted per-item pricing into a private `_item_subtotal(item, customer)` helper that uses guard-clause early returns; `calc` is now `sum(_item_subtotal(...) for item in items)`.
- Replaced the country-tax `if/elif` chain and the coupon conditionals with module-level lookup tables `_TAX_RATES` (default 0.10) and `_COUPON_FACTORS` (default 1.0).
- Behavior unchanged: public `calc` signature, all rates/thresholds, VIP-over-coupon precedence, and final 2-dp rounding are identical — all 8 tests stay green.

## Why
Inherited code with a six-deep conditional pyramid and one-letter names. Splitting the per-item logic out and turning the rate/discount rules into data makes the flow readable and the rules trivial to extend.

## Risk + how to roll back
- **Risk: low.** No public API or numeric change; pure restructuring. Main exposure is the VIP-before-coupon precedence and the "missing/unknown coupon ⇒ factor 1.0" default.
- **Roll back:** revert the refactor commit, or `git checkout HEAD~1 -- module-08/after/pricing.py`. `before/pricing.py` is the pristine original to diff against.

## Watch-outs for the next engineer
- **VIP beats coupon:** a VIP customer's coupon is intentionally ignored — don't "fix" it without confirming intent.
- **Truthiness:** `if customer.get("vip"):` replaced `== True`; a truthy non-`True` vip value would now discount.
- **Silent defaults:** missing/`None`/unknown coupon all map to factor `1.0`, and invalid items return `0.0` — no errors or logging.
- **Rules are data now:** add a country/coupon by editing `_TAX_RATES` / `_COUPON_FACTORS`, not the control flow. Discount is per-line and applied pre-tax.
