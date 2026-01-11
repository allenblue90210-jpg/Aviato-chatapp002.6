#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class SneakerIconBackendTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        resp_json = response.json()
                        if isinstance(resp_json, dict) and len(str(resp_json)) < 200:
                            print(f"   Response: {resp_json}")
                    except:
                        pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self):
        """Test login with demo credentials"""
        # OAuth2 expects form data, not JSON
        url = f"{self.base_url}/api/auth/login"
        self.tests_run += 1
        print(f"\n🔍 Testing Login with Demo User...")
        
        try:
            response = requests.post(
                url, 
                data={"username": "demo@aviato.com", "password": "password"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"   Token obtained: {self.token[:20]}...")
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
            
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_get_users(self):
        """Test getting users list"""
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "api/users",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
        return success

    def test_get_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )
        if success and 'email' in response:
            print(f"   User: {response.get('name')} ({response.get('email')})")
        return success

def main():
    print("🚀 Starting Sneaker Icon Backend Tests...")
    print("=" * 50)
    
    # Setup
    tester = SneakerIconBackendTester()

    # Run essential tests for login functionality
    if not tester.test_login():
        print("\n❌ Login failed - cannot proceed with frontend testing")
        return 1

    # Test basic API endpoints needed for the app
    tester.test_get_me()
    tester.test_get_users()

    # Print results
    print(f"\n📊 Backend Tests Summary:")
    print(f"   Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed >= 2:  # Login + at least one other test
        print("✅ Backend is ready for frontend testing")
        return 0
    else:
        print("❌ Backend issues detected - may affect frontend testing")
        return 1

if __name__ == "__main__":
    sys.exit(main())