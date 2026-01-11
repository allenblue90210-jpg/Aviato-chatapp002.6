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
                if response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, {}
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.content:
                    print(f"Response: {response.text[:200]}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and login"""
        import time
        test_email = f"test_nav_{int(time.time())}@test.com"
        
        # First signup
        url = f"{self.base_url}/api/auth/signup"
        self.tests_run += 1
        print(f"\n🔍 Testing Signup...")
        
        try:
            response = requests.post(url, json={
                "email": test_email,
                "password": "password123",
                "name": "Nav Test User"
            }, timeout=10)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Signup successful")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Got token from signup")
                    return True
            else:
                print(f"❌ Signup failed - Status: {response.status_code}")
                if response.content:
                    print(f"Response: {response.text[:200]}")
            return False
        except Exception as e:
            print(f"❌ Signup failed - Error: {str(e)}")
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
            print(f"✅ Found {len(response)} users")
            return True
        return False

    def test_get_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )
        if success and 'email' in response:
            print(f"✅ Current user: {response.get('name', 'Unknown')}")
            return True
        return False

def main():
    print("🚀 Starting Backend API Tests...")
    
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
    print(f"\n📊 Backend Tests Summary: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed! Ready for UI testing.")
        return 0
    else:
        print("❌ Some backend tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())