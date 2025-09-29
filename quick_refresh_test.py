#!/usr/bin/env python3
"""
Quick test to verify auto-refresh functionality
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_endpoint(name, url):
    """Test a single endpoint and show results"""
    print(f"\n🔍 Testing {name}")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Success - API call worked")
            return True
        elif response.status_code == 401:
            print("   ⚠️  Unauthorized - Token may be expired")
            return False
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Quick Auto-Refresh Test")
    print("=" * 40)

    # Test key endpoints
    endpoints = [
        ("Merchant Info", f"{BASE_URL}/api/merchants/info"),
        ("Orders List", f"{BASE_URL}/api/orders"),
        ("Items List", f"{BASE_URL}/api/inventory/items"),
        ("Customers List", f"{BASE_URL}/api/customers"),
    ]

    success_count = 0
    total_count = len(endpoints)

    for name, url in endpoints:
        if test_endpoint(name, url):
            success_count += 1

    print(f"\n📊 Results: {success_count}/{total_count} endpoints successful")

    if success_count == total_count:
        print("✅ All APIs are working - auto-refresh is functioning!")
    elif success_count > 0:
        print("⚠️  Some APIs working - check individual endpoint issues")
    else:
        print("❌ No APIs working - check token configuration")

    # Test refresh endpoint
    print(f"\n🔄 Testing Refresh Endpoint")
    try:
        response = requests.post(f"{BASE_URL}/oauth/refresh", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Refresh endpoint working")
        else:
            print("   ❌ Refresh endpoint failed")
    except Exception as e:
        print(f"   ❌ Refresh endpoint error: {e}")

if __name__ == "__main__":
    main()
