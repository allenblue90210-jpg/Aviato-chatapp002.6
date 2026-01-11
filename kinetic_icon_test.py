import requests
import sys
from datetime import datetime

class KineticIconTester:
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
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup with new user and then login"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"kinetic_test_{timestamp}@test.com"
        test_password = "TestPass123!"
        
        # First try signup
        url = f"{self.base_url}/api/auth/signup"
        self.tests_run += 1
        print(f"\n🔍 Testing Signup with new user...")
        
        try:
            response = requests.post(url, json={
                "email": test_email,
                "password": test_password,
                "name": "Kinetic Test User"
            })
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Signup Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Signup successful, token obtained")
                    return True
            else:
                print(f"❌ Signup Failed - Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")
                
                # If signup fails, try login with demo user
                return self.test_demo_login()
            
            return success
        except Exception as e:
            print(f"❌ Signup Failed - Error: {str(e)}")
            # If signup fails, try login with demo user
            return self.test_demo_login()

    def test_demo_login(self):
        """Test login with demo credentials"""
        url = f"{self.base_url}/api/auth/login"
        self.tests_run += 1
        print(f"\n🔍 Testing Login with Demo User...")
        
        try:
            # Use form data for OAuth2PasswordRequestForm
            response = requests.post(url, data={
                "username": "demo@aviato.com", 
                "password": "password"
            })
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Login successful, token obtained")
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")
            
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"✅ Login successful, token obtained")
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

    def test_get_users(self):
        """Test getting users list"""
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "api/users",
            200
        )
        return success

def main():
    # Setup
    tester = KineticIconTester()

    print("🚀 Starting Kinetic Icon Backend Tests...")
    print("=" * 50)

    # Test login first
    if not tester.test_signup_and_login():
        print("❌ Authentication failed, stopping tests")
        return 1

    # Test authenticated endpoints
    tester.test_auth_me()
    tester.test_get_users()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Backend Tests Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed! Ready for frontend testing.")
        return 0
    else:
        print("❌ Some backend tests failed. Check API connectivity.")
        return 1

if __name__ == "__main__":
    sys.exit(main())