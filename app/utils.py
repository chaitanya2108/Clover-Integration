import requests
from typing import Dict, Any, Optional
from app.config import Config

class CloverAPIClient:
    """Utility class for making Clover API requests"""

    def __init__(self):
        self.config = Config()
        self.base_url = self.config.clover_api_url
        self.api_version = self.config.CLOVER_API_VERSION
        self.merchant_id = self.config.get_merchant_id()

    def _get_url(self, endpoint: str) -> str:
        """Construct full API URL"""
        return f"{self.base_url}/{self.api_version}/merchants/{self.merchant_id}/{endpoint}"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to Clover API with automatic token refresh"""
        url = self._get_url(endpoint)
        headers = self.config.get_headers()

        # Update headers if provided
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30

        response = requests.request(method, url, headers=headers, **kwargs)

        # If we get a 401 (Unauthorized), try to refresh token and retry once
        if response.status_code == 401:
            try:
                from app.token_store import refresh_token_if_needed
                merchant_id = self.config.get_merchant_id()
                if merchant_id and refresh_token_if_needed(merchant_id):
                    # Token was refreshed, get new headers and retry
                    headers = self.config.get_headers()
                    if 'headers' in kwargs:
                        headers.update(kwargs.get('headers', {}))
                    response = requests.request(method, url, headers=headers, **kwargs)
            except Exception as e:
                # If refresh fails, return original response
                print(f"Token refresh attempt failed: {str(e)}")

        return response

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request"""
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make POST request"""
        return self._make_request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, json=data)

    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint)

    def get_merchant_info(self) -> Dict[str, Any]:
        """Get merchant information"""
        response = self.get('')
        response.raise_for_status()
        return response.json()

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.get('')
            return response.status_code == 200
        except Exception:
            return False

    def get_api_status(self) -> Dict[str, Any]:
        """Get API connection status and basic info"""
        try:
            merchant_info = self.get_merchant_info()
            return {
                'status': 'connected',
                'merchant_name': merchant_info.get('name', 'Unknown'),
                'merchant_id': self.merchant_id,
                'api_version': self.api_version,
                'environment': 'sandbox' if self.config.USE_SANDBOX else 'production'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'merchant_id': self.merchant_id,
                'api_version': self.api_version,
                'environment': 'sandbox' if self.config.USE_SANDBOX else 'production'
            }