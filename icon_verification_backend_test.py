#!/usr/bin/env python3

import requests
import sys
from datetime import datetime

class IconVerificationBackendTester:
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
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text[:200]}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self):
        """Test login with demo credentials"""
        print("\n🔐 Testing Login...")
        
        # Using form data for OAuth2PasswordRequestForm
        login_data = {
            "username": "demo@aviato.com",
            "password": "password"
        }
        
        url = f"{self.base_url}/api/auth/login"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(url, data=login_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.tests_passed += 1
                result = response.json()
                self.token = result.get('access_token')
                print(f"✅ Login successful - Token received")
                return True, result
            else:
                print(f"❌ Login failed - Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text[:200]}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Login failed - Error: {str(e)}")
            return False, {}
        finally:
            self.tests_run += 1

    def test_auth_me(self):
        """Test getting current user info"""
        return self.run_test("Get Current User", "GET", "auth/me", 200)

    def test_get_users(self):
        """Test getting users list"""
        return self.run_test("Get Users List", "GET", "users", 200)

def main():
    print("🚀 Starting Icon Verification Backend Tests...")
    print("=" * 50)
    
    # Setup
    tester = IconVerificationBackendTester()

    # Test login
    login_success, login_response = tester.test_login()
    if not login_success:
        print("\n❌ Login failed, cannot proceed with authenticated tests")
        print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        return 1

    # Test authenticated endpoints
    tester.test_auth_me()
    tester.test_get_users()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Backend Tests Summary: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed! Ready for frontend testing.")
        return 0
    else:
        print("❌ Some backend tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())