#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None

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
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and login"""
        print("\n=== Testing Authentication ===")
        
        # First try to signup a new user
        timestamp = int(datetime.now().timestamp())
        test_email = f"test_{timestamp}@test.com"
        test_password = "TestPass123!"
        
        signup_data = {
            "email": test_email,
            "password": test_password,
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "Signup New User",
            "POST",
            "api/auth/signup",
            200,
            data=signup_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response.get('user', {})
            print(f"   Signed up and logged in as: {self.current_user.get('name', 'Unknown')}")
            return True
            
        # If signup fails, try demo login
        print("\n   Signup failed, trying demo login...")
        url = f"{self.base_url}/api/auth/login"
        login_data = {
            "username": "demo@aviato.com",
            "password": "password"
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Login with Demo User...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, data=login_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    self.current_user = response_data.get('user', {})
                    print(f"   Logged in as: {self.current_user.get('name', 'Unknown')}")
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            
        return False
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response.get('user', {})
            print(f"   Logged in as: {self.current_user.get('name', 'Unknown')}")
            return True
        return False

    def test_auth_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User Info",
            "GET",
            "api/auth/me",
            200
        )
        return success

    def test_users_endpoint(self):
        """Test users endpoint"""
        print("\n=== Testing User Endpoints ===")
        
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "api/users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
            return True
        return False

    def test_conversations_endpoint(self):
        """Test conversations endpoint"""
        print("\n=== Testing Chat/Conversations Endpoints ===")
        
        success, response = self.run_test(
            "Get Conversations",
            "GET",
            "api/conversations",
            200
        )
        
        if success:
            print(f"   Found {len(response) if isinstance(response, list) else 0} conversations")
            return True
        return False

    def test_start_chat(self):
        """Test starting a chat with another user"""
        # First get users to find someone to chat with
        success, users = self.run_test(
            "Get Users for Chat Test",
            "GET",
            "api/users",
            200
        )
        
        if not success or not users:
            print("❌ Cannot test chat - no users available")
            return False
            
        # Find a user that's not the current user
        target_user = None
        for user in users:
            if user.get('id') != self.current_user.get('id'):
                target_user = user
                break
                
        if not target_user:
            print("❌ Cannot test chat - no other users available")
            return False
            
        print(f"   Attempting to start chat with: {target_user.get('name', 'Unknown')}")
        
        success, response = self.run_test(
            "Start Chat",
            "POST",
            "api/conversations/start",
            200,
            data={"userId": target_user['id']}
        )
        
        return success

def main():
    print("🚀 Starting Backend API Tests for Chat Messenger")
    print("=" * 50)
    
    tester = APITester()
    
    # Test authentication first
    if not tester.test_signup_and_login():
        print("\n❌ Authentication failed - cannot proceed with other tests")
        return 1
    
    # Test auth/me endpoint
    tester.test_auth_me()
    
    # Test core endpoints
    tester.test_users_endpoint()
    tester.test_conversations_endpoint()
    tester.test_start_chat()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())