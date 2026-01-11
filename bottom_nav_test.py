#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class BottomNavBackendTester:
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
                if response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, {}
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and login"""
        print("\n🔐 Testing Signup and Login...")
        
        # First try signup
        signup_url = f"{self.base_url}/api/auth/signup"
        test_email = f"bottom_nav_test_{int(datetime.now().timestamp())}@test.com"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Signup...")
        
        try:
            response = requests.post(
                signup_url,
                json={
                    "email": test_email,
                    "password": "password123",
                    "name": "Bottom Nav Test User"
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Signup Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"   Token obtained: {self.token[:20]}...")
                    return True, response_data.get('user', {})
            else:
                print(f"❌ Signup Failed - Expected 200, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
            
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success, response

    def test_users_endpoint(self):
        """Test users endpoint for match page"""
        success, response = self.run_test(
            "Get Users (Match Page)",
            "GET",
            "users",
            200
        )
        return success, response

    def test_conversations_endpoint(self):
        """Test conversations endpoint for chat page"""
        success, response = self.run_test(
            "Get Conversations (Chat Page)",
            "GET",
            "conversations",
            200
        )
        return success, response

def main():
    print("🚀 Starting Bottom Nav Backend API Tests...")
    print("=" * 50)
    
    # Setup
    tester = BottomNavBackendTester()

    # Test signup and login first
    login_success, user_data = tester.test_signup_and_login()
    if not login_success:
        print("❌ Login failed, cannot proceed with other tests")
        return 1

    print(f"\n👤 Logged in as: {user_data.get('name', 'Unknown')} ({user_data.get('email', 'Unknown')})")

    # Test endpoints that bottom nav pages will use
    tester.test_auth_me()
    tester.test_users_endpoint()
    tester.test_conversations_endpoint()

    # Print results
    print(f"\n📊 Backend API Test Results:")
    print(f"   Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend APIs are working correctly!")
        return 0
    else:
        print("❌ Some backend APIs failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())