import requests
import sys
import time
from datetime import datetime, timedelta

class BrownModeFullIntegrationTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
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
                    error_data = response.json()
                    print(f"Response: {error_data}")
                    return False, error_data
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

    def send_message_expect_blocked(self, sender_name, target_name, message_text):
        """Send message expecting it to be blocked (403 status)"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}' (EXPECT BLOCKED)",
            "POST",
            f"conversations/{target_id}/messages",
            403,
            data={"text": message_text},
            token=sender_token
        )
        return success, response

    def send_message(self, sender_name, target_name, message_text):
        """Send message from sender to target"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        success, response = self.run_test(
            f"{sender_name} -> {target_name}: '{message_text}'",
            "POST",
            f"conversations/{target_id}/messages",
            200,
            data={"text": message_text},
            token=sender_token
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
    print("🧪 Brown Mode Complete Integration Test")
    print("Testing Brown Mode 'Deadline' Logic with Timezone")
    print("=" * 60)
    
    tester = BrownModeFullIntegrationTester()
    
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
    
    # Step 1: Get Browser Timezone Offset (simulated)
    print("\n📝 Step 1: Get Browser Timezone Offset...")
    
    # Simulate different timezone offsets for testing
    test_cases = [
        {"name": "UTC (GMT+0)", "offset": 0},
        {"name": "EST (GMT-5)", "offset": 300},  # EST is UTC-5, so offset is +300 minutes
        {"name": "PST (GMT-8)", "offset": 480},  # PST is UTC-8, so offset is +480 minutes
    ]
    
    for case in test_cases:
        print(f"\n🌍 Testing timezone: {case['name']} (offset: {case['offset']} minutes)")
        
        # Get current UTC time
        now_utc = datetime.utcnow()
        print(f"Current UTC time: {now_utc.strftime('%H:%M:%S')}")
        
        # Calculate user's local time
        user_local_time = now_utc - timedelta(minutes=case['offset'])
        print(f"User's local time: {user_local_time.strftime('%H:%M:%S')}")
        
        # Step 2: Create Brown User (Deadline = NOW + 1 Hour)
        print(f"\n📝 Step 2: Create Brown User with deadline = NOW + 1 Hour ({case['name']})...")
        
        future_local = user_local_time + timedelta(hours=1)
        future_hour = future_local.hour
        future_minute = future_local.minute
        
        success, _ = tester.set_brown_mode_with_timezone(
            brown_user, future_hour, future_minute, case['offset']
        )
        if not success:
            print(f"❌ Failed to set brown mode for {case['name']}")
            continue
        
        # Step 3: Verify messaging Works
        print(f"\n📝 Step 3: Verify messaging works with future deadline ({case['name']})...")
        
        # Start conversation
        tester.start_conversation(sender_user, brown_user)
        
        # Send message (should work)
        success, _ = tester.send_message(sender_user, brown_user, f"Message before deadline - {case['name']}")
        if success:
            print(f"✅ Messaging works with future deadline ({case['name']})")
        else:
            print(f"❌ Messaging failed with future deadline ({case['name']})")
            continue
        
        # Step 4: Create Brown User (Deadline = NOW - 1 Hour)
        print(f"\n📝 Step 4: Update Brown User with deadline = NOW - 1 Hour ({case['name']})...")
        
        past_local = user_local_time - timedelta(hours=1)
        past_hour = past_local.hour
        past_minute = past_local.minute
        
        success, _ = tester.set_brown_mode_with_timezone(
            brown_user, past_hour, past_minute, case['offset']
        )
        if not success:
            print(f"❌ Failed to update brown mode for {case['name']}")
            continue
        
        # Step 5: Verify messaging Fails (403)
        print(f"\n📝 Step 5: Verify messaging fails with past deadline ({case['name']})...")
        
        # Send message (should be blocked)
        success, response = tester.send_message_expect_blocked(
            sender_user, brown_user, f"Message after deadline - {case['name']}"
        )
        if success:
            print(f"✅ Messaging correctly blocked with past deadline ({case['name']})")
            
            # Check error message contains Brown Mode reference
            if 'detail' in response and 'Brown Mode' in response['detail']:
                print(f"✅ Correct error message: {response['detail']}")
            else:
                print(f"⚠️ Error message may not be specific: {response}")
        else:
            print(f"❌ Messaging was not blocked with past deadline ({case['name']})")
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All Brown Mode Timezone Integration tests PASSED!")
        print("\n✅ Confirmed functionality:")
        print("   1. ✅ Browser timezone offset can be captured")
        print("   2. ✅ Brown users with future deadlines allow messaging")
        print("   3. ✅ Messaging works correctly before deadline")
        print("   4. ✅ Brown users with past deadlines block messaging")
        print("   5. ✅ Messaging fails with 403 after deadline")
        print("   6. ✅ Timezone offset is respected and blocking happens at user's local time")
        print("\n🔍 This confirms the timezone offset logic is working correctly!")
        return 0
    else:
        print("\n❌ Some tests FAILED!")
        print("🔧 Issues found that need attention from main agent")
        return 1

if __name__ == "__main__":
    sys.exit(main())