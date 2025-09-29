# Clover API Testing Suite

A Flask application for testing Clover APIs with Swagger documentation integration.

## Features

- **Swagger UI**: Interactive API documentation at `/swagger/`
- **Modular Structure**: Organized API endpoints by functionality
- **Environment Configuration**: Easy setup with `.env` file
- **Error Handling**: Comprehensive error handling for API calls
- **CORS Support**: Enabled for frontend integration

## API Endpoints

### Merchants

- `GET /api/merchants/info` - Get merchant information
- `GET /api/merchants/properties` - Get merchant properties

### Inventory

- `GET /api/inventory/items` - Get all inventory items
- `POST /api/inventory/items` - Create new inventory item
- `GET /api/inventory/items/{item_id}` - Get specific item
- `GET /api/inventory/categories` - Get all categories

### Orders

- `GET /api/orders/` - Get all orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{order_id}` - Get specific order
- `PUT /api/orders/{order_id}` - Update order
- `GET /api/orders/{order_id}/line_items` - Get order line items
- `POST /api/orders/{order_id}/line_items` - Add line item to order

### Payments

- `GET /api/payments/` - Get all payments
- `GET /api/payments/{payment_id}` - Get specific payment
- `GET /api/payments/{payment_id}/refunds` - Get payment refunds
- `POST /api/payments/{payment_id}/refunds` - Create refund
- `GET /api/payments/refunds` - Get all refunds

### Customers

- `GET /api/customers/` - Get all customers
- `POST /api/customers/` - Create new customer
- `GET /api/customers/{customer_id}` - Get specific customer
- `PUT /api/customers/{customer_id}` - Update customer
- `DELETE /api/customers/{customer_id}` - Delete customer
- `GET /api/customers/{customer_id}/addresses` - Get customer addresses
- `POST /api/customers/{customer_id}/addresses` - Create customer address
- `GET /api/customers/{customer_id}/phone_numbers` - Get customer phone numbers
- `POST /api/customers/{customer_id}/phone_numbers` - Create customer phone number
- `GET /api/customers/{customer_id}/email_addresses` - Get customer email addresses
- `POST /api/customers/{customer_id}/email_addresses` - Create customer email address

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `.env` file and update with your Clover API credentials:

   ```
   CLOVER_ACCESS_TOKEN=your_access_token_here
   CLOVER_MERCHANT_ID=your_merchant_id_here
   CLOVER_APP_ID=your_app_id_here
   CLOVER_APP_SECRET=your_app_secret_here
   SITE_URL=http://localhost:8080
   OAUTH_CALLBACK_PATH=/oauth/callback
   ```

3. **Run the application:**

   ```bash
   python main.py
   ```

4. **Access the application:**
   - Main app: http://localhost:8080
   - Swagger docs: http://localhost:8080/swagger/
   - Health check: http://localhost:8080/health

## Configuration

### Environment Variables

- `CLOVER_BASE_URL`: Production Clover API URL (default: https://api.clover.com)
- `CLOVER_SANDBOX_URL`: Sandbox Clover API URL (default: https://sandbox.dev.clover.com)
- `CLOVER_ACCESS_TOKEN`: Your Clover access token
- `CLOVER_MERCHANT_ID`: Your merchant ID
- `CLOVER_APP_ID`: Your app ID
- `CLOVER_APP_SECRET`: Your app secret
- `CLOVER_API_VERSION`: API version (default: v3)
- `USE_SANDBOX`: Use sandbox environment (default: True)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable Flask debug mode
- `SECRET_KEY`: Flask secret key
- `SITE_URL`: Base URL for your app (default: http://localhost:8080)
- `OAUTH_CALLBACK_PATH`: OAuth callback path (default: /oauth/callback)

## OAuth Authentication

1. In your Clover developer dashboard, set Alternate Launch Path to `/oauth/callback` and Site URL to `http://localhost:8080` (for local testing).
2. Start the app and navigate to one of the following:
   - From Clover launch, Clover will redirect to `/oauth/callback?code=...&merchant_id=...` and the app will exchange the code automatically.
   - Or initiate manually: `http://localhost:8080/oauth/authorize?merchant_id=YOUR_MERCHANT_ID` which redirects to Clover, then back to `/oauth/callback`.
3. After successful exchange, tokens are stored locally in `tokens.json` (gitignored).
4. You can verify tokens at `GET /oauth/tokens` (redacted) and API status at `GET /api/status`.

### Token Refresh

The application includes automatic token refresh functionality:

- **Automatic Refresh**: All API calls automatically refresh expired access tokens
- **Manual Refresh**: Use `POST /oauth/refresh` to manually refresh tokens
- **Token Expiration**: Tokens are refreshed 60 seconds before expiration
- **Retry Logic**: Failed API calls due to expired tokens are automatically retried once

**Refresh Endpoint:**

```bash
curl -X POST http://localhost:8080/oauth/refresh
```

**Response:**

```json
{
  "message": "Token refreshed successfully",
  "merchant_id": "YOUR_MERCHANT_ID",
  "access_token_expiration": 1758581462000,
  "refresh_token_expiration": 1758581462000
}
```

## Testing with Swagger

1. Navigate to http://localhost:8080/swagger/
2. Expand any API section (e.g., "merchants", "inventory", etc.)
3. Click on an endpoint to test
4. Click "Try it out"
5. Fill in required parameters
6. Click "Execute" to make the API call
7. View the response in the "Response body" section

## Project Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration management
│   └── api/
│       ├── merchants.py     # Merchant API endpoints
│       ├── inventory.py     # Inventory API endpoints
│       ├── orders.py        # Orders API endpoints
│       ├── payments.py      # Payments API endpoints
│       └── customers.py     # Customers API endpoints
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Error Handling

The application includes comprehensive error handling:

- **API Errors**: Clover API errors are properly forwarded with status codes
- **Validation**: Request validation using Flask-RESTX models
- **Timeouts**: 30-second timeout for API calls
- **Exception Handling**: Internal server errors are caught and reported

## Development

### Adding New Endpoints

1. Create or modify files in `app/api/`
2. Define Swagger models using `api.model()`
3. Add endpoints using `@api.route()` decorators
4. Include proper error handling and documentation

### Testing

Use the Swagger UI for interactive testing, or use tools like:

- Postman
- curl
- HTTPie

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use sandbox environment for testing
- Rotate access tokens regularly
- Monitor API usage and rate limits

## Next Steps

After setting up the basic structure, you can:

1. Add authentication middleware
2. Implement request/response logging
3. Add rate limiting
4. Create automated tests
5. Add more Clover API endpoints as needed
