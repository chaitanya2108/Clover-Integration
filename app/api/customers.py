import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from app.config import Config

MISSING_MID_MSG = "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env"

api = Namespace('customers', description='Clover Customers API operations')

# Define models for Swagger documentation
customer_model = api.model('Customer', {
    'id': fields.String(description='Customer ID'),
    'firstName': fields.String(description='First name'),
    'lastName': fields.String(description='Last name'),
    'marketingAllowed': fields.Boolean(description='Marketing allowed'),
    'customerSince': fields.Integer(description='Customer since timestamp'),
    'orders': fields.List(fields.String, description='Order references')
})

address_model = api.model('Address', {
    'id': fields.String(description='Address ID'),
    'address1': fields.String(description='Address line 1'),
    'address2': fields.String(description='Address line 2'),
    'address3': fields.String(description='Address line 3'),
    'city': fields.String(description='City'),
    'state': fields.String(description='State'),
    'zip': fields.String(description='ZIP code'),
    'country': fields.String(description='Country')
})

phone_number_model = api.model('PhoneNumber', {
    'id': fields.String(description='Phone number ID'),
    'phoneNumber': fields.String(description='Phone number')
})

email_address_model = api.model('EmailAddress', {
    'id': fields.String(description='Email address ID'),
    'emailAddress': fields.String(description='Email address'),
    'verifiedTime': fields.Integer(description='Verified timestamp')
})

@api.route('/')
class Customers(Resource):
    @api.doc('get_customers')
    def get(self):
        """Get all customers"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers"

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

    @api.doc('create_customer')
    @api.expect(customer_model)
    def post(self):
        """Create a new customer"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers"

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

@api.route('/<string:customer_id>')
class Customer(Resource):
    @api.doc('get_customer')
    def get(self, customer_id):
        """Get specific customer"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}"

            expand = request.args.get('expand', None)
            params = {}
            if expand:
                params['expand'] = expand

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

    @api.doc('update_customer')
    @api.expect(customer_model)
    def put(self, customer_id):
        """Update a customer"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}"

            response = requests.put(
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

    @api.doc('delete_customer')
    def delete(self, customer_id):
        """Delete a customer"""
        try:
            config = Config()
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{config.CLOVER_MERCHANT_ID}/customers/{customer_id}"

            response = requests.delete(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return {'message': 'Customer deleted successfully'}
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/<string:customer_id>/addresses')
class CustomerAddresses(Resource):
    @api.doc('get_customer_addresses')
    def get(self, customer_id):
        """Get customer addresses"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/addresses"

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

    @api.doc('create_customer_address')
    @api.expect(address_model)
    def post(self, customer_id):
        """Create customer address"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/addresses"

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

@api.route('/<string:customer_id>/phone_numbers')
class CustomerPhoneNumbers(Resource):
    @api.doc('get_customer_phone_numbers')
    def get(self, customer_id):
        """Get customer phone numbers"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/phone_numbers"

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

    @api.doc('create_customer_phone_number')
    @api.expect(phone_number_model)
    def post(self, customer_id):
        """Create customer phone number"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/phone_numbers"

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

@api.route('/<string:customer_id>/email_addresses')
class CustomerEmailAddresses(Resource):
    @api.doc('get_customer_email_addresses')
    def get(self, customer_id):
        """Get customer email addresses"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/email_addresses"

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

    @api.doc('create_customer_email_address')
    @api.expect(email_address_model)
    def post(self, customer_id):
        """Create customer email address"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/customers/{customer_id}/email_addresses"

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