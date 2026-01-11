import requests
import sys
import time
from datetime import datetime, timedelta

class BrownModeTimezoneValidationTest:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
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

    def set_brown_mode(self, user_name, timed_hour, timed_minute=0):
        """Set user to brown mode with specified closing time (no timezone offset stored)"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        success, response = self.run_test(
            f"Set {user_name} to Brown Mode (Closes at {timed_hour}:{timed_minute:02d})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": timed_hour,
                    "timedMinute": timed_minute
                    # Deliberately NOT setting timezoneOffset to test header fallback
                }
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
    print("🧪 Brown Mode Universal Timezone Fix Validation")
    print("=" * 60)
    print("Testing that backend uses CLIENT's timezone offset from headers")
    print("=" * 60)
    
    # Get current server time
    now_utc = datetime.utcnow()
    print(f"Current Server Time (UTC): {now_utc.strftime('%H:%M:%S')}")
    
    tester = BrownModeTimezoneValidationTest()
    
    # Test users
    timestamp = int(time.time())
    brown_user = f"brown_user_{timestamp}"
    sender_user = f"sender_{timestamp}"
    
    # Step 0: Create test users
    print("\n📝 Step 0: Creating test users...")
    users_to_create = [
        (brown_user, f"{brown_user}@test.com", "Brown User"),
        (sender_user, f"{sender_user}@test.com", "Sender User")
    ]
    
    for user_key, email, name in users_to_create:
        if not tester.create_user(email, "password123", name, user_key):
            print(f"❌ Failed to create {name}, stopping tests")
            return 1
    
    # Test Scenario 1: UTC-8 timezone (Pacific Time)
    print("\n" + "="*50)
    print("SCENARIO 1: UTC-8 Timezone (Pacific Time)")
    print("="*50)
    
    timezone_offset_minutes = 480  # 8 hours * 60 minutes behind UTC
    user_local_time = now_utc - timedelta(minutes=timezone_offset_minutes)
    
    print(f"Server UTC Time: {now_utc.strftime('%H:%M:%S')}")
    print(f"User Local Time (UTC-8): {user_local_time.strftime('%H:%M:%S')}")
    
    current_hour = user_local_time.hour
    current_minute = user_local_time.minute
    
    # Set deadline 1 hour in the future (should allow)
    future_deadline_hour = (current_hour + 1) % 24
    future_deadline_minute = current_minute
    
    print(f"\n📝 Step 1: Set deadline to {future_deadline_hour:02d}:{future_deadline_minute:02d} (1 hour in future)...")
    success, _ = tester.set_brown_mode(brown_user, future_deadline_hour, future_deadline_minute)
    if not success:
        return 1
    
    print(f"\n📝 Step 2: Start conversation and send message (should succeed)...")
    success, _ = tester.start_conversation_with_timezone(sender_user, brown_user, timezone_offset_minutes)
    if not success:
        return 1
    
    success, _ = tester.send_message_with_timezone(
        sender_user, brown_user,
        f"Message at {current_hour:02d}:{current_minute:02d} with {future_deadline_hour:02d}:{future_deadline_minute:02d} deadline",
        timezone_offset_minutes,
        expected_status=200
    )
    if not success:
        return 1
    
    # Set deadline 1 hour in the past (should block)
    past_deadline_hour = (current_hour - 1) % 24
    past_deadline_minute = current_minute
    
    print(f"\n📝 Step 3: Update deadline to {past_deadline_hour:02d}:{past_deadline_minute:02d} (1 hour in past)...")
    success, _ = tester.set_brown_mode(brown_user, past_deadline_hour, past_deadline_minute)
    if not success:
        return 1
    
    print(f"\n📝 Step 4: Send message (should be blocked)...")
    success, _ = tester.send_message_with_timezone(
        sender_user, brown_user,
        f"Message at {current_hour:02d}:{current_minute:02d} with {past_deadline_hour:02d}:{past_deadline_minute:02d} deadline",
        timezone_offset_minutes,
        expected_status=403
    )
    if not success:
        return 1
    
    # Test Scenario 2: UTC+0 timezone (same as server)
    print("\n" + "="*50)
    print("SCENARIO 2: UTC+0 Timezone (Same as Server)")
    print("="*50)
    
    utc_offset = 0
    server_hour = now_utc.hour
    server_minute = now_utc.minute
    
    print(f"Server UTC Time: {now_utc.strftime('%H:%M:%S')}")
    print(f"User Local Time (UTC+0): {now_utc.strftime('%H:%M:%S')} (same as server)")
    
    # Create another user for this test
    user2 = f"user2_{timestamp}"
    if not tester.create_user(f"{user2}@test.com", "password123", "User 2", user2):
        return 1
    
    # The deadline is still set to past_deadline_hour:past_deadline_minute from previous test
    print(f"Current deadline: {past_deadline_hour:02d}:{past_deadline_minute:02d}")
    print(f"Server time: {server_hour:02d}:{server_minute:02d}")
    
    # Determine if server time is past the deadline
    server_time_minutes = server_hour * 60 + server_minute
    deadline_time_minutes = past_deadline_hour * 60 + past_deadline_minute
    
    if server_time_minutes >= deadline_time_minutes:
        expected_status = 403
        expected_result = "blocked"
    else:
        expected_status = 200
        expected_result = "allowed"
    
    print(f"Expected result: {expected_result} (status {expected_status})")
    
    print(f"\n📝 Step 5: Test conversation start with UTC+0...")
    success, _ = tester.start_conversation_with_timezone(user2, brown_user, utc_offset, expected_status)
    if not success:
        return 1
    
    if expected_status == 200:
        print(f"\n📝 Step 6: Send message with UTC+0 (should succeed)...")
        success, _ = tester.send_message_with_timezone(
            user2, brown_user,
            f"Message with UTC+0 at {server_hour:02d}:{server_minute:02d}",
            utc_offset,
            expected_status=200
        )
        if not success:
            return 1
    
    # Test Scenario 3: Different timezone to show contrast
    print("\n" + "="*50)
    print("SCENARIO 3: UTC+5 Timezone (5 hours ahead)")
    print("="*50)
    
    timezone_ahead = -300  # 5 hours ahead (negative offset)
    user_ahead_time = now_utc - timedelta(minutes=timezone_ahead)
    
    print(f"Server UTC Time: {now_utc.strftime('%H:%M:%S')}")
    print(f"User Local Time (UTC+5): {user_ahead_time.strftime('%H:%M:%S')}")
    
    # Create another user
    user3 = f"user3_{timestamp}"
    if not tester.create_user(f"{user3}@test.com", "password123", "User 3", user3):
        return 1
    
    ahead_hour = user_ahead_time.hour
    ahead_minute = user_ahead_time.minute
    
    # Compare with deadline
    ahead_time_minutes = ahead_hour * 60 + ahead_minute
    
    if ahead_time_minutes >= deadline_time_minutes:
        expected_status = 403
        expected_result = "blocked"
    else:
        expected_status = 200
        expected_result = "allowed"
    
    print(f"User time: {ahead_hour:02d}:{ahead_minute:02d}, Deadline: {past_deadline_hour:02d}:{past_deadline_minute:02d}")
    print(f"Expected result: {expected_result} (status {expected_status})")
    
    print(f"\n📝 Step 7: Test with UTC+5 timezone...")
    success, _ = tester.start_conversation_with_timezone(user3, brown_user, timezone_ahead, expected_status)
    if not success:
        return 1
    
    if expected_status == 200:
        success, _ = tester.send_message_with_timezone(
            user3, brown_user,
            f"Message with UTC+5 at {ahead_hour:02d}:{ahead_minute:02d}",
            timezone_ahead,
            expected_status=200
        )
        if not success:
            return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL BROWN MODE TIMEZONE TESTS PASSED!")
        print("✅ Backend correctly uses CLIENT's timezone offset from headers")
        print("✅ Different timezones produce different results as expected")
        print("✅ Universal timezone fix is working correctly")
        return 0
    else:
        print("\n❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())