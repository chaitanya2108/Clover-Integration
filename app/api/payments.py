import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from app.config import Config
from werkzeug.exceptions import HTTPException
from app.api_utils import make_clover_request, get_merchant_id_or_abort, build_merchant_url

MISSING_MID_MSG = "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env"

api = Namespace('payments', description='Clover Payments API operations')

# Define models for Swagger documentation
payment_model = api.model('Payment', {
    'id': fields.String(description='Payment ID', example='pay_123'),
    'order': fields.Raw(description='Order reference', example={'id': 'ORD-12345'}),
    'amount': fields.Integer(description='Payment amount in cents', example=2199),
    'tipAmount': fields.Integer(description='Tip amount in cents', example=300),
    'cashbackAmount': fields.Integer(description='Cashback amount in cents', example=0),
    'externalPaymentId': fields.String(description='External payment ID', example='ext_abc'),
    'result': fields.String(description='Payment result', example='SUCCESS'),
    'createdTime': fields.Integer(description='Created timestamp', example=1758581462000),
    'clientCreatedTime': fields.Integer(description='Client created timestamp', example=1758581461000)
})

authorization_payment_summary = api.model('AuthorizationPaymentSummary', {
    'id': fields.String(description='Payment ID', example='pay_123'),
    'order': fields.Raw(description='Order reference', example={'id': 'ORD-12345'}),
    'amount': fields.Integer(description='Amount in cents', example=2199)
})

authorization_create_model = api.model('AuthorizationCreate', {
    'id': fields.String(description='Authorization ID (optional)', example='auth_123'),
    'payment': fields.Nested(authorization_payment_summary, description='Payment details', required=True),
    'tabName': fields.String(description='Tab name', example='Table 3'),
    'amount': fields.Integer(description='Authorization amount in cents', example=2199),
    'cardType': fields.String(description='Card type', example='VISA'),
    'last4': fields.String(description='Last 4 digits', example='4242'),
    'type': fields.String(description='Authorization type', example='TAB'),
    'note': fields.String(description='Note', example='Auth for dinner'),
    'externalReferenceId': fields.String(description='External reference', example='ext-ref-001')
})

authorization_update_model = api.model('AuthorizationUpdate', {
    'payment': fields.Raw(description='Payment-level options', example={
        'offline': 'false',
        'transactionSettings': {
            'disableCashBack': 'false',
            'cloverShouldHandleReceipts': 'true',
            'forcePinEntryOnSwipe': 'false',
            'disableRestartTransactionOnFailure': 'false',
            'allowOfflinePayment': 'false',
            'approveOfflinePaymentWithoutPrompt': 'false',
            'forceOfflinePayment': 'false',
            'disableReceiptSelection': 'false',
            'disableDuplicateCheck': 'false',
            'autoAcceptPaymentConfirmations': 'false',
            'autoAcceptSignature': 'false',
            'returnResultOnTransactionComplete': 'false',
            'disableCreditSurcharge': 'false'
        },
        'transactionInfo': {
            'isTokenBasedTx': 'false',
            'emergencyFlag': 'false'
        }
    }),
    'closingPayment': fields.Raw(description='Closing payment options', example={
        'offline': 'false',
        'transactionSettings': {
            'disableCashBack': 'false',
            'cloverShouldHandleReceipts': 'true',
            'forcePinEntryOnSwipe': 'false',
            'disableRestartTransactionOnFailure': 'false',
            'allowOfflinePayment': 'false',
            'approveOfflinePaymentWithoutPrompt': 'false',
            'forceOfflinePayment': 'false',
            'disableReceiptSelection': 'false',
            'disableDuplicateCheck': 'false',
            'autoAcceptPaymentConfirmations': 'false',
            'autoAcceptSignature': 'false',
            'returnResultOnTransactionComplete': 'false',
            'disableCreditSurcharge': 'false'
        },
        'transactionInfo': {
            'isTokenBasedTx': 'false',
            'emergencyFlag': 'false'
        }
    })
})

@api.route('/')
class Payments(Resource):
    @api.doc('get_payments', description='Get all payments')
    def get(self):
        """Get all payments"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/payments"

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

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/<string:payment_id>')
class Payment(Resource):
    @api.doc('get_payment', description='Get a single payment by ID')
    def get(self, payment_id):
        """Get specific payment"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/payments/{payment_id}"

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

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

# Removed refunds endpoints (unnecessary for this scope)

# Removed refunds collection endpoint (unnecessary for this scope)

@api.route('/orders/<string:order_id>/payments')
class OrderPayments(Resource):
    @api.doc('get_order_payments', description='Get all payments for an order')
    def get(self, order_id):
        """Get all payments for an order"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/orders/{order_id}/payments"

            response = requests.get(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/authorizations')
class Authorizations(Resource):
    @api.doc('get_authorizations', description='Get all authorizations')
    def get(self):
        """Get all authorizations"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/authorizations"

            response = requests.get(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('create_authorization', description='Create an authorization on a Payment')
    @api.expect(authorization_create_model)
    def post(self):
        """Create an authorization on a Payment"""
        try:
            payload = request.get_json(silent=True)
            if payload is None:
                api.abort(400, 'Invalid JSON body. Ensure Content-Type: application/json and valid JSON payload.')
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/authorizations"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

@api.route('/authorizations/<string:authorization_id>')
class Authorization(Resource):
    @api.doc('get_authorization', description='Get a single authorization by ID')
    def get(self, authorization_id):
        """Get a single authorization"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/authorizations/{authorization_id}"

            response = requests.get(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('update_authorization', description='Update an authorization')
    @api.expect(authorization_update_model)
    def post(self, authorization_id):
        """Update an authorization"""
        try:
            payload = request.get_json(silent=True)
            if payload is None:
                api.abort(400, 'Invalid JSON body. Ensure Content-Type: application/json and valid JSON payload.')
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/authorizations/{authorization_id}"

            response = requests.post(
                url,
                headers=config.get_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")

    @api.doc('delete_authorization', description='Delete an authorization')
    def delete(self, authorization_id):
        """Delete an authorization"""
        try:
            config = Config()
            merchant_id = config.get_merchant_id()
            if not merchant_id:
                api.abort(400, MISSING_MID_MSG)
            url = f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/authorizations/{authorization_id}"

            response = requests.delete(
                url,
                headers=config.get_headers(),
                timeout=30
            )

            if response.status_code in [200, 204]:
                return {'message': f'Authorization {authorization_id} deleted successfully'}
            else:
                api.abort(response.status_code, f"Clover API error: {response.text}")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            api.abort(500, f"Internal error: {str(e)}")