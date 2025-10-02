#!/usr/bin/env python3
"""
Quick endpoint testing script
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_endpoint(method, endpoint, description):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)

        status = "✅" if 200 <= response.status_code < 300 else "❌"
        print(f"{status} {method} {endpoint} - {response.status_code} - {description}")

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"    Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"    Items: {len(data)}")
            except:
                pass

    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR - {description}: {e}")

def main():
    print("🚀 Testing API Endpoints")
    print("=" * 50)

    # OAuth endpoints
    print("\n🔐 OAuth Endpoints:")
    test_endpoint("GET", "/oauth/tokens", "List tokens")
    test_endpoint("POST", "/oauth/refresh", "Refresh token")

    # Merchant endpoints
    print("\n🏪 Merchant Endpoints:")
    test_endpoint("GET", "/api/merchants/info", "Merchant info")
    test_endpoint("GET", "/api/merchants/properties", "Merchant properties")

    # Inventory endpoints
    print("\n📦 Inventory Endpoints:")
    test_endpoint("GET", "/api/inventory/items", "All items")
    test_endpoint("GET", "/api/inventory/categories", "Categories")
    test_endpoint("GET", "/api/inventory/modifiers", "Modifiers")

    # Orders endpoints
    print("\n📋 Orders Endpoints:")
    test_endpoint("GET", "/api/orders", "All orders")
    test_endpoint("GET", "/api/orders/atomic", "Atomic orders")

    # Customers endpoints
    print("\n👥 Customers Endpoints:")
    test_endpoint("GET", "/api/customers", "All customers")

    # Payments endpoints
    print("\n💳 Payments Endpoints:")
    test_endpoint("GET", "/api/payments", "All payments")

    # Utility endpoints
    print("\n🛠️ Utility Endpoints:")
    test_endpoint("GET", "/", "Root endpoint")

    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    main()
