#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://localhost:8080"

endpoints = [
    ("GET", "/oauth/tokens", "OAuth Tokens"),
    ("POST", "/oauth/refresh", "OAuth Refresh"),
    ("GET", "/api/merchants/info", "Merchant Info"),
    ("GET", "/api/merchants/properties", "Merchant Properties"),
    ("GET", "/api/inventory/items?limit=5", "Inventory Items"),
    ("GET", "/api/inventory/categories?limit=5", "Categories"),
    ("GET", "/api/inventory/modifiers?limit=5", "Modifiers"),
    ("GET", "/api/orders?limit=5", "Orders"),
    ("GET", "/api/customers?limit=5", "Customers"),
    ("GET", "/api/payments?limit=5", "Payments"),
]

print("Testing API Endpoints...")
print("=" * 60)

passed = 0
failed = 0

for method, endpoint, description in endpoints:
    try:
        url = BASE_URL + endpoint
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, timeout=5)

        if 200 <= r.status_code < 300:
            print(f"✅ {description}: {r.status_code}")
            passed += 1
        else:
            print(f"❌ {description}: {r.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ {description}: ERROR - {str(e)[:50]}")
        failed += 1

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed out of {len(endpoints)} tests")
print(f"Success rate: {(passed/len(endpoints)*100):.1f}%")
