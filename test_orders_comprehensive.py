#!/usr/bin/env python3
"""
Comprehensive test script for all Clover Order API endpoints
Tests all order management operations through the Flask API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_result(test_name, success, response_data=None, error=None):
    """Print test result in a formatted way"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")

    if success and response_data:
        if isinstance(response_data, dict):
            if 'id' in response_data:
                print(f"    ID: {response_data.get('id')}")
            if 'state' in response_data:
                print(f"    State: {response_data.get('state')}")
            if 'total' in response_data:
                print(f"    Total: ${response_data.get('total', 0)/100:.2f}")
        elif isinstance(response_data, list):
            print(f"    Found {len(response_data)} items")

    if error:
        print(f"    Error: {error}")

def test_get_orders():
    """Test GET /api/orders - Get list of orders"""
    print_section("TEST 1: Get All Orders")

    try:
        response = requests.get(f"{BASE_URL}/api/orders", timeout=30)
        success = response.status_code == 200
        data = response.json() if success else None
        error = response.text if not success else None

        print_result("Get Orders List", success, data, error)
        return data if success else None

    except Exception as e:
        print_result("Get Orders List", False, error=str(e))
        return None

def test_create_atomic_order():
    """Test POST /api/orders/atomic - Create atomic order"""
    print_section("TEST 2: Create Atomic Order")

    atomic_order_payload = {
        "orderCart": {
            "currency": "USD",
            "title": "Test Order - API Testing",
            "note": "Created via comprehensive test script",
            "clientCreatedTime": int(time.time() * 1000),
            "lineItems": [
                {
                    "item": {"id": "M87Z9DK9BVKKE"},  # Margherita Pizza
                    "name": "Margherita",
                    "price": 1699,
                    "unitQty": 1,
                    "note": "Test pizza order"
                },
                {
                    "item": {"id": "1FC5RCZ4XPZTT"},  # Cappuccino
                    "name": "Cappuccino",
                    "price": 499,
                    "unitQty": 1,
                    "note": "Test coffee order"
                }
            ],
            "groupLineItems": True
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/atomic",
            json=atomic_order_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        success = response.status_code in [200, 201]
        data = response.json() if success else None
        error = response.text if not success else None

        print_result("Create Atomic Order", success, data, error)
        return data.get('id') if success and data else None

    except Exception as e:
        print_result("Create Atomic Order", False, error=str(e))
        return None

def test_get_single_order(order_id):
    """Test GET /api/orders/{orderId} - Get specific order"""
    print_section("TEST 3: Get Single Order")

    if not order_id:
        print_result("Get Single Order", False, error="No order ID provided")
        return None

    try:
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}", timeout=30)
        success = response.status_code == 200
        data = response.json() if success else None
        error = response.text if not success else None

        print_result("Get Single Order", success, data, error)
        return data if success else None

    except Exception as e:
        print_result("Get Single Order", False, error=str(e))
        return None

def test_update_order(order_id):
    """Test POST /api/orders/{orderId} - Update order"""
    print_section("TEST 4: Update Order")

    if not order_id:
        print_result("Update Order", False, error="No order ID provided")
        return False

    update_payload = {
        "orderType": {
            "taxable": "false",
            "isDefault": "false",
            "filterCategories": "false",
            "isHidden": "false",
            "isDeleted": "false"
        },
        "taxRemoved": "false",
        "note": "Updated via API test script"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}",
            json=update_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        success = response.status_code == 200
        data = response.json() if success else None
        error = response.text if not success else None

        print_result("Update Order", success, data, error)
        return success

    except Exception as e:
        print_result("Update Order", False, error=str(e))
        return False

def test_checkout_atomic_order():
    """Test POST /api/orders/atomic/checkouts - Checkout atomic order"""
    print_section("TEST 5: Checkout Atomic Order")

    checkout_payload = {
        "orderCart": {
            "orderType": {
                "taxable": "false",
                "isDefault": "false",
                "filterCategories": "false",
                "isHidden": "false",
                "isDeleted": "false"
            },
            "groupLineItems": "false"
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/atomic/checkouts",
            json=checkout_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        success = response.status_code in [200, 201]
        data = response.json() if success else None
        error = response.text if not success else None

        print_result("Checkout Atomic Order", success, data, error)
        return success

    except Exception as e:
        print_result("Checkout Atomic Order", False, error=str(e))
        return False

def test_delete_order(order_id):
    """Test DELETE /api/orders/{orderId} - Delete order"""
    print_section("TEST 6: Delete Order")

    if not order_id:
        print_result("Delete Order", False, error="No order ID provided")
        return False

    try:
        response = requests.delete(f"{BASE_URL}/api/orders/{order_id}", timeout=30)
        success = response.status_code in [200, 204]
        data = response.json() if success and response.text else {"message": "Order deleted"}
        error = response.text if not success else None

        print_result("Delete Order", success, data, error)
        return success

    except Exception as e:
        print_result("Delete Order", False, error=str(e))
        return False

def main():
    """Run all order API tests"""
    print("🚀 Starting Comprehensive Order API Tests")
    print("📡 Flask Server: " + BASE_URL)
    print("🔐 Using OAuth tokens from server configuration")

    results = {
        'passed': 0,
        'failed': 0,
        'total': 6
    }

    # Test 1: Get all orders
    orders_data = test_get_orders()
    results['passed' if orders_data is not None else 'failed'] += 1

    # Test 2: Create atomic order
    order_id = test_create_atomic_order()
    results['passed' if order_id else 'failed'] += 1

    # Test 3: Get single order (if we have an order ID)
    single_order = test_get_single_order(order_id)
    results['passed' if single_order is not None else 'failed'] += 1

    # Test 4: Update order (if we have an order ID)
    update_success = test_update_order(order_id)
    results['passed' if update_success else 'failed'] += 1

    # Test 5: Checkout atomic order
    checkout_success = test_checkout_atomic_order()
    results['passed' if checkout_success else 'failed'] += 1

    # Test 6: Delete order (if we have an order ID) - Run last since it removes the order
    delete_success = test_delete_order(order_id)
    results['passed' if delete_success else 'failed'] += 1

    # Final Results
    print_section("TEST RESULTS SUMMARY")
    print(f"✅ Passed: {results['passed']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")

    if results['passed'] == results['total']:
        print("🎉 All tests passed! Your Order API is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

    print("\n📋 Swagger UI Available at: http://localhost:5000/")
    print("🔍 Try the endpoints manually in Swagger for more detailed testing")

if __name__ == "__main__":
    main()