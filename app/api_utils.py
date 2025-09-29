"""Utility functions for API requests with automatic token refresh"""

import requests
from typing import Optional, Dict, Any
from app.config import Config


def make_clover_request(method: str, url: str, merchant_id: str, **kwargs) -> requests.Response:
    """
    Make a request to Clover API with automatic token refresh on 401 errors.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Full URL to request
        merchant_id: Merchant ID for token refresh
        **kwargs: Additional arguments for requests.request()

    Returns:
        requests.Response object
    """
    config = Config()

    # Set default timeout if not provided
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 30

    # Get headers (this will auto-refresh if needed)
    headers = config.get_headers()
    if 'headers' in kwargs:
        headers.update(kwargs.pop('headers'))

    # Make initial request
    response = requests.request(method, url, headers=headers, **kwargs)

    # If we get a 401 (Unauthorized), try to refresh token and retry once
    if response.status_code == 401:
        try:
            from app.token_store import refresh_token_if_needed
            if refresh_token_if_needed(merchant_id):
                # Token was refreshed, get new headers and retry
                headers = config.get_headers()
                if 'headers' in kwargs:
                    headers.update(kwargs.get('headers', {}))
                response = requests.request(method, url, headers=headers, **kwargs)
        except Exception as e:
            # If refresh fails, return original response
            print(f"Token refresh attempt failed: {str(e)}")

    return response


def get_merchant_id_or_abort(api) -> str:
    """Get merchant ID or abort with error message"""
    config = Config()
    merchant_id = config.get_merchant_id()
    if not merchant_id:
        MISSING_MID_MSG = "Merchant ID not set. Complete OAuth flow or set CLOVER_MERCHANT_ID in .env"
        api.abort(400, MISSING_MID_MSG)
    return merchant_id


def build_merchant_url(config: Config, merchant_id: str, endpoint: str = "") -> str:
    """Build full URL for merchant API endpoint"""
    return f"{config.clover_api_url}/{config.CLOVER_API_VERSION}/merchants/{merchant_id}/{endpoint}".rstrip('/')
