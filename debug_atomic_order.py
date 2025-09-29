#!/usr/bin/env python3
"""
Debug atomic order API endpoint
"""
import requests
import json

def test_atomic_order():
    url = "http://localhost:8080/api/orders/atomic/orders"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "order": {
            "state": "open",
            "taxRemoved": False,
            "isVat": False
        },
        "lineItems": [
            {
                "item": {
                    "id": "1FC5RCZ4XPZTT"
                },
                "name": "Cappuccino",
                "price": 499,
                "unitQty": 1
            },
            {
                "item": {
                    "id": "VVS0H9DW86CTY"
                },
                "name": "Espresso",
                "price": 399,
                "unitQty": 1
            }
        ]
    }

    print("Testing atomic order creation...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_atomic_order()