import requests
import sys
import time
from datetime import datetime, timedelta

class BrownModeRealisticTimezoneTest:
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
    print("🧪 Brown Mode Realistic Timezone Test")
    print("=" * 60)
    
    # Get current server time
    now_utc = datetime.utcnow()
    print(f"Current Server Time (UTC): {now_utc.strftime('%H:%M:%S')}")
    
    # Calculate timezone scenario
    # Let's use UTC-8 (Pacific Time) - 480 minutes behind UTC
    timezone_offset_minutes = 480  # 8 hours * 60 minutes
    user_local_time = now_utc - timedelta(minutes=timezone_offset_minutes)
    
    print(f"User Local Time (UTC-8): {user_local_time.strftime('%H:%M:%S')}")
    print(f"Timezone Offset: {timezone_offset_minutes} minutes behind UTC")
    
    # Set deadlines relative to user's local time
    current_hour = user_local_time.hour
    current_minute = user_local_time.minute
    
    # Future deadline (1 hour from now)
    future_deadline_hour = (current_hour + 1) % 24
    future_deadline_minute = current_minute
    
    # Past deadline (1 hour ago)
    past_deadline_hour = (current_hour - 1) % 24
    past_deadline_minute = current_minute
    
    print(f"Future Deadline: {future_deadline_hour:02d}:{future_deadline_minute:02d} (should allow)")
    print(f"Past Deadline: {past_deadline_hour:02d}:{past_deadline_minute:02d} (should block)")
    print("=" * 60)
    
    tester = BrownModeRealisticTimezoneTest()
    
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
    
    # Step 1: Set Brown User with future deadline (should allow messaging)
    print(f"\n📝 Step 1: Set Brown User deadline to {future_deadline_hour:02d}:{future_deadline_minute:02d} (future)...")
    
    success, _ = tester.set_brown_mode(brown_user, future_deadline_hour, future_deadline_minute)
    if not success:
        print("❌ Failed to set brown mode")
        return 1
    
    # Step 2: Start conversation
    print("\n📝 Step 2: Start conversation...")
    success, _ = tester.start_conversation_with_timezone(sender_user, brown_user, timezone_offset_minutes)
    if not success:
        print("❌ Failed to start conversation")
        return 1
    
    # Step 3: Test messaging before deadline (should succeed)
    print(f"\n📝 Step 3: Test messaging before deadline ({current_hour:02d}:{current_minute:02d} < {future_deadline_hour:02d}:{future_deadline_minute:02d})...")
    
    success, _ = tester.send_message_with_timezone(
        sender_user, brown_user,
        f"Message before deadline at {current_hour:02d}:{current_minute:02d}",
        timezone_offset_minutes,
        expected_status=200
    )
    if not success:
        print("❌ Message failed before deadline")
        return 1
    
    # Step 4: Update to past deadline (should block messaging)
    print(f"\n📝 Step 4: Update Brown User deadline to {past_deadline_hour:02d}:{past_deadline_minute:02d} (past)...")
    
    success, _ = tester.set_brown_mode(brown_user, past_deadline_hour, past_deadline_minute)
    if not success:
        print("❌ Failed to update brown mode")
        return 1
    
    # Step 5: Test messaging after deadline (should be blocked)
    print(f"\n📝 Step 5: Test messaging after deadline ({current_hour:02d}:{current_minute:02d} > {past_deadline_hour:02d}:{past_deadline_minute:02d})...")
    
    success, _ = tester.send_message_with_timezone(
        sender_user, brown_user,
        f"Message after deadline at {current_hour:02d}:{current_minute:02d}",
        timezone_offset_minutes,
        expected_status=403
    )
    if not success:
        print("❌ Message was not blocked as expected")
        return 1
    
    # Step 6: Test with different timezone (UTC+0) to verify header usage
    print(f"\n📝 Step 6: Test with UTC+0 timezone (should behave differently)...")
    
    # Create another user
    user2 = f"user2_{timestamp}"
    if not tester.create_user(f"{user2}@test.com", "password123", "User 2", user2):
        print("❌ Failed to create User 2")
        return 1
    
    # With UTC+0, the current server time is used directly
    utc_offset = 0
    server_hour = now_utc.hour
    server_minute = now_utc.minute
    
    print(f"Server time: {server_hour:02d}:{server_minute:02d}, Deadline: {past_deadline_hour:02d}:{past_deadline_minute:02d}")
    
    # Start conversation
    success, _ = tester.start_conversation_with_timezone(user2, brown_user, utc_offset)
    if not success:
        print("❌ Failed to start conversation with UTC offset")
        return 1
    
    # Determine expected result based on server time vs deadline
    if server_hour > past_deadline_hour or (server_hour == past_deadline_hour and server_minute >= past_deadline_minute):
        expected_status = 403
        expected_result = "blocked"
    else:
        expected_status = 200
        expected_result = "allowed"
    
    print(f"Expected result with UTC+0: {expected_result} (status {expected_status})")
    
    success, _ = tester.send_message_with_timezone(
        user2, brown_user,
        f"Message with UTC+0 at {server_hour:02d}:{server_minute:02d}",
        utc_offset,
        expected_status=expected_status
    )
    if not success:
        print(f"❌ UTC+0 test failed")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode Timezone tests PASSED!")
        print("✅ Backend correctly uses CLIENT's timezone offset from headers")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())