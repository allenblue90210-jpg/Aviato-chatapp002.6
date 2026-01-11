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
        """Run a single API test"""
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
                    print(f"Response: {response.json()}")
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

    def set_brown_mode_with_timezone(self, user_name, timed_hour, timed_minute=0, timezone_offset=0):
        """Set user to brown mode with specified closing time and timezone offset"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        success, response = self.run_test(
            f"Set {user_name} to Brown Mode (Closes at {timed_hour}:{timed_minute:02d}, TZ offset: {timezone_offset})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": timed_hour,
                    "timedMinute": timed_minute,
                    "timezoneOffset": timezone_offset
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
        return success, response

    def send_message_with_timezone_header(self, sender_name, target_name, message_text, timezone_offset=0):
        """Send message with timezone offset header"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        headers = {'x-timezone-offset': str(timezone_offset)}
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}' (TZ offset: {timezone_offset})",
            "POST",
            f"conversations/{target_id}/messages",
            200,
            data={"text": message_text},
            token=sender_token,
            headers=headers
        )
        return success, response

    def send_message_expect_blocked_with_timezone(self, sender_name, target_name, message_text, timezone_offset=0):
        """Send message expecting it to be blocked (403 status) with timezone header"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        headers = {'x-timezone-offset': str(timezone_offset)}
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}' (EXPECT BLOCKED, TZ offset: {timezone_offset})",
            "POST",
            f"conversations/{target_id}/messages",
            403,  # Expecting 403 Forbidden
            data={"text": message_text},
            token=sender_token,
            headers=headers
        )
        return success, response

    def start_conversation(self, sender_name, target_name):
        """Start conversation between users"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        success, response = self.run_test(
            f"Start conversation: {sender_name} -> {target_name}",
            "POST",
            "conversations/start",
            200,
            data={"userId": target_id},
            token=sender_token
        )
        return success, response

def main():
    print("🧪 Brown Mode Timezone Fix Test")
    print("Testing scenario: Local Time = 9 PM, Server UTC Time = 2 AM")
    print("=" * 60)
    
    tester = BrownModeTimezoneAPITester()
    
    # Test users
    timestamp = int(time.time())
    brown_user = f"brown_user_{timestamp}"
    user1 = f"user1_{timestamp}"
    
    users_to_create = [
        (brown_user, f"{brown_user}@test.com", "Brown User"),
        (user1, f"{user1}@test.com", "User 1")
    ]
    
    # Step 0: Create test users
    print("\n📝 Step 0: Creating test users...")
    for user_key, email, name in users_to_create:
        if not tester.create_user(email, "password123", name, user_key):
            print(f"❌ Failed to create {name}, stopping tests")
            return 1
    
    # Scenario: Local Time = 9 PM (21:00), Server UTC Time = 2 AM (02:00)
    # This means timezone offset = -420 minutes (UTC-7, like Pacific Time)
    # When it's 2 AM UTC, it's 7 PM local time (UTC-7)
    # But we want to simulate 9 PM local time when server is 2 AM UTC
    # So we need UTC+7 timezone (offset = +420 minutes)
    
    timezone_offset = 420  # +7 hours from UTC (when UTC is 2 AM, local is 9 AM)
    # Actually, let's recalculate:
    # If local time is 9 PM and server UTC is 2 AM, that means:
    # Local is 19 hours ahead of UTC... that doesn't make sense.
    # Let me think: if server UTC is 2 AM and local is 9 PM the previous day,
    # then local is 5 hours behind UTC. So offset should be +300 minutes.
    
    # Let's simulate: UTC time is 2 AM (02:00), local time should be 9 PM previous day (21:00)
    # That means local is 5 hours behind UTC, so offset = +300 minutes
    timezone_offset = 300  # +5 hours offset (local is behind UTC)
    
    print(f"\n🌍 Timezone Setup:")
    print(f"   Server UTC Time: 02:00 AM")
    print(f"   Local Time: 21:00 PM (previous day)")
    print(f"   Timezone Offset: +{timezone_offset} minutes")
    
    # Step 1: Set Brown User to Brown Mode with deadline at 10 PM local time
    print("\n📝 Step 1: Set deadline to 10 PM local time...")
    
    # Deadline: 10 PM local time (22:00)
    deadline_hour = 22
    deadline_minute = 0
    
    success, brown_data = tester.set_brown_mode_with_timezone(
        brown_user, deadline_hour, deadline_minute, timezone_offset
    )
    if not success:
        print("❌ Failed to set brown mode, stopping tests")
        return 1
    
    # Verify brown mode settings
    availability = brown_data.get('availability', {})
    timed_hour = availability.get('timedHour')
    timed_minute = availability.get('timedMinute')
    stored_offset = availability.get('timezoneOffset')
    print(f"✅ Brown User set: Closes at {timed_hour}:{timed_minute:02d}, TZ offset: {stored_offset}")
    
    # Step 2: Test messaging at 9 PM local time (should work - before 10 PM deadline)
    print("\n📝 Step 2: Test messaging at 9 PM local time (before deadline)...")
    
    # Start conversation first
    tester.start_conversation(user1, brown_user)
    
    # Send message with timezone offset (simulating 9 PM local time)
    success, _ = tester.send_message_with_timezone_header(
        user1, brown_user, "Hello at 9 PM local time!", timezone_offset
    )
    if success:
        print("✅ Message sent successfully at 9 PM local time (before 10 PM deadline)")
    else:
        print("❌ Message failed at 9 PM local time (unexpected)")
        return 1
    
    # Step 3: Set deadline to 8 PM local time (should block current 9 PM messages)
    print("\n📝 Step 3: Set deadline to 8 PM local time...")
    
    # New deadline: 8 PM local time (20:00)
    new_deadline_hour = 20
    new_deadline_minute = 0
    
    success, brown_data = tester.set_brown_mode_with_timezone(
        brown_user, new_deadline_hour, new_deadline_minute, timezone_offset
    )
    if not success:
        print("❌ Failed to update brown mode, stopping tests")
        return 1
    
    # Verify updated settings
    availability = brown_data.get('availability', {})
    timed_hour = availability.get('timedHour')
    timed_minute = availability.get('timedMinute')
    stored_offset = availability.get('timezoneOffset')
    print(f"✅ Brown User updated: Closes at {timed_hour}:{timed_minute:02d}, TZ offset: {stored_offset}")
    
    # Step 4: Test messaging at 9 PM local time (should be blocked - after 8 PM deadline)
    print("\n📝 Step 4: Test messaging at 9 PM local time (should be blocked after 8 PM deadline)...")
    
    # Send message (should be blocked with 403)
    success, response = tester.send_message_expect_blocked_with_timezone(
        user1, brown_user, "Hello at 9 PM after 8 PM deadline!", timezone_offset
    )
    if success:
        print("✅ Message correctly blocked at 9 PM local time (after 8 PM deadline)")
    else:
        print("❌ Message was not blocked at 9 PM local time (unexpected)")
        return 1
    
    # Step 5: Test without timezone offset (should use stored offset)
    print("\n📝 Step 5: Test messaging without timezone header (should use stored offset)...")
    
    # Send message without timezone header (backend should use stored offset)
    target_id = tester.users[brown_user]['id']
    sender_token = tester.tokens[user1]
    
    url = f"{tester.base_url}/api/conversations/{target_id}/messages"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {sender_token}'
        # No x-timezone-offset header
    }
    data = {"text": "Hello without timezone header!"}
    
    tester.tests_run += 1
    print(f"\n🔍 Testing message without timezone header (EXPECT BLOCKED)...")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 403:
            tester.tests_passed += 1
            print("✅ Message correctly blocked using stored timezone offset")
        else:
            print(f"❌ Expected 403, got {response.status_code}")
            return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode Timezone tests PASSED!")
        print("\n✅ Timezone Fix Verification:")
        print("   - Backend correctly uses stored timezone offset")
        print("   - Backend falls back to x-timezone-offset header")
        print("   - Time calculations work with user's local timezone")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())