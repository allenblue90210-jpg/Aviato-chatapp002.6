#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class BackendTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
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
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and login"""
        print("\n=== Testing Signup and Authentication ===")
        
        # First try signup
        signup_url = f"{self.base_url}/api/auth/signup"
        signup_data = {
            'email': 'brown_test@test.com',
            'password': 'password123',
            'name': 'Brown Test User'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Signup...")
        print(f"   URL: {signup_url}")
        
        try:
            response = requests.post(signup_url, json=signup_data, timeout=10)
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Signup Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    self.current_user = response_data.get('user', {})
                    print(f"   Token obtained: {self.token[:20]}...")
                    print(f"   User: {self.current_user.get('name', 'Unknown')}")
                    return True
            else:
                print(f"❌ Signup Failed - Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                    
                # If signup fails, try login with existing user
                return self.test_login_existing()
        except Exception as e:
            print(f"❌ Signup Failed - Error: {str(e)}")
            return self.test_login_existing()
            
    def test_login_existing(self):
        """Try to login with existing user"""
        print(f"\n🔍 Testing Login with existing user...")
        
        # Try with a user from the API response
        url = f"{self.base_url}/api/auth/login"
        form_data = {
            'username': 'testui@test.com',
            'password': 'password'
        }
        
        self.tests_run += 1
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, data=form_data, timeout=10)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    self.current_user = response_data.get('user', {})
                    print(f"   Token obtained: {self.token[:20]}...")
                    print(f"   User: {self.current_user.get('name', 'Unknown')}")
                    return True
                return False
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response.get('user', {})
            print(f"   Token obtained: {self.token[:20]}...")
            print(f"   User: {self.current_user.get('name', 'Unknown')}")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            print(f"   User ID: {response.get('id')}")
            print(f"   Email: {response.get('email')}")
            print(f"   Current Mode: {response.get('availabilityMode')}")
        
        return success

    def test_get_users(self):
        """Test getting all users"""
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
            # Check if any users have brown mode
            brown_users = [u for u in response if u.get('availabilityMode') == 'brown']
            if brown_users:
                print(f"   ⚠️  Found {len(brown_users)} users with brown mode")
                for user in brown_users:
                    print(f"      - {user.get('name', 'Unknown')} (ID: {user.get('id')})")
            else:
                print(f"   ✅ No users found with brown mode")
        
        return success

    def test_conversations(self):
        """Test conversations endpoint"""
        success, response = self.run_test(
            "Get Conversations",
            "GET",
            "conversations",
            200
        )
        
        if success:
            print(f"   Found {len(response) if isinstance(response, list) else 0} conversations")
        
        return success

def main():
    print("🚀 Starting Backend API Tests")
    print("=" * 50)
    
    tester = BackendTester()
    
    # Test authentication
    if not tester.test_signup_and_login():
        print("\n❌ Authentication failed - stopping tests")
        return 1
    
    # Test user endpoints
    tester.test_get_current_user()
    tester.test_get_users()
    tester.test_conversations()
    
    # Print final results
    print(f"\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())