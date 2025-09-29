import requests
from flask import current_app
from flask_restx import Namespace, Resource, fields
from app.config import Config
from app.api_utils import make_clover_request, get_merchant_id_or_abort, build_merchant_url

api = Namespace('merchants', description='Clover Merchant API operations')

# Define models for Swagger documentation
merchant_model = api.model('Merchant', {
    'id': fields.String(description='Merchant ID'),
    'name': fields.String(description='Merchant name'),
    'address': fields.String(description='Merchant address'),
    'phone': fields.String(description='Merchant phone number'),
    'website': fields.String(description='Merchant website'),
    'timezone': fields.String(description='Merchant timezone')
})

@api.route('/info')
class MerchantInfo(Resource):
    @api.doc('get_merchant_info')
    @api.marshal_with(merchant_model)
    def get(self):
        """Get merchant information"""
        try:
            config = Config()
            merchant_id = get_merchant_id_or_abort(api)
            url = build_merchant_url(config, merchant_id)

            response = make_clover_request('GET', url, merchant_id)

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/properties')
class MerchantProperties(Resource):
    @api.doc('get_merchant_properties')
    def get(self):
        """Get merchant properties"""
        try:
            config = Config()
            merchant_id = get_merchant_id_or_abort(api)
            url = build_merchant_url(config, merchant_id, 'properties')

            response = make_clover_request('GET', url, merchant_id)

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")