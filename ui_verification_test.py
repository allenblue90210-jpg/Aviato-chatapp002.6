#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class UIVerificationTester:
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
                return True, response.json() if response.content else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.content:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup with new user and then login"""
        print("\n🔐 Testing Signup and Login...")
        
        # Generate unique email for testing
        timestamp = int(datetime.now().timestamp())
        test_email = f"test_ui_{timestamp}@test.com"
        test_password = "TestPass123!"
        test_name = "UI Test User"
        
        # Try signup first
        signup_data = {
            "email": test_email,
            "password": test_password,
            "name": test_name
        }
        
        url = f"{self.base_url}/api/auth/signup"
        headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"Attempting signup with: {test_email}")
            response = requests.post(url, json=signup_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'access_token' in result:
                    self.token = result['access_token']
                    self.tests_passed += 1
                    print(f"✅ Signup successful - Token received")
                    print(f"User: {result.get('user', {}).get('name', 'Unknown')}")
                    self.tests_run += 1
                    return True
                else:
                    print(f"❌ Signup failed - No token in response")
            else:
                print(f"❌ Signup failed - Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Signup failed - Error: {str(e)}")
        
        self.tests_run += 1
        return False

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        if not self.token:
            print("❌ No token available, skipping API tests")
            return False
            
        # Test /auth/me
        success, _ = self.run_test("Get Current User", "GET", "auth/me", 200)
        if not success:
            return False
            
        # Test /users
        success, _ = self.run_test("Get Users List", "GET", "users", 200)
        return success

def main():
    print("🚀 Starting UI Verification Backend Tests...")
    print("=" * 50)
    
    tester = UIVerificationTester()
    
    # Test login
    if not tester.test_signup_and_login():
        print("\n❌ Login test failed - Cannot proceed with UI verification")
        return 1
    
    # Test basic endpoints
    if not tester.test_basic_endpoints():
        print("\n❌ Basic API tests failed")
        return 1
    
    # Print results
    print(f"\n📊 Backend Tests Summary:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed - Ready for UI verification")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())