# ARCHITECTURE — `pricing.py`

Two functions and two lookup tables. `_item_subtotal` prices one validated
line (with discount); `calc` sums those, then applies tax and shipping and
rounds. Rates and discounts live in module-level data, not control flow.

## Data flow

```
   items[]            country            customer{vip, coupon}
      │                  │                        │
      ▼                  │                        │
┌──────────────┐         │                        │
│_item_subtotal│  skip None / wrong-shape /       │
│ (validate)   │  qty<=0 / price<=0 -> 0.0        │
└──────┬───────┘         │                        │
       ▼                  │                        │
┌──────────────┐         │                        │
│ discount     │◀────────┼────────────────────────┘
│ (per line)   │  VIP 0.9 > _COUPON_FACTORS[coupon] (default 1.0)
└──────┬───────┘         │
       ▼ line subtotal   │
┌──────────────┐         │
│ calc(): sum()│  subtotal = Σ _item_subtotal(item, customer)
└──────┬───────┘         │
       │ subtotal        │
   ┌───┴─────┐           ▼
   ▼         ▼      ┌──────────────┐
┌────────┐ ┌──────┐ │ _TAX_RATES   │ (country → rate)
│shipping│ │ tax  │◀┘  US .07 GB .20 DE .19 FR .20 default .10
│ tiers  │ │      │
└───┬────┘ └──┬───┘
    │ ship    │ tax
    └────┬─────┘
         ▼
   ┌────────────────────────┐
   │ round(subtotal+tax+ship,│──► final price
   │       2)               │
   └────────────────────────┘
```

## Components

**`_item_subtotal(item, customer) -> float`.** Inputs: one `(name, qty, price)`
tuple + `customer`. Validates and returns `0.0` for `None`, wrong-length,
`qty<=0`, or `price<=0`; otherwise prices the line and applies at most one
discount — VIP (0.9) taking precedence over a coupon factor. Output: line subtotal.

**`_TAX_RATES` (dict).** Maps ISO-2 country → flat tax rate; `calc` falls back
to `0.10` for unknown countries.

**`_COUPON_FACTORS` (dict).** Maps coupon code → multiplier (`SAVE10`→0.9,
`SAVE20`→0.8); unknown/missing codes fall back to `1.0` (no discount).

**`calc(items, country, customer)`.** Orchestrator. Sums `_item_subtotal` over
all items, multiplies by the tax rate, adds tiered shipping (<50 → 9.99,
<200 → 4.99, else free), and returns the total rounded to 2 dp.

## Known limitations

1. Rules live in code: `_TAX_RATES`/`_COUPON_FACTORS` are module constants —
   adding a country or coupon needs a code edit and deploy, not config.
2. Float money math with a single end rounding — risks cent drift; no `Decimal`.
3. Invalid items and unknown coupons fail silently (`0.0` / factor `1.0`) — no
   errors or logging.
4. No currency/locale awareness — one implicit currency; shipping fees are
   magic numbers.
5. Discounts don't stack and apply per line only — no order-level promotions,
   tiers, or tax-exempt handling.
