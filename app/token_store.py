"""Simple file-based token storage for Clover OAuth tokens.
Not for production use. Replace with database/secure storage as needed.
"""

import json
import os
import threading
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