import requests
import sys
from datetime import datetime

class BasicAPITester:
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
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text}")

            return success, response.json() if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self):
        """Test login with demo user"""
        # Use form data for login
        url = f"{self.base_url}/api/auth/login"
        data = {
            'username': 'demo@aviato.com',
            'password': 'password'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Demo User Login...")
        
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

    def test_get_users(self):
        """Get all users"""
        success, response = self.run_test(
            "Get Users",
            "GET",
            "users",
            200
        )
        return success, response

    def test_get_me(self):
        """Get current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success, response

    def test_get_conversations(self):
        """Get conversations"""
        success, response = self.run_test(
            "Get Conversations",
            "GET",
            "conversations",
            200
        )
        return success, response

def main():
    print("🧪 Basic Backend API Tests")
    print("=" * 50)
    
    tester = BasicAPITester()

    # Test login
    success, login_data = tester.test_login()
    if not success:
        print("❌ Login failed, stopping tests")
        return 1

    print(f"✅ Logged in as: {login_data.get('user', {}).get('name', 'Unknown')}")

    # Test basic endpoints
    tester.test_get_me()
    tester.test_get_users()
    tester.test_get_conversations()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All basic backend tests PASSED!")
        return 0
    else:
        print("❌ Some backend tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())