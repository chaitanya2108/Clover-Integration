import requests
from flask import current_app
from flask_restx import Namespace, Resource, fields
from app.config import Config

MISSING_MID_MSG = "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env"

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
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}"

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

@api.route('/properties')
class MerchantProperties(Resource):
    @api.doc('get_merchant_properties')
    def get(self):
        """Get merchant properties"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/properties"

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