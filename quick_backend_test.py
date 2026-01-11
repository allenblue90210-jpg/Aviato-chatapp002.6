import requests
import sys

class QuickAPITester:
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
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if endpoint == 'auth/login':
                    # Use form data for login
                    response = requests.post(url, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)

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
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup_and_login(self):
        """Test signup and login"""
        import time
        timestamp = int(time.time())
        email = f"test_user_{timestamp}@test.com"
        
        # Try signup first
        success, response = self.run_test(
            "Signup Test User",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password123", "name": "Test User"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True, response['user']
        
        # If signup fails, try login with demo user
        success, response = self.run_test(
            "Login Demo User",
            "POST",
            "auth/login",
            200,
            data={"username": "demo@aviato.com", "password": "password"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True, response['user']
        return False, {}

    def test_get_users(self):
        """Get all users"""
        success, response = self.run_test(
            "Get Users",
            "GET",
            "users",
            200
        )
        return success, response

def main():
    print("🧪 Quick Backend API Test")
    print("=" * 50)
    
    tester = QuickAPITester()
    
    # Test login
    login_success, user_data = tester.test_signup_and_login()
    if not login_success:
        print("❌ Login/Signup failed, stopping tests")
        return 1
    
    print(f"✅ Logged in as: {user_data.get('name', 'Unknown')}")
    
    # Test get users
    users_success, users_data = tester.test_get_users()
    if users_success:
        print(f"✅ Found {len(users_data)} users")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())