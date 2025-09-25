#!/usr/bin/env python3
"""
Test atomic order creation using actual inventory items from your Clover merchant
Use this script to test or copy the JSON payload for Swagger UI testing
"""
import requests
import json
import time

# Flask server base URL
BASE_URL = "http://localhost:5000"

def create_test_atomic_order():
    """
    Create atomic order with real inventory items.
    This payload can be copied and used directly in Swagger UI.
    """

    # This is the exact JSON payload you can use in Swagger UI
    atomic_order_payload = {
        "orderCart": {
            "currency": "USD",
            "title": "Italian Restaurant Test Order",
            "note": "Test order created via Swagger API testing",
            "clientCreatedTime": int(time.time() * 1000),  # Current timestamp
            "lineItems": [
                {
                    "item": {"id": "M87Z9DK9BVKKE"},  # Margherita Pizza
                    "name": "Margherita",
                    "price": 1699,  # $16.99 in cents
                    "unitQty": 1,
                    "note": "Classic margherita pizza"
                },
                {
                    "item": {"id": "4V55AWS7VCNM8"},  # Spaghetti Carbonara
                    "name": "Spaghetti Carbonara",
                    "price": 1999,  # $19.99 in cents
                    "unitQty": 1,
                    "note": "Traditional carbonara pasta"
                },
                {
                    "item": {"id": "1FC5RCZ4XPZTT"},  # Cappuccino
                    "name": "Cappuccino",
                    "price": 499,   # $4.99 in cents
                    "unitQty": 2,
                    "note": "Two cappuccinos"
                }
            ],
            "groupLineItems": True
        }
    }

    print("=" * 80)
    print("SWAGGER UI TEST PAYLOAD FOR ATOMIC ORDER CREATION")
    print("=" * 80)
    print("Copy the JSON below and paste it into Swagger UI:")
    print()
    print(json.dumps(atomic_order_payload, indent=2))
    print()
    print("=" * 80)
    print("Order Summary:")
    print("- 1x Margherita Pizza: $16.99")
    print("- 1x Spaghetti Carbonara: $19.99")
    print("- 2x Cappuccino: $4.99 each")
    total = (1699 + 1999 + 499*2) / 100
    print(f"- Total Expected: ${total:.2f}")
    print("=" * 80)

    return atomic_order_payload

def test_via_flask_api():
    """Test the atomic order creation via our Flask API"""
    payload = create_test_atomic_order()

    print("\nTesting via Flask API...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/atomic",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"Response Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Order ID: {result.get('id', 'N/A')}")
            print(f"State: {result.get('state', 'N/A')}")
            if 'total' in result:
                print(f"Total: ${result['total']/100:.2f}")
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("Make sure your Flask server is running on http://localhost:5000")

if __name__ == "__main__":
    print("Clover Atomic Order Test Script")
    print("Choose an option:")
    print("1. Display Swagger UI payload (copy-paste ready)")
    print("2. Test via Flask API (requires server running)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        create_test_atomic_order()
        print("\n📋 Copy the JSON payload above and use it in Swagger UI")
        print("🌐 Go to: http://localhost:5000/ -> Try it out on POST /api/orders/atomic")

    elif choice == "2":
        test_via_flask_api()

    else:
        # Default: show payload
        create_test_atomic_order()
        print("\n📋 Copy the JSON payload above and use it in Swagger UI")
        print("🌐 Go to: http://localhost:5000/ -> Try it out on POST /api/orders/atomic")