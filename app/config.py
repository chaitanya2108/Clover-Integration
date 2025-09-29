import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clover-api-test-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # Clover API configuration
    CLOVER_BASE_URL = os.environ.get('CLOVER_BASE_URL', 'https://api.clover.com')
    CLOVER_SANDBOX_URL = os.environ.get('CLOVER_SANDBOX_URL', 'https://sandbox.dev.clover.com')
    CLOVER_ACCESS_TOKEN = os.environ.get('CLOVER_ACCESS_TOKEN')
    CLOVER_MERCHANT_ID = os.environ.get('CLOVER_MERCHANT_ID')
    CLOVER_APP_ID = os.environ.get('CLOVER_APP_ID')
    CLOVER_APP_SECRET = os.environ.get('CLOVER_APP_SECRET')
    CLOVER_API_VERSION = os.environ.get('CLOVER_API_VERSION', 'v3')

    # Use sandbox by default for testing
    USE_SANDBOX = os.environ.get('USE_SANDBOX', 'True').lower() == 'true'

    # OAuth / app URLs
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8080')
    OAUTH_CALLBACK_PATH = os.environ.get('OAUTH_CALLBACK_PATH', '/oauth/callback')

    @property
    def clover_api_url(self):
        return self.CLOVER_SANDBOX_URL if self.USE_SANDBOX else self.CLOVER_BASE_URL

    @property
    def oauth_authorize_base(self) -> str:
        """Base URL for OAuth authorize endpoint depending on environment."""
        # Sandbox uses sandbox.dev.clover.com for authorize
        return 'https://sandbox.dev.clover.com' if self.USE_SANDBOX else 'https://www.clover.com'

    @property
    def oauth_token_base(self) -> str:
        """Base URL for OAuth token endpoint depending on environment."""
        # Sandbox uses apisandbox.dev.clover.com for token exchange per Clover docs
        return 'https://apisandbox.dev.clover.com' if self.USE_SANDBOX else 'https://api.clover.com'

    @property
    def oauth_authorize_url(self) -> str:
        return f"{self.oauth_authorize_base}/oauth/v2/authorize"

    @property
    def oauth_token_url(self) -> str:
        return f"{self.oauth_token_base}/oauth/v2/token"

    @property
    def oauth_redirect_uri(self) -> str:
        # Ensure there is exactly one '/'
        return f"{self.SITE_URL.rstrip('/')}{self.OAUTH_CALLBACK_PATH}"

    @classmethod
    def get_headers(cls):
        """Get common headers for Clover API requests with auto-refresh"""
        token = cls.CLOVER_ACCESS_TOKEN
        # Try dynamic token from token store if not provided in env
        if not token:
            try:
                from app.token_store import get_valid_access_token, get_default_merchant_id
                merchant_id = cls.CLOVER_MERCHANT_ID or get_default_merchant_id()
                if merchant_id:
                    token = get_valid_access_token(merchant_id)
            except Exception:
                token = None

        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    @classmethod
    def get_merchant_id(cls):
        """Resolve the merchant ID from environment or stored tokens."""
        if cls.CLOVER_MERCHANT_ID:
            return cls.CLOVER_MERCHANT_ID
        try:
            from app.token_store import get_default_merchant_id
            return get_default_merchant_id()
        except Exception:
            return None