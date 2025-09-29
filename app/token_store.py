"""Simple file-based token storage for Clover OAuth tokens.
Not for production use. Replace with database/secure storage as needed.
"""

import json
import os
import threading
import time
import requests
from typing import Optional, Dict, Any

_LOCK = threading.Lock()
_TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'tokens.json')
_TOKEN_FILE = os.path.abspath(_TOKEN_FILE)


def _load_tokens() -> Dict[str, Any]:
    if not os.path.exists(_TOKEN_FILE):
        return {}
    try:
        with open(_TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_tokens(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(_TOKEN_FILE), exist_ok=True)
    with open(_TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def save_tokens(merchant_id: str, access_token: str, refresh_token: str,
                access_token_expiration: Optional[int] = None,
                refresh_token_expiration: Optional[int] = None) -> None:
    with _LOCK:
        data = _load_tokens()
        data[merchant_id] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expiration': access_token_expiration,
            'refresh_token_expiration': refresh_token_expiration
        }
        _save_tokens(data)


def get_access_token(merchant_id: str) -> Optional[str]:
    with _LOCK:
        data = _load_tokens()
        entry = data.get(merchant_id)
        return entry.get('access_token') if entry else None


def get_refresh_token(merchant_id: str) -> Optional[str]:
    with _LOCK:
        data = _load_tokens()
        entry = data.get(merchant_id)
        return entry.get('refresh_token') if entry else None


def get_default_merchant_id() -> Optional[str]:
    with _LOCK:
        data = _load_tokens()
        # Return first merchant_id if any
        return next(iter(data.keys())) if data else None


def get_all_tokens() -> Dict[str, Any]:
    with _LOCK:
        return _load_tokens()


def is_token_expired(merchant_id: str, token_type: str = 'access_token') -> bool:
    """Check if a token is expired based on expiration timestamp"""
    with _LOCK:
        data = _load_tokens()
        entry = data.get(merchant_id)
        if not entry:
            return True

        expiration_key = f'{token_type}_expiration'
        expiration = entry.get(expiration_key)

        if not expiration:
            # If no expiration info, assume token is valid
            return False

        # Add 60 second buffer before actual expiration
        current_time = int(time.time())
        return current_time >= (expiration - 60)


def refresh_token_if_needed(merchant_id: str) -> bool:
    """
    Refresh access token if it's expired or about to expire.
    Returns True if token was refreshed, False if no refresh was needed.
    """
    with _LOCK:
        # Check if access token is expired
        if not is_token_expired(merchant_id, 'access_token'):
            return False

        data = _load_tokens()
        entry = data.get(merchant_id)
        if not entry:
            return False

        refresh_token = entry.get('refresh_token')
        if not refresh_token:
            return False

        try:
            # Import here to avoid circular imports
            from app.config import Config
            config = Config()

            refresh_url = f"{config.oauth_token_base}/oauth/v2/refresh"
            payload = {
                'client_id': config.CLOVER_APP_ID,
                'refresh_token': refresh_token
            }
            headers = {'Content-Type': 'application/json'}

            response = requests.post(refresh_url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                new_data = response.json()

                # Update tokens in the data dict
                data[merchant_id].update({
                    'access_token': new_data.get('access_token'),
                    'refresh_token': new_data.get('refresh_token', refresh_token),
                    'access_token_expiration': new_data.get('access_token_expiration'),
                    'refresh_token_expiration': new_data.get('refresh_token_expiration')
                })

                _save_tokens(data)
                return True
            else:
                # Log error but don't raise exception
                print(f"Token refresh failed for merchant {merchant_id}: {response.text}")
                return False

        except Exception as e:
            print(f"Error refreshing token for merchant {merchant_id}: {str(e)}")
            return False


def get_valid_access_token(merchant_id: str) -> Optional[str]:
    """
    Get a valid access token, refreshing if necessary.
    Returns None if no valid token can be obtained.
    """
    # Try to refresh token if needed
    refresh_token_if_needed(merchant_id)

    # Return the (potentially refreshed) access token
    return get_access_token(merchant_id)