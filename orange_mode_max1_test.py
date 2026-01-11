#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class OrangeModeMax1Tester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.user_ids = {}  # Store user IDs
        self.tests_run = 0
        self.tests_passed = 0
        self.orange_user_id = None

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

    def set_orange_mode(self, user_id, token, max_contacts=1):
        """Set user to orange mode with specified max contacts"""
        success, response = self.run_test(
            f"Set Orange Mode (max={max_contacts})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "orange",
                "availability": {
                    "maxContact": max_contacts,
                    "currentContacts": 0
                }
            },
            token=token
        )
        return success

    def get_user_info(self, user_id):
        """Get user information to check current contacts"""
        success, response = self.run_test(
            f"Get User Info {user_id}",
            "GET",
            f"users/{user_id}",
            200
        )
        if success:
            current_contacts = response.get('availability', {}).get('currentContacts', 0)
            max_contacts = response.get('availability', {}).get('maxContact', 0)
            mode = response.get('availabilityMode', 'unknown')
            self.log(f"   User {user_id}: Mode={mode}, CurrentContacts={current_contacts}/{max_contacts}")
            return current_contacts, max_contacts, mode
        return None, None, None

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
    tester = OrangeModeMax1Tester()
    
    # Test timestamp for unique emails
    timestamp = int(time.time())
    
    try:
        tester.log("🚀 Starting Orange Mode (Max=1) Message-Based Count Test")
        tester.log("=" * 70)
        
        # Step 1: Create Orange User (Max=1)
        tester.log("\n📋 STEP 1: Create Orange User (Max=1)")
        orange_email = f"orange_user_{timestamp}@test.com"
        orange_user_id, orange_token = tester.create_user(orange_email, "password123", "Orange User")
        
        if not orange_user_id:
            tester.log("❌ Failed to create orange user")
            return 1
            
        # Set orange mode with max=1
        if not tester.set_orange_mode(orange_user_id, orange_token, max_contacts=1):
            tester.log("❌ Failed to set orange mode")
            return 1
            
        tester.orange_user_id = orange_user_id
        
        # Verify initial state
        current_contacts, max_contacts, mode = tester.get_user_info(orange_user_id)
        if mode != "orange" or current_contacts != 0 or max_contacts != 1:
            tester.log(f"❌ Orange user setup failed. Mode: {mode}, Contacts: {current_contacts}/{max_contacts}")
            return 1
            
        # Step 2: User 1 starts chat. Verify count = 0/1 (because no message sent)
        tester.log("\n📋 STEP 2: User 1 starts chat. Verify count = 0/1 (no message sent)")
        user1_email = f"user_1_{timestamp}@test.com"
        user1_id, user1_token = tester.create_user(user1_email, "password123", "User 1")
        
        if not user1_id:
            tester.log("❌ Failed to create user 1")
            return 1
            
        # Start chat with orange user
        conv_id = tester.start_chat(user1_token, orange_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ Failed to start chat for user 1")
            return 1
            
        # Verify count is still 0 (no message sent yet)
        current_contacts, max_contacts, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 0:
            tester.log(f"❌ Expected count 0/1, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Count correctly remains at {current_contacts}/{max_contacts} (no message sent)")
            
        # Step 3: User 1 sends message. Verify count = 1/1
        tester.log("\n📋 STEP 3: User 1 sends message. Verify count = 1/1")
        msg_id = tester.send_message(user1_token, orange_user_id, "Hello from User 1!", should_succeed=True)
        if not msg_id:
            tester.log("❌ Failed to send message from user 1")
            return 1
            
        # Verify count increased to 1
        current_contacts, max_contacts, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 1:
            tester.log(f"❌ Expected count 1/1, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Count correctly updated to {current_contacts}/{max_contacts}")
            
        # Step 4: User 2 starts chat. Should this fail (403)?
        tester.log("\n📋 STEP 4: User 2 starts chat. Should fail (403)?")
        user2_email = f"user_2_{timestamp}@test.com"
        user2_id, user2_token = tester.create_user(user2_email, "password123", "User 2")
        
        if not user2_id:
            tester.log("❌ Failed to create user 2")
            return 1
            
        # This should fail with 403 because limit is reached
        conv_id = tester.start_chat(user2_token, orange_user_id, should_succeed=False)
        if conv_id is not None:
            tester.log("❌ User 2 should not have been able to start chat")
            return 1
            
        # Step 5: Verify User 2 cannot see "1/1 max contact" (blocked from opening chat)
        tester.log("\n📋 STEP 5: Verify User 2 is blocked from opening chat")
        # This is already verified in step 4 - start_chat failed with 403
        
        # Step 6: Test if User 2 could open chat (View Only) - this should fail based on backend logic
        tester.log("\n📋 STEP 6: User 2 cannot open chat (View Only) - blocked by backend")
        # The backend blocks start_chat when limit is reached, so no "View Only" mode
        
        # Step 7: Verify User 2 cannot send message (already blocked at chat level)
        tester.log("\n📋 STEP 7: User 2 cannot send message (blocked at chat level)")
        # Since start_chat failed, send_message would also fail
        msg_id = tester.send_message(user2_token, orange_user_id, "Hello from User 2!", should_succeed=False)
        if msg_id is not None:
            tester.log("❌ User 2 should not have been able to send message")
            return 1
            
        # Final verification
        tester.log("\n📋 FINAL VERIFICATION")
        current_contacts, max_contacts, mode = tester.get_user_info(orange_user_id)
        tester.log(f"Final state - Mode: {mode}, Current Contacts: {current_contacts}/{max_contacts}")
        
        if current_contacts == 1 and max_contacts == 1 and mode == "orange":
            tester.log("✅ Orange Mode (Max=1) Message-Based Count test PASSED!")
        else:
            tester.log("❌ Orange Mode (Max=1) Message-Based Count test FAILED!")
            return 1
            
    except Exception as e:
        tester.log(f"❌ Test failed with exception: {str(e)}")
        return 1
    
    finally:
        # Print results
        tester.log("\n" + "=" * 70)
        tester.log(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        
        if tester.tests_passed == tester.tests_run:
            tester.log("🎉 ALL TESTS PASSED!")
            return 0
        else:
            tester.log("💥 SOME TESTS FAILED!")
            return 1

if __name__ == "__main__":
    sys.exit(main())