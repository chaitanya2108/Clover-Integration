import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from app.config import Config
from app.api_utils import make_clover_request, get_merchant_id_or_abort, build_merchant_url

api = Namespace('orders', description='Clover Orders API operations')

# Define models for Swagger documentation (with examples for easy Swagger testing)
order_model = api.model('Order', {
    'id': fields.String(description='Order ID', example='ORD-12345'),
    'currency': fields.String(description='Currency code', example='USD'),
    'total': fields.Integer(description='Total amount in cents', example=1699),
    'state': fields.String(description='Order state', example='open'),
    'createdTime': fields.Integer(description='Created timestamp', example=1758581462000),
    'clientCreatedTime': fields.Integer(description='Client created timestamp', example=1758581461000),
    'modifiedTime': fields.Integer(description='Modified timestamp', example=1758581463000)
})

# Atomic order models
atomic_line_item = api.model('AtomicLineItem', {
    'id': fields.String(description='Line item ID', example='LI-1'),
    'item': fields.Raw(description='Item reference with id', example={'id': 'M87Z9DK9BVKKE'}),
    'name': fields.String(description='Item name', example='Margherita'),
    'price': fields.Integer(description='Item price in cents', example=1699),
    'unitQty': fields.Integer(description='Quantity', example=2),
    'note': fields.String(description='Line item note', example='No basil')
})

atomic_order_cart = api.model('AtomicOrderCart', {
    'id': fields.String(description='Order cart ID', example='CART-1'),
    'currency': fields.String(description='Currency code (e.g., USD)', example='USD'),
    'title': fields.String(description='Order title', example='Test Atomic Order'),
    'note': fields.String(description='Order note', example='Table 7'),
    'clientCreatedTime': fields.Integer(description='Client created timestamp', example=1758581462000),
    'lineItems': fields.List(fields.Nested(atomic_line_item), description='Line items', example=[
        {
            'item': {'id': '1FC5RCZ4XPZTT'},
            'name': 'Cappuccino',
            'price': 499,
            'unitQty': 1
        },
        {
            'item': {'id': 'M87Z9DK9BVKKE'},
            'name': 'Margherita',
            'price': 1699,
            'unitQty': 1
        }
    ]),
    'groupLineItems': fields.Boolean(description='Group line items', default=True, example=True)
})

atomic_order_model = api.model('AtomicOrder', {
    'orderCart': fields.Nested(atomic_order_cart, description='Order cart data', required=True)
}, example={
    'orderCart': {
        'currency': 'USD',
        'title': 'Test Atomic Order',
        'note': 'Table 7',
        'clientCreatedTime': 1758581462000,
        'lineItems': [
            {'item': {'id': '1FC5RCZ4XPZTT'}, 'name': 'Cappuccino', 'price': 499, 'unitQty': 1},
            {'item': {'id': 'M87Z9DK9BVKKE'}, 'name': 'Margherita', 'price': 1699, 'unitQty': 1}
        ],
        'groupLineItems': True
    }
})

# Atomic order checkout models
order_type_model = api.model('OrderType', {
    'taxable': fields.String(description='Whether the order type is taxable', default='false', example='false'),
    'isDefault': fields.String(description='Whether this is the default order type', default='false', example='false'),
    'filterCategories': fields.String(description='Whether to filter categories', default='false', example='false'),
    'isHidden': fields.String(description='Whether the order type is hidden', default='false', example='false'),
    'isDeleted': fields.String(description='Whether the order type is deleted', default='false', example='false')
})

checkout_order_cart = api.model('CheckoutOrderCart', {
    'id': fields.String(description='Order cart ID', example='CART-CHK-1'),
    'currency': fields.String(description='Currency code (e.g., USD)', example='USD'),
    'title': fields.String(description='Order title', example='Checkout Atomic Order'),
    'note': fields.String(description='Order note', example='Table 3'),
    'clientCreatedTime': fields.Integer(description='Client created timestamp', example=1758581462000),
    'orderType': fields.Nested(order_type_model, description='Order type configuration'),
    'lineItems': fields.List(fields.Nested(atomic_line_item), description='Line items', example=[
        {
            'item': {'id': '1FC5RCZ4XPZTT'},
            'name': 'Cappuccino',
            'price': 499,
            'unitQty': 1
        },
        {
            'item': {'id': 'M87Z9DK9BVKKE'},
            'name': 'Margherita',
            'price': 1699,
            'unitQty': 1
        }
    ]),
    'groupLineItems': fields.String(description='Whether to group line items', default='false', example='true')
})

atomic_checkout_model = api.model('AtomicCheckout', {
    'orderCart': fields.Nested(checkout_order_cart, description='Order cart data for checkout', required=True)
}, example={
    'orderCart': {
        'id': 'CART-CHK-1',
        'currency': 'USD',
        'title': 'Checkout Atomic Order',
        'note': 'Table 3',
        'clientCreatedTime': 1758581462000,
        'orderType': {
            'taxable': 'false',
            'isDefault': 'false',
            'filterCategories': 'false',
            'isHidden': 'false',
            'isDeleted': 'false'
        },
        'lineItems': [
            {'item': {'id': '1FC5RCZ4XPZTT'}, 'name': 'Cappuccino', 'price': 499, 'unitQty': 1},
            {'item': {'id': 'M87Z9DK9BVKKE'}, 'name': 'Margherita', 'price': 1699, 'unitQty': 1}
        ],
        'groupLineItems': 'true'
    }
})

# Order update model
order_update_model = api.model('OrderUpdate', {
    'orderType': fields.Nested(order_type_model, description='Order type configuration'),
    'taxRemoved': fields.String(description='Whether tax is removed', default='false', example='false'),
    'state': fields.String(description='Order state (e.g., open, locked, paid)', example='open'),
    'title': fields.String(description='Order title', example='Updated Title'),
    'note': fields.String(description='Order note', example='Updated note'),
    'lineItems': fields.List(fields.Nested(atomic_line_item), description='Order line items', example=[
        {'item': {'id': 'VVS0H9DW86CTY'}, 'name': 'Espresso', 'price': 399, 'unitQty': 1},
        {'item': {'id': 'Q4AND7VJE1GKE'}, 'name': 'Panna Cotta', 'price': 799, 'unitQty': 2}
    ])
})

line_item_model = api.model('LineItem', {
    'id': fields.String(description='Line item ID', example='LI-1'),
    'orderRef': fields.String(description='Order reference', example='ORD-12345'),
    'item': fields.Raw(description='Item reference (object with id)', example={'id': '1FC5RCZ4XPZTT'}),
    'name': fields.String(description='Item name', example='Cappuccino'),
    'price': fields.Integer(description='Item price in cents', example=499),
    'unitQty': fields.Integer(description='Quantity', example=1)
})

@api.route('/')
class Orders(Resource):
    @api.doc('get_orders', description='Gets a list of orders')
    def get(self):
        """Get all orders"""
        try:
            config = Config()
            merchant_id = get_merchant_id_or_abort(api)
            url = build_merchant_url(config, merchant_id, 'orders')

            # Get query parameters
            limit = request.args.get('limit', 100)
            offset = request.args.get('offset', 0)
            filter_param = request.args.get('filter', None)
            expand = request.args.get('expand', None)

            params = {
                'limit': limit,
                'offset': offset
            }

            if filter_param:
                params['filter'] = filter_param
            if expand:
                params['expand'] = expand

            response = make_clover_request(
                'GET',
                url,
                merchant_id,
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    # Removed POST /orders (unwanted)

@api.route('/<string:order_id>')
class Order(Resource):
    @api.doc('get_order', description='Get a single order by ID')
    def get(self, order_id):
        """Get specific order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}"

            expand = request.args.get('expand', None)
            params = {}
            if expand:
                params['expand'] = expand
            else:
                # Default to comprehensive expansion for complete order details
                params['expand'] = (
                    'lineItems,lineItems.item,lineItems.modifications,'
                    'discounts,orderType,payments,taxRates,serviceCharge,'
                    'device,merchant,employee'
                )

            response = requests.get(
                url,
                headers=config.get_headers(),
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('update_order', description='Update an order')
    @api.expect(order_update_model)
    def post(self, order_id):
        """Update an order (POST method as per Clover API)"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=request.json,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('delete_order', description='Delete an order')
    def delete(self, order_id):
        """Delete an order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}"

            response = requests.delete(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code in [200, 204]:
                return {'message': f'Order {order_id} deleted successfully'}
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

# Removed /orders/<order_id>/line_items (unwanted)
@api.route('/<string:order_id>/line_items')
class OrderLineItems(Resource):
    @api.doc('get_order_line_items', description='Get order line items')
    def get(self, order_id):
        """Get order line items"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}/line_items"

            response = requests.get(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('add_line_item', description='Add line item to order')
    @api.expect(line_item_model)
    def post(self, order_id):
        """Add line item to order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}/line_items"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=request.json,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/<string:order_id>/line_items/<string:line_item_id>')
class OrderLineItem(Resource):
    @api.doc('update_line_item', description='Update line item (e.g., quantity, note)')
    @api.expect(api.model('LineItemUpdate', {
        'unitQty': fields.Integer(description='Quantity', example=2),
        'note': fields.String(description='Line item note', example='Extra hot')
    }))
    def post(self, order_id, line_item_id):
        """Update a specific line item"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}/line_items/{line_item_id}"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=request.json,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('delete_line_item', description='Delete a line item from order')
    def delete(self, order_id, line_item_id):
        """Delete a specific line item"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}/line_items/{line_item_id}"

            response = requests.delete(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code in [200, 204]:
                return {'message': f'Line item {line_item_id} deleted successfully'}
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")


@api.route('/atomic')
class AtomicOrders(Resource):
    @api.doc('create_atomic_order', description='Create an atomic order')
    @api.expect(atomic_order_model)
    def post(self):
        """Create an atomic order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)

            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/atomic_order/orders"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=request.json,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")


@api.route('/atomic/checkouts')
class AtomicCheckouts(Resource):
    @api.doc('checkout_atomic_order', description='Checkout an atomic order')
    @api.expect(atomic_checkout_model)
    def post(self):
        """Checkout an atomic order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)

            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/atomic_order/checkouts"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=request.json,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")