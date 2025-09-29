#!/usr/bin/env python3
"""
Test script for token refresh functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_refresh_endpoint():
    """Test the /oauth/refresh endpoint"""
    print("🧪 Testing Token Refresh Endpoint")
    print("=" * 50)

    # Test refresh endpoint
    refresh_url = f"{BASE_URL}/oauth/refresh"

    try:
        print(f"📡 Making POST request to: {refresh_url}")
        response = requests.post(refresh_url, timeout=30)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            print("✅ Token refresh endpoint is working!")
            data = response.json()
            print(f"🔄 Refresh successful for merchant: {data.get('merchant_id')}")
        elif response.status_code == 404:
            print("⚠️  No tokens found - you need to complete OAuth flow first")
            print("💡 Visit: http://localhost:8080/oauth/authorize")
        else:
            print(f"❌ Refresh failed: {response.text}")

    except Exception as e:
        print(f"❌ Error testing refresh endpoint: {str(e)}")

def test_token_list():
    """Test the /oauth/tokens endpoint"""
    print("\n🔍 Testing Token List Endpoint")
    print("=" * 50)

    tokens_url = f"{BASE_URL}/oauth/tokens"

    try:
        print(f"📡 Making GET request to: {tokens_url}")
        response = requests.get(tokens_url, timeout=30)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            print("✅ Token list endpoint is working!")
            data = response.json()
            print(f"🔑 Found {len(data)} stored token(s)")
            for merchant_id, token_info in data.items():
                print(f"   - Merchant: {merchant_id}")
                print(f"     Access Token: {token_info.get('access_token')}")
                print(f"     Refresh Token: {token_info.get('refresh_token')}")
        else:
            print(f"❌ Token list failed: {response.text}")

    except Exception as e:
        print(f"❌ Error testing token list: {str(e)}")

def test_merchant_api():
    """Test merchant API to see if auto-refresh works"""
    print("\n🏪 Testing Merchant API (Auto-refresh)")
    print("=" * 50)

    merchant_url = f"{BASE_URL}/api/merchants/info"

    try:
        print(f"📡 Making GET request to: {merchant_url}")
        response = requests.get(merchant_url, timeout=30)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Merchant API is working!")
            data = response.json()
            print(f"🏪 Merchant: {data.get('name', 'Unknown')}")
            print(f"🆔 Merchant ID: {data.get('id')}")
        elif response.status_code == 400:
            print("⚠️  No merchant ID configured - complete OAuth flow first")
        else:
            print(f"❌ Merchant API failed: {response.text}")

    except Exception as e:
        print(f"❌ Error testing merchant API: {str(e)}")

def main():
    print("🚀 Token Refresh Functionality Test")
    print("=" * 60)
    print(f"🎯 Testing against: {BASE_URL}")
    print()

    # Test endpoints
    test_token_list()
    test_refresh_endpoint()
    test_merchant_api()

    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print("1. /oauth/tokens - Lists stored tokens (redacted)")
    print("2. /oauth/refresh - Refreshes access token")
    print("3. /api/merchants/info - Tests auto-refresh in API calls")
    print()
    print("💡 To test refresh functionality:")
    print("   1. Complete OAuth flow: http://localhost:8080/oauth/authorize")
    print("   2. Wait for token to expire (or manually refresh)")
    print("   3. Make API calls - they should auto-refresh expired tokens")

if __name__ == "__main__":
    main()
