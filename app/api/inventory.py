import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from app.config import Config
from app.api_utils import make_clover_request, get_merchant_id_or_abort, build_merchant_url

api = Namespace('inventory', description='Clover Inventory API operations')

# Define models for Swagger documentation
item_model = api.model('Item', {
    'id': fields.String(description='Item ID'),
    'name': fields.String(description='Item name'),
    'price': fields.Integer(description='Item price in cents'),
    'priceType': fields.String(description='Price type'),
    'defaultTaxRates': fields.Boolean(description='Use default tax rates'),
    'cost': fields.Integer(description='Item cost in cents'),
    'isRevenue': fields.Boolean(description='Is revenue item'),
    'stockCount': fields.Integer(description='Stock count')
})

category_model = api.model('Category', {
    'id': fields.String(description='Category ID'),
    'name': fields.String(description='Category name'),
    'sortOrder': fields.Integer(description='Sort order')
})

@api.route('/items')
class Items(Resource):
    @api.doc('get_items')
    def get(self):
        """Get all inventory items"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env")
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/items"

            # Get query parameters
            limit = request.args.get('limit', 100)
            offset = request.args.get('offset', 0)

            params = {
                'limit': limit,
                'offset': offset
            }

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

    @api.doc('create_item')
    @api.expect(item_model)
    def post(self):
        """Create a new inventory item"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env")
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/items"

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

@api.route('/items/<string:item_id>')
class Item(Resource):
    @api.doc('get_item')
    def get(self, item_id):
        """Get specific inventory item"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env")
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/items/{item_id}"

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

@api.route('/categories')
class Categories(Resource):
    @api.doc('get_categories')
    def get(self):
        """Get all inventory categories"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env")
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/categories"

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