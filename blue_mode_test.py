#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import time

class BlueModeAPITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.user_ids = {}  # Store user IDs
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error details: {error_detail}")
                except:
                    self.log(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def create_user(self, email, password, name):
        """Create a new user via signup"""
        success, response = self.run_test(
            f"Create User {name}",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            user_id = response['user']['id']
            token = response['access_token']
            self.tokens[email] = token
            self.user_ids[email] = user_id
            self.log(f"   Created user {name} with ID: {user_id}")
            return user_id, token
        return None, None

    def set_blue_mode(self, user_id, token, future_date):
        """Set user to blue mode with future open date"""
        success, response = self.run_test(
            f"Set Blue Mode (openDate={future_date})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "blue",
                "availability": {
                    "openDate": future_date
                }
            },
            token=token
        )
        return success

    def get_user_info(self, user_id):
        """Get user information"""
        success, response = self.run_test(
            f"Get User Info {user_id}",
            "GET",
            f"users/{user_id}",
            200
        )
        if success:
            mode = response.get('availabilityMode', 'unknown')
            open_date = response.get('availability', {}).get('openDate', 'none')
            self.log(f"   User {user_id}: Mode={mode}, OpenDate={open_date}")
            return mode, open_date
        return None, None

    def start_chat(self, from_token, target_user_id, should_succeed=True):
        """Start a chat with target user"""
        expected_status = 200 if should_succeed else 403
        test_name = f"Start Chat with {target_user_id}" + ("" if should_succeed else " (Should Fail)")
        
        success, response = self.run_test(
            test_name,
            "POST",
            "conversations/start",
            expected_status,
            data={"userId": target_user_id},
            token=from_token
        )
        
        if success and should_succeed:
            conv_id = response.get('id')
            status = response.get('status')
            self.log(f"   Chat started: ID={conv_id}, Status={status}")
            return conv_id
        elif success and not should_succeed:
            self.log(f"   ✅ Correctly blocked chat attempt")
            return None
        else:
            return None

    def send_message(self, from_token, target_user_id, message_text, should_succeed=True):
        """Send a message to target user"""
        expected_status = 200 if should_succeed else 403
        test_name = f"Send Message to {target_user_id}" + ("" if should_succeed else " (Should Fail)")
        
        success, response = self.run_test(
            test_name,
            "POST",
            f"conversations/{target_user_id}/messages",
            expected_status,
            data={"text": message_text},
            token=from_token
        )
        
        if success and should_succeed:
            msg_id = response.get('id')
            self.log(f"   Message sent: ID={msg_id}")
            return msg_id
        elif success and not should_succeed:
            self.log(f"   ✅ Correctly blocked message attempt")
            return None
        else:
            return None

def main():
    tester = BlueModeAPITester()
    
    # Test timestamp for unique emails
    timestamp = int(time.time())
    
    try:
        tester.log("🚀 Starting Blue Mode Strict Blocking Test")
        tester.log("=" * 60)
        
        # Step 1: Create Blue User with Future Date
        tester.log("\n📋 STEP 1: Create Blue User with Future Date")
        
        # Calculate future date (tomorrow)
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tester.log(f"   Using future date: {future_date}")
        
        blue_email = f"blue_user_{timestamp}@test.com"
        blue_user_id, blue_token = tester.create_user(blue_email, "password123", "Blue User")
        
        if not blue_user_id:
            tester.log("❌ Failed to create blue user")
            return 1
            
        # Set blue mode with future date
        if not tester.set_blue_mode(blue_user_id, blue_token, future_date):
            tester.log("❌ Failed to set blue mode")
            return 1
        
        # Verify blue mode setup
        mode, open_date = tester.get_user_info(blue_user_id)
        if mode != "blue" or open_date != future_date:
            tester.log(f"❌ Blue user setup failed. Mode: {mode}, OpenDate: {open_date}")
            return 1
        
        # Step 2: Create Regular User (User 1)
        tester.log("\n📋 STEP 2: Create Regular User (User 1)")
        user1_email = f"user1_{timestamp}@test.com"
        user1_id, user1_token = tester.create_user(user1_email, "password123", "User 1")
        
        if not user1_id:
            tester.log("❌ Failed to create user 1")
            return 1
        
        # Step 3: User 1 tries to start chat - should fail with 403
        tester.log("\n📋 STEP 3: User 1 tries to start chat - should fail (403)")
        conv_id = tester.start_chat(user1_token, blue_user_id, should_succeed=False)
        if conv_id is not None:
            tester.log("❌ User 1 should not have been able to start chat")
            return 1
        
        # Step 4: User 1 tries to send message - should fail with 403
        tester.log("\n📋 STEP 4: User 1 tries to send message - should fail (403)")
        msg_id = tester.send_message(user1_token, blue_user_id, "Hello Blue User!", should_succeed=False)
        if msg_id is not None:
            tester.log("❌ User 1 should not have been able to send message")
            return 1
        
        # Step 5: Test with past date (should work)
        tester.log("\n📋 STEP 5: Test Blue Mode with Past Date (should work)")
        
        # Set blue mode with past date
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tester.log(f"   Using past date: {past_date}")
        
        if not tester.set_blue_mode(blue_user_id, blue_token, past_date):
            tester.log("❌ Failed to set blue mode with past date")
            return 1
        
        # Now User 1 should be able to start chat
        conv_id = tester.start_chat(user1_token, blue_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ User 1 should be able to start chat with past date")
            return 1
        
        # And send message
        msg_id = tester.send_message(user1_token, blue_user_id, "Hello Blue User (past date)!", should_succeed=True)
        if not msg_id:
            tester.log("❌ User 1 should be able to send message with past date")
            return 1
        
        # Step 6: Set back to future date and verify blocking again
        tester.log("\n📋 STEP 6: Set back to future date and verify blocking again")
        
        if not tester.set_blue_mode(blue_user_id, blue_token, future_date):
            tester.log("❌ Failed to set blue mode back to future date")
            return 1
        
        # Create another user to test
        user2_email = f"user2_{timestamp}@test.com"
        user2_id, user2_token = tester.create_user(user2_email, "password123", "User 2")
        
        if not user2_id:
            tester.log("❌ Failed to create user 2")
            return 1
        
        # User 2 should be blocked from starting chat
        conv_id = tester.start_chat(user2_token, blue_user_id, should_succeed=False)
        if conv_id is not None:
            tester.log("❌ User 2 should be blocked from starting chat")
            return 1
        
        # User 2 should be blocked from sending message
        msg_id = tester.send_message(user2_token, blue_user_id, "Hello from User 2!", should_succeed=False)
        if msg_id is not None:
            tester.log("❌ User 2 should be blocked from sending message")
            return 1
        
        tester.log("\n✅ Blue Mode Strict Blocking test PASSED!")
        tester.log("   - Future date correctly blocks all access")
        tester.log("   - Past date allows normal access")
        tester.log("   - Both start_chat and send_message endpoints respect blue mode")
            
    except Exception as e:
        tester.log(f"❌ Test failed with exception: {str(e)}")
        return 1
    
    finally:
        # Print results
        tester.log("\n" + "=" * 60)
        tester.log(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        
        if tester.tests_passed == tester.tests_run:
            tester.log("🎉 ALL TESTS PASSED!")
            return 0
        else:
            tester.log("💥 SOME TESTS FAILED!")
            return 1

if __name__ == "__main__":
    sys.exit(main())