#!/usr/bin/env python3

import requests
import sys
import time
from datetime import datetime, timedelta
import json

class BrownModeCorrectTest:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.sender_token = None
        self.sender_id = None
        self.brown_user_token = None
        self.brown_user_id = None
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
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_user(self, email_suffix, name):
        """Create a test user"""
        timestamp = int(time.time())
        email = f"{email_suffix}_{timestamp}@test.com"
        
        success, response = self.run_test(
            f"Create User: {name}",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password123", "name": name}
        )
        
        if success and 'access_token' in response:
            return response['access_token'], response['user']['id'], email
        return None, None, None

    def set_brown_mode(self, user_id, token, timed_hour, timed_minute=0):
        """Set user to Brown Mode with specific closing time"""
        success, response = self.run_test(
            f"Set Brown Mode (Closes at {timed_hour}:{timed_minute:02d})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": timed_hour,
                    "timedMinute": timed_minute,
                    "timezoneOffset": 0  # UTC for testing
                }
            },
            token=token
        )
        return success, response

    def test_message_to_brown_user(self, sender_token, brown_user_id, expect_blocked=False):
        """Test sending message TO a Brown Mode user"""
        expected_status = 403 if expect_blocked else 200
        test_name = f"Send message TO Brown Mode user (expect {'BLOCKED' if expect_blocked else 'SUCCESS'})"
        
        success, response = self.run_test(
            test_name,
            "POST",
            f"conversations/{brown_user_id}/messages",
            expected_status,
            data={"text": "Test message to Brown Mode user"},
            token=sender_token
        )
        return success, response

    def test_conversation_start_with_brown_user(self, sender_token, brown_user_id, expect_blocked=False):
        """Test starting conversation WITH a Brown Mode user"""
        expected_status = 403 if expect_blocked else 200
        test_name = f"Start conversation WITH Brown Mode user (expect {'BLOCKED' if expect_blocked else 'SUCCESS'})"
        
        success, response = self.run_test(
            test_name,
            "POST",
            "conversations/start",
            expected_status,
            data={"userId": brown_user_id},
            token=sender_token
        )
        return success, response

def main():
    print("🧪 Brown Mode 'Minute Precision' & Display - CORRECTED Test")
    print("=" * 70)
    print("Testing: Messages TO Brown Mode users should be blocked after deadline")
    
    tester = BrownModeCorrectTest()
    
    # Step 1: Create two users - one sender, one Brown Mode user
    print("\n📝 Step 1: Create test users...")
    
    sender_token, sender_id, sender_email = tester.create_user("sender", "Message Sender")
    if not sender_token:
        print("❌ Failed to create sender user")
        return 1
    
    brown_token, brown_user_id, brown_email = tester.create_user("brownuser", "Brown Mode User")
    if not brown_token:
        print("❌ Failed to create Brown Mode user")
        return 1
    
    print(f"✅ Created sender: {sender_email}")
    print(f"✅ Created Brown Mode user: {brown_email}")
    
    # Step 2: Set Brown Mode user with FUTURE time (should allow messaging)
    print("\n📝 Step 2: Set Brown Mode user with FUTURE closing time...")
    
    future_time = datetime.utcnow() + timedelta(hours=2)
    future_hour = future_time.hour
    future_minute = future_time.minute
    
    success, brown_data = tester.set_brown_mode(brown_user_id, brown_token, future_hour, future_minute)
    if not success:
        print("❌ Failed to set Brown Mode")
        return 1
    
    print(f"✅ Brown Mode user set to close at {future_hour}:{future_minute:02d} (FUTURE)")
    
    # Step 3: Test messaging TO Brown Mode user BEFORE deadline (should work)
    print("\n📝 Step 3: Test messaging TO Brown Mode user BEFORE deadline...")
    
    success, _ = tester.test_conversation_start_with_brown_user(sender_token, brown_user_id, expect_blocked=False)
    if success:
        print("✅ Conversation start works before deadline")
    
    success, _ = tester.test_message_to_brown_user(sender_token, brown_user_id, expect_blocked=False)
    if success:
        print("✅ Messaging works before deadline")
    
    # Step 4: Set Brown Mode user with PAST time (should block messaging)
    print("\n📝 Step 4: Set Brown Mode user with PAST closing time...")
    
    past_time = datetime.utcnow() - timedelta(hours=1)
    past_hour = past_time.hour
    past_minute = past_time.minute
    
    success, brown_data = tester.set_brown_mode(brown_user_id, brown_token, past_hour, past_minute)
    if not success:
        print("❌ Failed to update Brown Mode")
        return 1
    
    print(f"✅ Brown Mode user updated to close at {past_hour}:{past_minute:02d} (PAST)")
    
    # Step 5: Test messaging TO Brown Mode user AFTER deadline (should be blocked)
    print("\n📝 Step 5: Test messaging TO Brown Mode user AFTER deadline...")
    
    success, _ = tester.test_conversation_start_with_brown_user(sender_token, brown_user_id, expect_blocked=True)
    if success:
        print("✅ Conversation start correctly blocked after deadline")
    
    success, _ = tester.test_message_to_brown_user(sender_token, brown_user_id, expect_blocked=True)
    if success:
        print("✅ Messaging correctly blocked after deadline")
    
    # Step 6: Test minute precision
    print("\n📝 Step 6: Test minute precision...")
    
    current_time = datetime.utcnow()
    
    # Test 1 minute in future (should work)
    future_minute_time = current_time + timedelta(minutes=1)
    success, _ = tester.set_brown_mode(brown_user_id, brown_token, future_minute_time.hour, future_minute_time.minute)
    if success:
        print(f"✅ Set Brown Mode to close at {future_minute_time.hour}:{future_minute_time.minute:02d} (1 minute from now)")
        
        success, _ = tester.test_message_to_brown_user(sender_token, brown_user_id, expect_blocked=False)
        if success:
            print("✅ Messaging works 1 minute before deadline")
    
    # Test 1 minute in past (should block)
    past_minute_time = current_time - timedelta(minutes=1)
    success, _ = tester.set_brown_mode(brown_user_id, brown_token, past_minute_time.hour, past_minute_time.minute)
    if success:
        print(f"✅ Set Brown Mode to close at {past_minute_time.hour}:{past_minute_time.minute:02d} (1 minute ago)")
        
        success, _ = tester.test_message_to_brown_user(sender_token, brown_user_id, expect_blocked=True)
        if success:
            print("✅ Messaging correctly blocked 1 minute after deadline")
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode tests PASSED!")
        print("\n✅ VERIFIED FUNCTIONALITY:")
        print("  • Brown Mode blocks messages TO users after their deadline")
        print("  • Brown Mode blocks conversation starts after deadline")
        print("  • Minute-level precision works correctly")
        print("  • Time comparison logic is accurate")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())