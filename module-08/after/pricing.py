"""Order pricing.

Computes the final price of an order with discounts, taxes, and shipping.
"""

_TAX_RATES = {"US": 0.07, "GB": 0.20, "DE": 0.19, "FR": 0.20}

_COUPON_FACTORS = {"SAVE10": 0.9, "SAVE20": 0.8}


def _item_subtotal(item, customer) -> float:
    if item is None or len(item) != 3:
        return 0.0
    _, qty, price = item
    if qty <= 0 or price <= 0:
        return 0.0
    subtotal = qty * price
    if customer is None:
        return subtotal
    # VIP takes priority; a customer with both vip and coupon gets only the VIP discount
    if customer.get("vip"):
        return subtotal * 0.9
    factor = _COUPON_FACTORS.get(customer.get("coupon", ""), 1.0)
    return subtotal * factor


def calc(items, country, customer):
    subtotal = sum(_item_subtotal(item, customer) for item in items)
    tax = subtotal * _TAX_RATES.get(country, 0.10)
    if subtotal < 50:
        shipping = 9.99
    elif subtotal < 200:
        shipping = 4.99
    else:
        shipping = 0.0
    return round(subtotal + tax + shipping, 2)
