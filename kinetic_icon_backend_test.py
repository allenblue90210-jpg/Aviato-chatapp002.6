#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class KineticIconBackendTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
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
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and then login"""
        import time
        test_email = f"kinetic_icon_test_{int(time.time())}@test.com"
        test_password = "testpass123"
        
        # First, try to signup
        url = f"{self.base_url}/api/auth/signup"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Signup...")
        
        try:
            response = requests.post(
                url, 
                json={"email": test_email, "password": test_password, "name": "Kinetic Icon Test User"},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Signup successful - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Token obtained from signup")
                    return True
            else:
                print(f"❌ Signup failed - Status: {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"❌ Signup failed - Error: {str(e)}")
            return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_get_users(self):
        """Test getting users list"""
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "users",
            200
        )
        return success

def main():
    print("🚀 Starting Kinetic Icon Backend Tests...")
    print("=" * 50)
    
    # Setup
    tester = KineticIconBackendTester()

    # Test basic backend functionality needed for UI testing
    if not tester.test_signup_and_login():
        print("❌ Signup/Login failed, cannot proceed with UI testing")
        return 1

    if not tester.test_get_current_user():
        print("❌ Get current user failed")
        return 1

    if not tester.test_get_users():
        print("❌ Get users failed")
        return 1

    # Print results
    print(f"\n📊 Backend Tests Summary:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed - Ready for UI testing")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())