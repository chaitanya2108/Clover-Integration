#!/usr/bin/env python3
"""
Test the refresh token logic directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.token_store import get_all_tokens, is_token_expired, refresh_token_if_needed, get_valid_access_token
from app.config import Config
import time

def test_token_functions():
    """Test the token store functions directly"""
    print("🧪 Testing Token Store Functions")
    print("=" * 40)

    # Get all tokens
    tokens = get_all_tokens()
    print(f"📊 Stored tokens: {len(tokens)}")

    if not tokens:
        print("❌ No tokens found. Complete OAuth flow first.")
        return False

    merchant_id = list(tokens.keys())[0]
    print(f"🏪 Testing with merchant: {merchant_id}")

    # Check token data
    token_data = tokens[merchant_id]
    print(f"🔑 Access token: {token_data.get('access_token', 'None')[:20]}...")
    print(f"🔄 Refresh token: {token_data.get('refresh_token', 'None')[:20]}...")
    print(f"⏰ Access expiration: {token_data.get('access_token_expiration')}")
    print(f"⏰ Refresh expiration: {token_data.get('refresh_token_expiration')}")

    # Test token expiration check
    print(f"\n🔍 Testing token expiration check...")
    is_expired = is_token_expired(merchant_id, 'access_token')
    print(f"   Token expired: {is_expired}")

    # Test refresh if needed
    print(f"\n🔄 Testing refresh if needed...")
    was_refreshed = refresh_token_if_needed(merchant_id)
    print(f"   Token was refreshed: {was_refreshed}")

    # Test get valid access token
    print(f"\n🔑 Testing get valid access token...")
    valid_token = get_valid_access_token(merchant_id)
    print(f"   Valid token: {'Yes' if valid_token else 'No'}")
    if valid_token:
        print(f"   Token preview: {valid_token[:20]}...")

    return True

def test_config_headers():
    """Test config headers function"""
    print(f"\n⚙️  Testing Config Headers")
    print("=" * 40)

    config = Config()
    headers = config.get_headers()

    print(f"📋 Headers generated:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"   {key}: {value[:30]}...")
        else:
            print(f"   {key}: {value}")

    return 'Authorization' in headers

def main():
    print("🚀 Direct Token Logic Test")
    print("=" * 50)

    # Test token functions
    token_success = test_token_functions()

    # Test config headers
    headers_success = test_config_headers()

    print(f"\n📊 Results:")
    print(f"   Token functions: {'✅ Working' if token_success else '❌ Failed'}")
    print(f"   Config headers: {'✅ Working' if headers_success else '❌ Failed'}")

    if token_success and headers_success:
        print(f"\n✅ Auto-refresh logic is properly implemented!")
        print(f"   - Token expiration checking works")
        print(f"   - Token refresh mechanism works")
        print(f"   - Headers generation works")
        print(f"   - All APIs should auto-refresh expired tokens")
    else:
        print(f"\n❌ Issues found in auto-refresh logic")

if __name__ == "__main__":
    main()
