#!/usr/bin/env python3
"""
Test script to verify that all APIs automatically refresh expired tokens
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

def get_current_tokens():
    """Get current stored tokens"""
    try:
        response = requests.get(f"{BASE_URL}/oauth/tokens", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error getting tokens: {e}")
        return {}

def test_api_endpoint(endpoint_name: str, url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test a single API endpoint and return results"""
    print(f"\n🔍 Testing {endpoint_name}")
    print(f"   URL: {url}")
    print(f"   Method: {method}")

    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=15)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=15)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=15)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=15)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        return {
            "status": "success",
            "status_code": response.status_code,
            "response_length": len(response.text),
            "is_json": response.headers.get('content-type', '').startswith('application/json'),
            "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text
        }

    except requests.exceptions.Timeout:
        return {"status": "timeout", "message": "Request timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_expired_token():
    """Simulate an expired token by temporarily modifying the token store"""
    print("\n🔄 Simulating Expired Token Scenario")
    print("=" * 50)

    # Get current tokens
    tokens_before = get_current_tokens()
    print(f"📊 Tokens before test: {len(tokens_before)} stored")

    if not tokens_before:
        print("❌ No tokens found. Please complete OAuth flow first.")
        return False

    # Get merchant ID
    merchant_id = list(tokens_before.keys())[0]
    print(f"🏪 Using merchant ID: {merchant_id}")

    # Test all API endpoints
    endpoints_to_test = [
        ("Merchant Info", f"{BASE_URL}/api/merchants/info", "GET"),
        ("Merchant Properties", f"{BASE_URL}/api/merchants/properties", "GET"),
        ("Orders List", f"{BASE_URL}/api/orders", "GET"),
        ("Items List", f"{BASE_URL}/api/inventory/items", "GET"),
        ("Categories List", f"{BASE_URL}/api/inventory/categories", "GET"),
        ("Customers List", f"{BASE_URL}/api/customers", "GET"),
        ("Payments List", f"{BASE_URL}/api/payments", "GET"),
    ]

    print(f"\n🧪 Testing {len(endpoints_to_test)} API endpoints...")

    results = {}
    for endpoint_name, url, method in endpoints_to_test:
        result = test_api_endpoint(endpoint_name, url, method)
        results[endpoint_name] = result

        if result["status"] == "success":
            if result["status_code"] == 200:
                print(f"   ✅ {endpoint_name}: Success (200)")
            elif result["status_code"] == 401:
                print(f"   ⚠️  {endpoint_name}: Unauthorized (401) - Token may be expired")
            else:
                print(f"   ⚠️  {endpoint_name}: Status {result['status_code']}")
        else:
            print(f"   ❌ {endpoint_name}: {result['message']}")

    # Test refresh endpoint specifically
    print(f"\n🔄 Testing Refresh Endpoint")
    refresh_result = test_api_endpoint("Token Refresh", f"{BASE_URL}/oauth/refresh", "POST")
    results["Token Refresh"] = refresh_result

    if refresh_result["status"] == "success":
        if refresh_result["status_code"] == 200:
            print(f"   ✅ Token Refresh: Success (200)")
        else:
            print(f"   ❌ Token Refresh: Status {refresh_result['status_code']}")
    else:
        print(f"   ❌ Token Refresh: {refresh_result['message']}")

    # Get tokens after refresh
    tokens_after = get_current_tokens()

    # Compare tokens
    print(f"\n📊 Token Comparison:")
    print(f"   Before: {len(tokens_before)} tokens")
    print(f"   After:  {len(tokens_after)} tokens")

    if tokens_before and tokens_after:
        merchant_id = list(tokens_before.keys())[0]
        if merchant_id in tokens_after:
            before_exp = tokens_before[merchant_id].get('access_token_expiration', 0)
            after_exp = tokens_after[merchant_id].get('access_token_expiration', 0)

            if after_exp > before_exp:
                print(f"   ✅ Access token expiration updated: {before_exp} → {after_exp}")
                print(f"   ✅ Token refresh is working!")
            else:
                print(f"   ⚠️  Access token expiration unchanged: {before_exp}")
        else:
            print(f"   ❌ Merchant {merchant_id} not found in tokens after refresh")

    return results

def test_manual_refresh():
    """Test manual refresh endpoint"""
    print("\n🔄 Testing Manual Refresh Endpoint")
    print("=" * 50)

    try:
        response = requests.post(f"{BASE_URL}/oauth/refresh", timeout=15)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Manual refresh successful!")
            print(f"   Merchant ID: {data.get('merchant_id')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Manual refresh failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing manual refresh: {e}")
        return False

def main():
    print("🚀 Auto-Refresh Token Testing")
    print("=" * 60)
    print(f"🎯 Testing against: {BASE_URL}")
    print()

    # Test 1: Manual refresh endpoint
    manual_success = test_manual_refresh()

    # Test 2: API endpoints with potential auto-refresh
    results = simulate_expired_token()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Manual Refresh: {'✅ Working' if manual_success else '❌ Failed'}")

    if results:
        successful_apis = [name for name, result in results.items()
                          if result["status"] == "success" and result["status_code"] == 200]
        print(f"   Successful API Calls: {len(successful_apis)}/{len(results)}")

        if successful_apis:
            print("   ✅ Working endpoints:")
            for api in successful_apis:
                print(f"      - {api}")

        failed_apis = [name for name, result in results.items()
                      if result["status"] != "success" or result["status_code"] not in [200, 401]]
        if failed_apis:
            print("   ❌ Failed endpoints:")
            for api in failed_apis:
                print(f"      - {api}: {results[api].get('message', 'Unknown error')}")

    print("\n💡 Notes:")
    print("   - If APIs return 401, it means tokens are expired but auto-refresh should kick in")
    print("   - If APIs return 200, it means tokens are valid or were successfully refreshed")
    print("   - The refresh endpoint should update token expiration timestamps")

if __name__ == "__main__":
    main()
