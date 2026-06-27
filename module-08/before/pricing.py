"""Order pricing — deliberately messy. Refactor in Module 8.

Computes the final price of an order with discounts, taxes, and shipping.
"""

def calc(items, country, customer):
    # items: list of (name, qty, unit_price)
    # country: ISO-2 country code
    # customer: dict with optional keys: vip, coupon
    t = 0
    for it in items:
        if it != None:
            if len(it) == 3:
                n, q, p = it[0], it[1], it[2]
                if q > 0:
                    if p > 0:
                        sub = q * p
                        if customer != None:
                            if customer.get('vip') == True:
                                sub = sub * 0.9
                            else:
                                if customer.get('coupon') != None:
                                    if customer['coupon'] == 'SAVE10':
                                        sub = sub * 0.9
                                    elif customer['coupon'] == 'SAVE20':
                                        sub = sub * 0.8
                                    else:
                                        pass
                        t = t + sub
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    # tax
    if country == 'US':
        tax = t * 0.07
    elif country == 'GB':
        tax = t * 0.20
    elif country == 'DE':
        tax = t * 0.19
    elif country == 'FR':
        tax = t * 0.20
    else:
        tax = t * 0.10
    # shipping
    if t < 50:
        ship = 9.99
    else:
        if t < 200:
            ship = 4.99
        else:
            ship = 0.0
    final = t + tax + ship
    return round(final, 2)
