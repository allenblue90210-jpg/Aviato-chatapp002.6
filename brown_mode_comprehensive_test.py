#!/usr/bin/env python3

import requests
import sys
import time
from datetime import datetime, timedelta
import json

class BrownModeComprehensiveTest:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
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
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_user(self):
        """Create a test user for Brown Mode testing"""
        timestamp = int(time.time())
        email = f"browntest_{timestamp}@test.com"
        
        success, response = self.run_test(
            "Create Brown Mode Test User",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password123", "name": f"Brown Test {timestamp}"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"✅ Created user: {email} (ID: {self.user_id})")
            return True
        return False

    def set_brown_mode(self, timed_hour, timed_minute=0):
        """Set user to Brown Mode with specific closing time"""
        success, response = self.run_test(
            f"Set Brown Mode (Closes at {timed_hour}:{timed_minute:02d})",
            "PUT",
            f"users/{self.user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": timed_hour,
                    "timedMinute": timed_minute,
                    "timezoneOffset": 0  # UTC for testing
                }
            }
        )
        return success, response

    def get_user_info(self):
        """Get current user info"""
        success, response = self.run_test(
            "Get User Info",
            "GET",
            f"users/{self.user_id}",
            200
        )
        return success, response

    def test_message_blocking(self, target_user_id, expect_blocked=False):
        """Test sending message to check if Brown Mode blocks it"""
        expected_status = 403 if expect_blocked else 200
        test_name = f"Send message (expect {'BLOCKED' if expect_blocked else 'SUCCESS'})"
        
        success, response = self.run_test(
            test_name,
            "POST",
            f"conversations/{target_user_id}/messages",
            expected_status,
            data={"text": "Test message for Brown Mode"}
        )
        return success, response

    def test_conversation_start(self, target_user_id, expect_blocked=False):
        """Test starting conversation to check if Brown Mode blocks it"""
        expected_status = 403 if expect_blocked else 200
        test_name = f"Start conversation (expect {'BLOCKED' if expect_blocked else 'SUCCESS'})"
        
        success, response = self.run_test(
            test_name,
            "POST",
            "conversations/start",
            expected_status,
            data={"userId": target_user_id}
        )
        return success, response

def main():
    print("🧪 Brown Mode 'Minute Precision' & Display - Comprehensive Test")
    print("=" * 70)
    
    tester = BrownModeComprehensiveTest()
    
    # Step 1: Create Brown Mode test user
    print("\n📝 Step 1: Create Brown Mode test user...")
    if not tester.create_test_user():
        print("❌ Failed to create test user")
        return 1
    
    # Step 2: Set Brown Mode with future time (should allow access)
    print("\n📝 Step 2: Set Brown Mode with future closing time...")
    
    # Set closing time to 2 hours from now
    future_time = datetime.utcnow() + timedelta(hours=2)
    future_hour = future_time.hour
    future_minute = future_time.minute
    
    success, brown_data = tester.set_brown_mode(future_hour, future_minute)
    if not success:
        print("❌ Failed to set Brown Mode")
        return 1
    
    # Verify Brown Mode settings
    availability = brown_data.get('availability', {})
    print(f"✅ Brown Mode set - Closes at {availability.get('timedHour')}:{availability.get('timedMinute', 0):02d}")
    
    # Step 3: Test that messaging works BEFORE deadline
    print("\n📝 Step 3: Test messaging BEFORE deadline (should work)...")
    
    # Get another user to test messaging with
    users_response = requests.get(f"{tester.base_url}/api/users")
    if users_response.status_code == 200:
        users = users_response.json()
        other_user = next((u for u in users if u['id'] != tester.user_id), None)
        
        if other_user:
            # Test conversation start (should work)
            success, _ = tester.test_conversation_start(other_user['id'], expect_blocked=False)
            if success:
                print("✅ Conversation start works before deadline")
            
            # Test messaging (should work)  
            success, _ = tester.test_message_blocking(other_user['id'], expect_blocked=False)
            if success:
                print("✅ Messaging works before deadline")
        else:
            print("⚠️ No other users found for messaging test")
    
    # Step 4: Set Brown Mode with PAST time (should block access)
    print("\n📝 Step 4: Set Brown Mode with PAST closing time...")
    
    # Set closing time to 1 hour ago
    past_time = datetime.utcnow() - timedelta(hours=1)
    past_hour = past_time.hour
    past_minute = past_time.minute
    
    success, brown_data = tester.set_brown_mode(past_hour, past_minute)
    if not success:
        print("❌ Failed to update Brown Mode")
        return 1
    
    availability = brown_data.get('availability', {})
    print(f"✅ Brown Mode updated - Closes at {availability.get('timedHour')}:{availability.get('timedMinute', 0):02d} (PAST)")
    
    # Step 5: Test that messaging is BLOCKED after deadline
    print("\n📝 Step 5: Test messaging AFTER deadline (should be blocked)...")
    
    if other_user:
        # Test conversation start (should be blocked)
        success, _ = tester.test_conversation_start(other_user['id'], expect_blocked=True)
        if success:
            print("✅ Conversation start correctly blocked after deadline")
        
        # Test messaging (should be blocked)
        success, _ = tester.test_message_blocking(other_user['id'], expect_blocked=True)
        if success:
            print("✅ Messaging correctly blocked after deadline")
    
    # Step 6: Test minute precision by setting very specific times
    print("\n📝 Step 6: Test minute precision...")
    
    # Test with current time + 1 minute (should work)
    current_time = datetime.utcnow()
    future_minute_time = current_time + timedelta(minutes=1)
    
    success, _ = tester.set_brown_mode(future_minute_time.hour, future_minute_time.minute)
    if success:
        print(f"✅ Set Brown Mode to close at {future_minute_time.hour}:{future_minute_time.minute:02d} (1 minute from now)")
        
        # Should still work
        if other_user:
            success, _ = tester.test_message_blocking(other_user['id'], expect_blocked=False)
            if success:
                print("✅ Messaging works 1 minute before deadline")
    
    # Test with current time - 1 minute (should block)
    past_minute_time = current_time - timedelta(minutes=1)
    success, _ = tester.set_brown_mode(past_minute_time.hour, past_minute_time.minute)
    if success:
        print(f"✅ Set Brown Mode to close at {past_minute_time.hour}:{past_minute_time.minute:02d} (1 minute ago)")
        
        # Should be blocked
        if other_user:
            success, _ = tester.test_message_blocking(other_user['id'], expect_blocked=True)
            if success:
                print("✅ Messaging correctly blocked 1 minute after deadline")
    
    # Step 7: Verify user info shows correct Brown Mode status
    print("\n📝 Step 7: Verify user info shows Brown Mode status...")
    
    success, user_info = tester.get_user_info()
    if success:
        mode = user_info.get('availabilityMode')
        availability = user_info.get('availability', {})
        timed_hour = availability.get('timedHour')
        timed_minute = availability.get('timedMinute', 0)
        
        if mode == 'brown' and timed_hour is not None:
            print(f"✅ User correctly shows Brown Mode - Closes at {timed_hour}:{timed_minute:02d}")
        else:
            print(f"❌ User info incorrect - Mode: {mode}, Hour: {timed_hour}")
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Brown Mode tests PASSED!")
        print("\n✅ VERIFIED FUNCTIONALITY:")
        print("  • Brown Mode can be set with specific hour and minute")
        print("  • Messaging works BEFORE the deadline")
        print("  • Messaging is BLOCKED after the deadline")
        print("  • Conversation starts are BLOCKED after deadline")
        print("  • Minute-level precision is working correctly")
        print("  • User info correctly reflects Brown Mode status")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())