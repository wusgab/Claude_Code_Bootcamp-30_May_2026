"""Tests for pricing.calc — must remain green after refactor."""
from pricing import calc


def test_simple_us():
    items = [("widget", 2, 10.0)]
    assert calc(items, "US", None) == round(20 + 20 * 0.07 + 9.99, 2)


def test_vip_discount_applied():
    items = [("widget", 1, 100.0)]
    assert calc(items, "US", {"vip": True}) == round(90 + 90 * 0.07 + 4.99, 2)


def test_coupon_save10():
    items = [("widget", 1, 100.0)]
    assert calc(items, "US", {"coupon": "SAVE10"}) == round(90 + 90 * 0.07 + 4.99, 2)


def test_coupon_save20():
    items = [("widget", 1, 100.0)]
    assert calc(items, "GB", {"coupon": "SAVE20"}) == round(80 + 80 * 0.20 + 4.99, 2)


def test_unknown_coupon_no_discount():
    items = [("widget", 1, 100.0)]
    assert calc(items, "GB", {"coupon": "UNKNOWN"}) == round(100 + 20 + 4.99, 2)


def test_free_shipping_over_200():
    items = [("widget", 5, 50.0)]
    # 250 subtotal, FR 20% tax, free shipping
    assert calc(items, "FR", None) == round(250 + 50 + 0, 2)


def test_default_tax_rate():
    items = [("widget", 1, 100.0)]
    assert calc(items, "ZZ", None) == round(100 + 10 + 4.99, 2)


def test_skips_invalid_item():
    items = [None, ("widget", 1, 100.0), ("bad", 0, 10.0), ("neg", 1, -5.0)]
    assert calc(items, "US", None) == round(100 + 7 + 4.99, 2)
