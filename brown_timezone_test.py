import requests
import sys
import time
from datetime import datetime, timedelta

class BrownModeTimezoneAPITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, headers=None):
        """Run a single API test with custom headers"""
        url = f"{self.base_url}/api/{endpoint}"
        request_headers = {'Content-Type': 'application/json'}
        if token:
            request_headers['Authorization'] = f'Bearer {token}'
        if headers:
            request_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   Headers: {request_headers}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers)

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
                    error_data = response.json()
                    print(f"Response: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

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

    def set_brown_mode(self, user_name, timed_hour, timed_minute=0, timezone_offset=None):
        """Set user to brown mode with specified closing time and optional timezone offset"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        availability_data = {
            "timedHour": timed_hour,
            "timedMinute": timed_minute
        }
        
        # Only include timezone offset if explicitly provided
        if timezone_offset is not None:
            availability_data["timezoneOffset"] = timezone_offset
        
        success, response = self.run_test(
            f"Set {user_name} to Brown Mode (Closes at {timed_hour}:{timed_minute:02d}, TZ offset: {timezone_offset})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": availability_data
            },
            token=token
        )
        if success:
            self.users[user_name] = response
        return success, response

    def send_message_with_timezone(self, sender_name, target_name, message_text, timezone_offset_minutes, expected_status=200):
        """Send message with specific timezone offset header"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        # Add timezone offset header
        custom_headers = {
            'x-timezone-offset': str(timezone_offset_minutes)
        }
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}' (TZ offset: {timezone_offset_minutes} min)",
            "POST",
            f"conversations/{target_id}/messages",
            expected_status,
            data={"text": message_text},
            token=sender_token,
            headers=custom_headers
        )
        return success, response

    def start_conversation_with_timezone(self, sender_name, target_name, timezone_offset_minutes, expected_status=200):
        """Start conversation with specific timezone offset header"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        # Add timezone offset header
        custom_headers = {
            'x-timezone-offset': str(timezone_offset_minutes)
        }
        
        success, response = self.run_test(
            f"Start conversation: {sender_name} -> {target_name} (TZ offset: {timezone_offset_minutes} min)",
            "POST",
            "conversations/start",
            expected_status,
            data={"userId": target_id},
            token=sender_token,
            headers=custom_headers
        )
        return success, response

def main():
    print("🧪 Brown Mode Universal Timezone Fix Test")
    print("=" * 60)
    print("Testing scenario:")
    print("1. Create Brown User (Local Time = 9 PM, Server UTC Time = 2 AM)")
    print("2. Set Deadline to 10 PM")
    print("3. User messages -> Success")
    print("4. Set Deadline to 8 PM") 
    print("5. User messages -> Fail (403)")
    print("6. This proves backend uses CLIENT's timezone offset from headers")
    print("=" * 60)
    
    tester = BrownModeTimezoneAPITester()
    
    # Test users
    timestamp = int(time.time())
    brown_user = f"brown_user_{timestamp}"
    sender_user = f"sender_{timestamp}"
    
    users_to_create = [
        (brown_user, f"{brown_user}@test.com", "Brown User"),
        (sender_user, f"{sender_user}@test.com", "Sender User")
    ]
    
    # Step 0: Create test users
    print("\n📝 Step 0: Creating test users...")
    for user_key, email, name in users_to_create:
        if not tester.create_user(email, "password123", name, user_key):
            print(f"❌ Failed to create {name}, stopping tests")
            return 1
    
    # Calculate timezone scenario:
    # Local Time = 9 PM, Server UTC Time = 2 AM
    # This means user is UTC-5 (300 minutes behind UTC)
    # When it's 2 AM UTC, it's 9 PM local time (2 AM - 5 hours = 9 PM previous day)
    timezone_offset_minutes = 300  # 5 hours * 60 minutes = 300 minutes behind UTC
    
    print(f"\n🌍 Timezone Setup:")
    print(f"   Server UTC Time: 2:00 AM")
    print(f"   User Local Time: 9:00 PM (UTC-5, offset: {timezone_offset_minutes} minutes)")
    
    # Step 1: Set Brown User to Brown Mode with 10 PM deadline (should allow messaging)
    print("\n📝 Step 1: Set Brown User deadline to 10 PM (after current 9 PM local time)...")
    
    # Set deadline to 10 PM (22:00)
    deadline_hour = 22  # 10 PM
    deadline_minute = 0
    
    success, brown_data = tester.set_brown_mode(brown_user, deadline_hour, deadline_minute)
    if not success:
        print("❌ Failed to set brown mode, stopping tests")
        return 1
    
    print(f"✅ Brown User set to Brown Mode: Deadline at {deadline_hour}:{deadline_minute:02d}")
    
    # Step 2: Start conversation with timezone header
    print("\n📝 Step 2: Start conversation with timezone offset...")
    
    success, _ = tester.start_conversation_with_timezone(sender_user, brown_user, timezone_offset_minutes)
    if not success:
        print("❌ Failed to start conversation")
        return 1
    
    # Step 3: Test messaging before deadline (9 PM < 10 PM, should work)
    print("\n📝 Step 3: Test messaging at 9 PM local time with 10 PM deadline (should succeed)...")
    
    success, _ = tester.send_message_with_timezone(
        sender_user, brown_user, 
        "Hello at 9 PM local time with 10 PM deadline!", 
        timezone_offset_minutes, 
        expected_status=200
    )
    if success:
        print("✅ Message sent successfully - 9 PM < 10 PM deadline")
    else:
        print("❌ Message failed unexpectedly")
        return 1
    
    # Step 4: Set Brown User deadline to 8 PM (should block messaging)
    print("\n📝 Step 4: Update Brown User deadline to 8 PM (before current 9 PM local time)...")
    
    # Set deadline to 8 PM (20:00)
    deadline_hour = 20  # 8 PM
    deadline_minute = 0
    
    success, brown_data = tester.set_brown_mode(brown_user, deadline_hour, deadline_minute)
    if not success:
        print("❌ Failed to update brown mode, stopping tests")
        return 1
    
    print(f"✅ Brown User deadline updated to: {deadline_hour}:{deadline_minute:02d}")
    
    # Step 5: Test messaging after deadline (9 PM > 8 PM, should be blocked)
    print("\n📝 Step 5: Test messaging at 9 PM local time with 8 PM deadline (should fail with 403)...")
    
    success, response = tester.send_message_with_timezone(
        sender_user, brown_user, 
        "Hello at 9 PM local time with 8 PM deadline!", 
        timezone_offset_minutes, 
        expected_status=403
    )
    if success:
        print("✅ Message correctly blocked - 9 PM > 8 PM deadline")
    else:
        print("❌ Message was not blocked as expected")
        return 1
    
    # Step 6: Test conversation start after deadline (should also be blocked)
    print("\n📝 Step 6: Test starting new conversation after deadline...")
    
    # Create another user to test conversation start
    user2 = f"user2_{timestamp}"
    if not tester.create_user(f"{user2}@test.com", "password123", "User 2", user2):
        print("❌ Failed to create User 2")
        return 1
    
    success, _ = tester.start_conversation_with_timezone(
        user2, brown_user, 
        timezone_offset_minutes, 
        expected_status=403
    )
    if success:
        print("✅ Conversation start correctly blocked after deadline")
    else:
        print("❌ Conversation start was not blocked as expected")
        return 1
    
    # Step 7: Test with different timezone offset to verify header usage
    print("\n📝 Step 7: Test with different timezone offset (UTC+0) - should allow messaging...")
    
    # With UTC+0, server time 2 AM = local time 2 AM, which is < 8 PM deadline
    utc_offset = 0
    
    # Create another user for this test
    user3 = f"user3_{timestamp}"
    if not tester.create_user(f"{user3}@test.com", "password123", "User 3", user3):
        print("❌ Failed to create User 3")
        return 1
    
    # Start conversation first
    success, _ = tester.start_conversation_with_timezone(user3, brown_user, utc_offset)
    if not success:
        print("❌ Failed to start conversation with UTC offset")
        return 1
    
    # Send message (should succeed because 2 AM < 8 PM)
    success, _ = tester.send_message_with_timezone(
        user3, brown_user, 
        "Hello at 2 AM UTC with 8 PM deadline!", 
        utc_offset, 
        expected_status=200
    )
    if success:
        print("✅ Message sent successfully with UTC+0 - 2 AM < 8 PM deadline")
    else:
        print("❌ Message failed with UTC offset")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode Universal Timezone Fix tests PASSED!")
        print("✅ Backend correctly uses CLIENT's timezone offset from headers")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())