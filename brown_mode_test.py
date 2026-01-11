import requests
import sys
import time
from datetime import datetime

class BrownModeAPITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

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
                    error_response = response.json()
                    print(f"Response: {error_response}")
                    return False, error_response
                except:
                    print(f"Response text: {response.text}")
                    return False, {"detail": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_user(self, email, password, name, user_key):
        """Create a new user and get token"""
        success, response = self.run_test(
            f"Create User {name}",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            self.tokens[user_key] = response['access_token']
            self.users[user_key] = response['user']
            return True
        return False

    def login_user(self, email, password, name):
        """Login existing user"""
        # Use form data for login
        url = f"{self.base_url}/api/auth/login"
        data = {
            'username': email,
            'password': password
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Login {name}...")
        
        try:
            response = requests.post(url, data=data)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                resp_data = response.json()
                self.tokens[name] = resp_data['access_token']
                self.users[name] = resp_data['user']
                return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def set_brown_mode(self, user_name, timed_hour, timed_minute=0):
        """Set user to brown mode with specified deadline hour"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        success, response = self.run_test(
            f"Set {user_name} to Brown Mode (Deadline: {timed_hour}:{timed_minute:02d})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": timed_hour,
                    "timedMinute": timed_minute
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
        return success, response

    def start_conversation(self, sender_name, target_name, expected_status=200):
        """Start conversation between users"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        success, response = self.run_test(
            f"Start conversation: {sender_name} -> {target_name}",
            "POST",
            "conversations/start",
            expected_status,
            data={"userId": target_id},
            token=sender_token
        )
        return success, response

    def send_message(self, sender_name, target_name, message_text, expected_status=200):
        """Send message from sender to target"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}'",
            "POST",
            f"conversations/{target_id}/messages",
            expected_status,
            data={"text": message_text},
            token=sender_token
        )
        return success, response

def main():
    print("🧪 Brown Mode 'Deadline' Logic Test")
    print("=" * 50)
    
    # Get current time
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    print(f"Current time: {current_hour}:{current_minute:02d}")
    
    tester = BrownModeAPITester()
    
    # Test users
    timestamp = int(time.time())
    brown_user = f"brown_user_{timestamp}"
    user1 = f"user1_{timestamp}"
    
    users_to_create = [
        (brown_user, f"{brown_user}@test.com", "Brown User"),
        (user1, f"{user1}@test.com", "User 1")
    ]
    
    # Step 0: Create all users
    print("\n📝 Step 0: Creating test users...")
    for user_key, email, name in users_to_create:
        if not tester.create_user(email, "password123", name, user_key):
            print(f"❌ Failed to create {name}, stopping tests")
            return 1
    
    # Step 1: Create Brown User (Set to CURRENT HOUR - should block immediately)
    deadline_hour_past = current_hour  # Current hour should block
    print(f"\n📝 Step 1: Set Brown User to Brown Mode (Deadline: {deadline_hour_past}:00 - CURRENT HOUR)...")
    
    success, brown_data = tester.set_brown_mode(brown_user, deadline_hour_past, 0)
    if not success:
        print("❌ Failed to set brown mode, stopping tests")
        return 1
    
    print(f"✅ Brown User set to Brown Mode with deadline: {deadline_hour_past}:00 (should block now)")
    
    # Step 2: User 1 tries to start chat -> Should Fail (403: Unavailable after X)
    print(f"\n📝 Step 2: User 1 tries to start chat with Brown User (should FAIL - 403)...")
    
    success, response = tester.start_conversation(user1, brown_user, expected_status=403)
    if success:
        # Check if we got the expected error message
        detail = response.get('detail', '')
        if 'unavailable after' in detail.lower() and 'brown mode' in detail.lower():
            print(f"✅ Step 2 Complete: Got expected 403 error: {detail}")
        else:
            print(f"❌ Step 2 Failed: Got 403 but unexpected message: {detail}")
            return 1
    else:
        print("❌ Step 2 Failed: Expected 403 error but got different response")
        return 1
    
    # Step 3: Update Brown User (Set to CURRENT HOUR + 1 - should allow access)
    deadline_hour_future = (current_hour + 1) % 24
    print(f"\n📝 Step 3: Set Brown User to Brown Mode (Deadline: {deadline_hour_future}:00 - FUTURE HOUR)...")
    
    success, brown_data = tester.set_brown_mode(brown_user, deadline_hour_future, 0)
    if not success:
        print("❌ Failed to update brown mode, stopping tests")
        return 1
    
    print(f"✅ Brown User updated to Brown Mode with deadline: {deadline_hour_future}:00 (should allow access)")
    
    # Step 4: User 1 tries to start chat -> Should Succeed
    print(f"\n📝 Step 4: User 1 tries to start chat with Brown User (should SUCCEED)...")
    
    success, response = tester.start_conversation(user1, brown_user, expected_status=200)
    if success:
        print(f"✅ Step 4 Complete: Successfully started conversation")
    else:
        print("❌ Step 4 Failed: Expected successful conversation start")
        return 1
    
    # Step 5: Send a message to verify full flow works
    print(f"\n📝 Step 5: User 1 sends message to Brown User (should SUCCEED)...")
    
    success, response = tester.send_message(user1, brown_user, "Hello Brown User!", expected_status=200)
    if success:
        print(f"✅ Step 5 Complete: Successfully sent message")
    else:
        print("❌ Step 5 Failed: Expected successful message send")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode 'Deadline' Logic tests PASSED!")
        print(f"\n📋 Summary:")
        print(f"   ✅ Brown Mode blocks access when current hour >= deadline hour")
        print(f"   ✅ Brown Mode allows access when current hour < deadline hour")
        print(f"   ✅ Error message correctly mentions 'unavailable after X (Brown Mode)'")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())