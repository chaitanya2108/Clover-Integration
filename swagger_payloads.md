# Clover Order API - Swagger UI Test Payloads

This file contains ready-to-use JSON payloads for testing all Order API endpoints in Swagger UI.

## 1. Create Atomic Order

**Endpoint:** `POST /api/orders/atomic`

```json
{
  "orderCart": {
    "currency": "USD",
    "title": "Italian Restaurant Order",
    "note": "Test order via Swagger UI",
    "clientCreatedTime": 1758691800000,
    "lineItems": [
      {
        "item": { "id": "M87Z9DK9BVKKE" },
        "name": "Margherita",
        "price": 1699,
        "unitQty": 1,
        "note": "Classic margherita pizza"
      },
      {
        "item": { "id": "4V55AWS7VCNM8" },
        "name": "Spaghetti Carbonara",
        "price": 1999,
        "unitQty": 1,
        "note": "Traditional carbonara"
      },
      {
        "item": { "id": "1FC5RCZ4XPZTT" },
        "name": "Cappuccino",
        "price": 499,
        "unitQty": 2,
        "note": "Two cappuccinos"
      }
    ],
    "groupLineItems": true
  }
}
```

## 2. Checkout Atomic Order

**Endpoint:** `POST /api/orders/atomic/checkouts`

```json
{
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
```

## 3. Update Order

**Endpoint:** `POST /api/orders/{orderId}`
_Replace {orderId} with an actual order ID from a created order_

```json
{
  "orderType": {
    "taxable": "false",
    "isDefault": "false",
    "filterCategories": "false",
    "isHidden": "false",
    "isDeleted": "false"
  },
  "taxRemoved": "false",
  "state": "locked",
  "title": "Updated Order Title",
  "note": "Order updated via Swagger UI"
}
```

## 4. Get Orders List

**Endpoint:** `GET /api/orders`
_Query parameters (optional):_

- `limit`: Number of orders to return (default: 100)
- `offset`: Number of orders to skip (default: 0)
- `filter`: Filter criteria
- `expand`: Fields to expand

**Example URL:** `GET /api/orders?limit=10&offset=0`

## 5. Get Single Order

**Endpoint:** `GET /api/orders/{orderId}`
_Replace {orderId} with an actual order ID_

**Example URL:** `GET /api/orders/ABC123XYZ`

## 6. Delete Order

**Endpoint:** `DELETE /api/orders/{orderId}`
_Replace {orderId} with an actual order ID_
_No request body required_

---

## Testing Workflow

1. **Start your Flask server:** `python main.py`
2. **Complete OAuth flow:** Visit `http://localhost:8080/oauth/authorize`
3. **Open Swagger UI:** `http://localhost:8080/`
4. **Test in this order:**
   1. Create Atomic Order (copy payload from section 1)
   2. Note the returned order ID
   3. Get Single Order (use the order ID)
   4. Update Order (use the order ID and payload from section 3)
   5. Get Orders List (see all your orders)
   6. Checkout Atomic Order (copy payload from section 2)
   7. Delete Order (use the order ID) - **Do this last!**

## Available Inventory Items (Your Restaurant)

Use these real item IDs in your atomic orders:

**Pizzas:**

- Margherita: `M87Z9DK9BVKKE` ($16.99)
- Pepperoni: `GVPJ6EF8JE9Q6` ($18.99)
- Supreme: `V0ZNMNFX0P4VE` ($22.99)

**Pasta:**

- Spaghetti Carbonara: `4V55AWS7VCNM8` ($19.99)
- Penne Arrabbiata: `1C7R8YQW9BRPJ` ($17.99)
- Fettuccine Alfredo: `HQTW4VG6YW5MY` ($20.99)

**Beverages:**

- Cappuccino: `1FC5RCZ4XPZTT` ($4.99)
- Espresso: `VVS0H9DW86CTY` ($3.99)
- Latte: `XKKEP0V5JY38M` ($5.99)

**Desserts:**

- Tiramisu: `Y6H4YK4TJQFSP` ($8.99)
- Panna Cotta: `7MNY8M4QF8WA6` ($7.99)
- Gelato: `FPXDFNH8BFRM0` ($6.99)
