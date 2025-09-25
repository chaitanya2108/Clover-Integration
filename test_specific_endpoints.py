#!/usr/bin/env python3
"""
Test script for Clover API endpoints - specifically atomic order creation and inventory items
"""

import requests
import json
import time

def test_endpoint(url, method='GET', data=None, description=''):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=10)

        return {
            'url': url,
            'method': method,
            'description': description,
            'status_code': response.status_code,
            'success': response.status_code in [200, 201],
            'response_time': response.elapsed.total_seconds(),
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:400]
        }
    except Exception as e:
        return {
            'url': url,
            'method': method,
            'description': description,
            'success': False,
            'error': str(e)
        }

def main():
    """Test specific endpoints"""
    base_url = "http://localhost:5000"

    print("=" * 60)
    print("Clover API Specific Endpoint Tests")
    print("=" * 60)

    # Test inventory items first to get item IDs for atomic order
    print("1. Testing Inventory Items...")
    inventory_result = test_endpoint(f"{base_url}/api/inventory/items?limit=5", description="Get inventory items")

    print(f"{'✅ PASS' if inventory_result['success'] else '❌ FAIL'} {inventory_result['description']}")
    print(f"    Status: {inventory_result.get('status_code', 'N/A')}")
    if inventory_result.get('error'):
        print(f"    Error: {inventory_result['error']}")
    elif inventory_result.get('response_time'):
        print(f"    Response time: {inventory_result['response_time']:.3f}s")

    # Try to get an item ID for atomic order test
    item_id = None
    if inventory_result['success'] and isinstance(inventory_result['response'], dict):
        items = inventory_result['response'].get('elements', [])
        if items:
            item_id = items[0].get('id')
            print(f"    Found item ID for atomic order test: {item_id}")

    print()

    # Test atomic order creation
    print("2. Testing Atomic Order Creation...")

    if item_id:
        # Create a simple atomic order with one line item
        atomic_order_data = {
            "orderCart": {
                "currency": "USD",
                "title": "Test Order",
                "note": "Test order from API testing suite",
                "clientCreatedTime": int(time.time() * 1000),
                "lineItems": [
                    {
                        "item": {"id": item_id},
                        "name": "Test Item",
                        "price": 1000,  # $10.00 in cents
                        "unitQty": 1,
                        "note": "Test line item"
                    }
                ],
                "groupLineItems": True
            }
        }

        atomic_result = test_endpoint(
            f"{base_url}/api/orders/atomic",
            method='POST',
            data=atomic_order_data,
            description="Create atomic order"
        )

        print(f"{'✅ PASS' if atomic_result['success'] else '❌ FAIL'} {atomic_result['description']}")
        print(f"    Status: {atomic_result.get('status_code', 'N/A')}")
        if atomic_result.get('error'):
            print(f"    Error: {atomic_result['error']}")
        elif atomic_result.get('response_time'):
            print(f"    Response time: {atomic_result['response_time']:.3f}s")

        # Show created order ID if successful
        if atomic_result['success'] and isinstance(atomic_result['response'], dict):
            order_id = atomic_result['response'].get('id')
            if order_id:
                print(f"    Created order ID: {order_id}")
    else:
        print("❌ SKIP Create atomic order - no item ID available from inventory")

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    results = [inventory_result]
    if item_id:
        results.append(atomic_result)

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"Passed: {passed}/{total} endpoints")

    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("\nTroubleshooting tips:")
        print("- Ensure OAuth tokens are valid")
        print("- Check merchant has inventory items")
        print("- Verify server is running with latest code")

if __name__ == "__main__":
    main()