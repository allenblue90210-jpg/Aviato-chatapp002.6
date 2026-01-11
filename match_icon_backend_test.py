#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class SimpleAPITester:
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
                        print(f"   Response keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'Non-dict response'}")
                    except:
                        print(f"   Response length: {len(response.text)} chars")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self):
        """Test login with demo user"""
        url = f"{self.base_url}/api/auth/login"
        self.tests_run += 1
        print(f"\n🔍 Testing Login with Demo User...")
        
        try:
            # OAuth2PasswordRequestForm expects form data
            response = requests.post(url, data={
                "username": "demo@aviato.com", 
                "password": "password"
            }, timeout=10)

            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                resp_json = response.json()
                if 'access_token' in resp_json:
                    self.token = resp_json['access_token']
                    print(f"   Logged in as: {resp_json.get('user', {}).get('name', 'Unknown')}")
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            
        return False

    def test_get_users(self):
        """Get users list"""
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "api/users",
            200
        )
        if success:
            users_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {users_count} users")
        return success

    def test_get_me(self):
        """Get current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )
        return success

def main():
    print("🚀 Starting Backend API Tests...")
    print("=" * 50)
    
    # Setup
    tester = SimpleAPITester()

    # Run tests
    if not tester.test_login():
        print("❌ Login failed, stopping tests")
        return 1

    if not tester.test_get_me():
        print("❌ Get current user failed")
        return 1

    if not tester.test_get_users():
        print("❌ Get users failed")
        return 1

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())