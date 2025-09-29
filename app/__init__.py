from flask import Flask, redirect, request, url_for, jsonify
from flask_restx import Api, Namespace, Resource
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all domains
    CORS(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Clover API Testing Suite',
        description='A Flask application for testing Clover APIs with Swagger documentation',
        doc='/swagger/'
    )

    # Register API namespaces
    from app.api.merchants import api as merchants_ns
    from app.api.inventory import api as inventory_ns
    from app.api.orders import api as orders_ns
    from app.api.payments import api as payments_ns
    from app.api.customers import api as customers_ns

    api.add_namespace(merchants_ns, path='/api/merchants')
    api.add_namespace(inventory_ns, path='/api/inventory')
    api.add_namespace(orders_ns, path='/api/orders')
    api.add_namespace(payments_ns, path='/api/payments')
    api.add_namespace(customers_ns, path='/api/customers')

    # OAuth namespace (documented in Swagger)
    oauth_ns = Namespace('auth', description='Clover OAuth authentication')

    @oauth_ns.route('/authorize')
    class OAuthAuthorize(Resource):
        def get(self):
            """Redirect to Clover OAuth authorize endpoint"""
            cfg = Config()
            merchant_id = request.args.get('merchant_id') or cfg.CLOVER_MERCHANT_ID

            # Build redirect URL to Clover authorize
            params = {
                'client_id': cfg.CLOVER_APP_ID,
                'redirect_uri': cfg.oauth_redirect_uri,
            }
            # If merchant comes from Clover launch, code is provided in callback; otherwise, include merchant_id if known
            if merchant_id:
                params['merchant_id'] = merchant_id

            from urllib.parse import urlencode
            url = f"{cfg.oauth_authorize_url}?{urlencode(params)}"
            return redirect(url)

    @oauth_ns.route('/callback')
    class OAuthCallback(Resource):
        def get(self):
            """Handle Clover OAuth callback and exchange code for tokens"""
            cfg = Config()
            code = request.args.get('code')
            merchant_id = request.args.get('merchant_id') or request.args.get('merchantId')
            if not code:
                # First launch from Clover typically sends merchant_id but not code.
                # Initiate authorize flow now.
                params = {
                    'client_id': cfg.CLOVER_APP_ID,
                    'redirect_uri': cfg.oauth_redirect_uri,
                }
                if merchant_id:
                    params['merchant_id'] = merchant_id
                from urllib.parse import urlencode
                auth_url = f"{cfg.oauth_authorize_url}?{urlencode(params)}"
                return redirect(auth_url)
            if not merchant_id:
                # Try to use configured merchant id if not provided
                merchant_id = cfg.CLOVER_MERCHANT_ID

            import requests as rq
            payload = {
                'client_id': cfg.CLOVER_APP_ID,
                'client_secret': cfg.CLOVER_APP_SECRET,
                'code': code,
            }
            headers = {'content-type': 'application/json'}
            resp = rq.post(cfg.oauth_token_url, json=payload, headers=headers, timeout=30)
            if resp.status_code != 200:
                return {'error': 'Token exchange failed', 'status': resp.status_code, 'body': resp.text}, 400

            data = resp.json()

            # Store tokens
            try:
                from app.token_store import save_tokens
                save_tokens(
                    merchant_id=merchant_id or 'unknown',
                    access_token=data.get('access_token'),
                    refresh_token=data.get('refresh_token'),
                    access_token_expiration=data.get('access_token_expiration'),
                    refresh_token_expiration=data.get('refresh_token_expiration')
                )
            except Exception as e:
                return {'error': f'Failed to store tokens: {str(e)}'}, 500

            # Optionally set env merchant id for session usage
            # Provide a simple success page/json
            return {
                'message': 'OAuth successful',
                'merchant_id': merchant_id,
                'access_token_expiration': data.get('access_token_expiration'),
                'refresh_token_expiration': data.get('refresh_token_expiration')
            }

    @oauth_ns.route('/tokens')
    class OAuthTokens(Resource):
        def get(self):
            """List stored tokens (redacted) for debugging"""
            try:
                from app.token_store import get_all_tokens
                tokens = get_all_tokens()
                redacted = {}
                for mid, t in tokens.items():
                    redacted[mid] = {
                        'access_token': (t.get('access_token')[:6] + '...' if t.get('access_token') else None),
                        'refresh_token': (t.get('refresh_token')[:6] + '...' if t.get('refresh_token') else None),
                        'access_token_expiration': t.get('access_token_expiration'),
                        'refresh_token_expiration': t.get('refresh_token_expiration'),
                    }
                return redacted
            except Exception as e:
                return {'error': str(e)}, 500

    @oauth_ns.route('/refresh')
    class OAuthRefresh(Resource):
        def post(self):
            """Refresh access token using refresh token"""
            try:
                from app.token_store import get_all_tokens, save_tokens
                import requests

                # Get merchant_id from request or use default
                merchant_id = request.args.get('merchant_id')
                if not merchant_id:
                    from app.token_store import get_default_merchant_id
                    merchant_id = get_default_merchant_id()

                if not merchant_id:
                    return {'error': 'No merchant_id provided and no default merchant found'}, 400

                # Get stored tokens
                tokens = get_all_tokens()
                token_data = tokens.get(merchant_id)

                if not token_data:
                    return {'error': f'No tokens found for merchant_id: {merchant_id}'}, 404

                refresh_token = token_data.get('refresh_token')
                if not refresh_token:
                    return {'error': 'No refresh token available'}, 400

                # Prepare refresh request
                config = Config()
                refresh_url = f"{config.oauth_token_base}/oauth/v2/refresh"

                payload = {
                    'client_id': config.CLOVER_APP_ID,
                    'refresh_token': refresh_token
                }

                headers = {'Content-Type': 'application/json'}

                # Make refresh request
                response = requests.post(refresh_url, json=payload, headers=headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    # Save new tokens
                    save_tokens(
                        merchant_id=merchant_id,
                        access_token=data.get('access_token'),
                        refresh_token=data.get('refresh_token', refresh_token),  # Keep old refresh token if not provided
                        access_token_expiration=data.get('access_token_expiration'),
                        refresh_token_expiration=data.get('refresh_token_expiration')
                    )

                    return {
                        'message': 'Token refreshed successfully',
                        'merchant_id': merchant_id,
                        'access_token_expiration': data.get('access_token_expiration'),
                        'refresh_token_expiration': data.get('refresh_token_expiration')
                    }
                else:
                    return {
                        'error': f'Token refresh failed: {response.text}',
                        'status_code': response.status_code
                    }, response.status_code

            except Exception as e:
                return {'error': f'Internal error during token refresh: {str(e)}'}, 500

    api.add_namespace(oauth_ns, path='/oauth')

    @app.route('/')
    def index():
        return {
            'message': 'Clover API Testing Suite',
            'swagger_docs': '/swagger/',
            'status': 'running'
        }

    @app.route('/health')
    def health():
        return {'status': 'healthy'}

    @app.route('/api/status')
    def api_status():
        """Check Clover API connection status"""
        from app.utils import CloverAPIClient
        client = CloverAPIClient()
        return client.get_api_status()

    return app