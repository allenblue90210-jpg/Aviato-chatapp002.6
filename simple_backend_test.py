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
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")

            return success, response.json() if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password):
        """Test login and get token"""
        # Use form data for login
        url = f"{self.base_url}/api/auth/login"
        data = {
            'username': username,
            'password': password
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Login...")
        
        try:
            response = requests.post(url, data=data)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                resp_data = response.json()
                self.token = resp_data['access_token']
                return True, resp_data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

def main():
    # Setup
    tester = SimpleAPITester()
    
    print("🧪 Simple Backend API Test")
    print("=" * 50)

    # Test login with test user
    success, login_data = tester.test_login("test@test.com", "password")
    if not success:
        print("❌ Login failed, stopping tests")
        return 1

    print(f"✅ Login successful for user: {login_data.get('user', {}).get('name', 'Unknown')}")

    # Test get current user
    success, user_data = tester.run_test(
        "Get Current User",
        "GET",
        "auth/me",
        200
    )
    if not success:
        print("❌ Get current user failed")
        return 1

    # Test get users list
    success, users_data = tester.run_test(
        "Get Users List",
        "GET",
        "users",
        200
    )
    if not success:
        print("❌ Get users list failed")
        return 1

    print(f"✅ Found {len(users_data)} users in the system")

    # Test get conversations
    success, conversations_data = tester.run_test(
        "Get Conversations",
        "GET",
        "conversations",
        200
    )
    if not success:
        print("❌ Get conversations failed")
        return 1

    print(f"✅ Found {len(conversations_data)} conversations")

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())