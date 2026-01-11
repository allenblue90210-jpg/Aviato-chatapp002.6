import requests
import sys
from datetime import datetime

class BrownModeRemovalTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        if headers is None:
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

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

    def test_signup_and_login(self):
        """Test signup and login with new user"""
        # First try signup
        signup_url = f"{self.base_url}/api/auth/signup"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Signup with new user...")
        
        try:
            signup_data = {
                "email": f"brown_test_{int(datetime.now().timestamp())}@test.com",
                "password": "password123",
                "name": "Brown Test User"
            }
            
            response = requests.post(signup_url, json=signup_data, headers=headers)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Signup Passed - Status: {response.status_code}")
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"✅ Signup successful, token obtained")
                    return True, response_data.get('user', {}), signup_data['email']
            else:
                print(f"❌ Signup Failed - Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Signup Failed - Error: {str(e)}")
            
        return False, {}, None

    def test_get_users(self):
        """Get all users to check for brown mode users"""
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "users",
            200
        )
        if success:
            users = response if isinstance(response, list) else []
            brown_users = [u for u in users if u.get('availabilityMode') == 'brown']
            print(f"✅ Found {len(brown_users)} users with brown mode")
            return success, brown_users
        return False, []

    def test_brown_mode_chat_start(self, brown_user_id):
        """Test starting chat with brown mode user - should NOT be blocked"""
        success, response = self.run_test(
            f"Start Chat with Brown Mode User {brown_user_id}",
            "POST",
            "conversations/start",
            200,
            data={"userId": brown_user_id}
        )
        return success, response

    def test_brown_mode_send_message(self, brown_user_id):
        """Test sending message to brown mode user - should NOT be blocked"""
        success, response = self.run_test(
            f"Send Message to Brown Mode User {brown_user_id}",
            "POST",
            f"conversations/{brown_user_id}/messages",
            200,
            data={"text": "Test message to brown mode user"}
        )
        return success, response

    def test_update_user_to_brown_mode(self, user_id):
        """Test updating user to brown mode"""
        success, response = self.run_test(
            "Update User to Brown Mode",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": 14,
                    "timedMinute": 30,
                    "timezoneOffset": -480
                }
            }
        )
        return success, response

def main():
    # Setup
    tester = BrownModeRemovalTester()
    
    print("🚀 Starting Brown Mode Removal Backend Tests...")
    
    # Test 1: Signup and Login
    login_success, user_data, user_email = tester.test_signup_and_login()
    if not login_success:
        print("❌ Signup/Login failed, stopping tests")
        return 1

    current_user_id = user_data.get('id')
    
    # Test 2: Get all users to find brown mode users
    users_success, brown_users = tester.test_get_users()
    if not users_success:
        print("❌ Failed to get users")
        return 1
    
    # Get all users for testing
    all_users_success, all_users_response = tester.run_test(
        "Get All Users for Testing",
        "GET", 
        "users",
        200
    )
    all_users = all_users_response if isinstance(all_users_response, list) else []

    # Test 3: Update current user to brown mode
    print("📝 Setting current user to brown mode...")
    update_success, updated_user = tester.test_update_user_to_brown_mode(current_user_id)
    if update_success:
        print("✅ Successfully set user to brown mode")
    else:
        print("❌ Failed to set user to brown mode")
        return 1

    # Test 4: Find another user to test brown mode interaction
    other_users = [u for u in all_users if u.get('id') != current_user_id]
    if other_users:
        other_user_id = other_users[0].get('id')
        
        # Test starting chat with other user (should NOT be blocked)
        chat_success, chat_response = tester.test_brown_mode_chat_start(other_user_id)
        if chat_success:
            print("✅ Brown mode user can start chats (correct behavior)")
        else:
            print("❌ Brown mode user cannot start chats (incorrect behavior)")
        
        # Test sending message to other user (should NOT be blocked)
        msg_success, msg_response = tester.test_brown_mode_send_message(other_user_id)
        if msg_success:
            print("✅ Brown mode user can send messages (correct behavior)")
        else:
            print("❌ Brown mode user cannot send messages (incorrect behavior)")
    else:
        print("⚠️ No other users found to test brown mode interaction")

    # Print results
    print(f"\n📊 Backend Tests Summary:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed - Brown mode blocking logic successfully removed")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())