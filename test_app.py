#!/usr/bin/env python3
"""
Simple test script to verify Clover API Flask application setup
"""

import requests
import json
import time
from typing import Dict, Any

def test_endpoint(url: str, description: str) -> Dict[str, Any]:
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=10)
        return {
            'url': url,
            'description': description,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response_time': response.elapsed.total_seconds(),
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except Exception as e:
        return {
            'url': url,
            'description': description,
            'success': False,
            'error': str(e)
        }

def main():
    """Run basic tests on the Flask application"""
    base_url = "http://localhost:5000"

    print("=" * 60)
    print("Clover API Flask Application Test")
    print("=" * 60)

    # Test endpoints (focus on GETs that don't require IDs)
    endpoints = [
        ('/', 'Main application endpoint'),
        ('/health', 'Health check endpoint'),
        ('/api/status', 'Clover API status endpoint'),
        ('/oauth/tokens', 'View stored OAuth tokens (redacted)'),
        ('/api/merchants/info', 'Merchant info'),
        ('/api/merchants/properties', 'Merchant properties'),
        # Inventory
        ('/api/inventory/items?limit=5', 'Inventory items (limit 5)'),
        ('/api/inventory/categories', 'Inventory categories'),
        # Orders
        ('/api/orders/?limit=5', 'Orders list (limit 5)'),
        # Payments
        ('/api/payments/?limit=5', 'Payments list (limit 5)'),
        ('/api/payments/refunds?limit=5', 'Refunds list (limit 5)'),
        # Customers
        ('/api/customers/?limit=5', 'Customers list (limit 5)'),
        # Swagger last
        ('/swagger/', 'Swagger documentation')
    ]

    results = []

    print("Testing endpoints...")
    print("-" * 40)

    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        result = test_endpoint(url, description)
        results.append(result)

        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {description}")
        print(f"    URL: {url}")
        print(f"    Status: {result.get('status_code', 'N/A')}")

        if 'error' in result:
            print(f"    Error: {result['error']}")
        elif 'response_time' in result:
            print(f"    Response time: {result['response_time']:.3f}s")
        # Print small snippet of JSON to help debug failures
        if not result.get('success') and isinstance(result.get('response'), dict):
            snippet = json.dumps(result['response'])[:400]
            print(f"    Body: {snippet}")

        print()

    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)

    print("=" * 60)
    print(f"Test Summary: {passed}/{total} endpoints passed")

    if passed == total:
        print("✅ All tests passed! Your Flask application is running correctly.")
        print("\nNext steps:")
        print("1. Configure your Clover API credentials in .env file")
        print("2. Visit http://localhost:5000/swagger/ to test Clover APIs")
        print("3. Use /api/status endpoint to verify Clover API connection")
    else:
        print("❌ Some tests failed. Please check the application setup.")

        if any(r.get('error', '').find('Connection refused') != -1 for r in results):
            print("\n⚠️  It looks like the Flask application is not running.")
            print("   Please start it with: python main.py")

    print("=" * 60)

if __name__ == "__main__":
    main()