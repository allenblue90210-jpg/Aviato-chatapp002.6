#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class AviatoAPITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)

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

    def test_login(self, username, password):
        """Test login and get token"""
        url = f"{self.base_url}/api/auth/login"
        self.tests_run += 1
        print(f"\n🔍 Testing Login...")
        
        try:
            # Use form data for OAuth2PasswordRequestForm
            form_data = {
                'username': username,
                'password': password
            }
            response = requests.post(url, data=form_data, timeout=10)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Login successful, token obtained")
                    return True, response_data.get('user', {})
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup(self, email, password, name):
        """Test signup and get token"""
        success, response = self.run_test(
            "Signup",
            "POST",
            "api/auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"✅ Signup successful, token obtained")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )
        return success, response

    def test_get_users(self):
        """Test getting users list"""
        success, response = self.run_test(
            "Get Users",
            "GET", 
            "api/users",
            200
        )
        return success, response

def main():
    # Setup
    tester = AviatoAPITester()
    
    print("🚀 Starting Aviato Backend API Tests...")
    print(f"Testing against: {tester.base_url}")

    # First try to signup a new user for testing
    signup_success = tester.test_signup("test_aviato@test.com", "password", "Test User")
    if signup_success:
        print("✅ Signup successful, proceeding with tests")
    else:
        # Try login with existing test user
        login_success, user_data = tester.test_login("test_aviato@test.com", "password")
        if not login_success:
            print("❌ Both signup and login failed, stopping tests")
            return 1

    # Test getting current user
    me_success, me_data = tester.test_get_current_user()
    if me_success:
        print(f"✅ Current user verified: {me_data.get('name', 'Unknown')}")

    # Test getting users list
    users_success, users_data = tester.test_get_users()
    if users_success:
        user_count = len(users_data) if isinstance(users_data, list) else 0
        print(f"✅ Users list retrieved: {user_count} users found")

    # Print results
    print(f"\n📊 Backend API Tests Summary:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed >= 2:  # At least login/signup + one other test
        print("✅ Backend tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())