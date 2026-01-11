#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class OrangeFreshStartTester:
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

    def set_orange_mode(self, user_id, token, max_contacts=3):
        """Set user to orange mode with specified max contacts"""
        success, response = self.run_test(
            f"Set Orange Mode (max={max_contacts})",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "orange",
                "availability": {
                    "maxContact": max_contacts
                }
            },
            token=token
        )
        if success:
            mode_started_at = response.get('availability', {}).get('modeStartedAt')
            self.log(f"   Orange mode set with modeStartedAt: {mode_started_at}")
        return success, response

    def get_user_info(self, user_id):
        """Get user information to check current contacts"""
        success, response = self.run_test(
            f"Get User Info {user_id}",
            "GET",
            f"users/{user_id}",
            200
        )
        if success:
            availability = response.get('availability', {})
            current_contacts = availability.get('currentContacts', 0)
            max_contacts = availability.get('maxContact', 0)
            mode = response.get('availabilityMode', 'unknown')
            mode_started_at = availability.get('modeStartedAt', 0)
            self.log(f"   User {user_id}: Mode={mode}, Contacts={current_contacts}/{max_contacts}, ModeStarted={mode_started_at}")
            return current_contacts, max_contacts, mode, mode_started_at
        return None, None, None, None

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
    tester = OrangeFreshStartTester()
    
    # Test timestamp for unique emails
    timestamp = int(time.time())
    
    try:
        tester.log("🚀 Starting Orange Mode 'Fresh Start' Test")
        tester.log("=" * 60)
        
        # Step 1: Create Orange User (Max=3)
        tester.log("\n📋 STEP 1: Create Orange User (Max=3)")
        orange_email = f"orange_fresh_{timestamp}@test.com"
        orange_user_id, orange_token = tester.create_user(orange_email, "password123", "Orange Fresh User")
        
        if not orange_user_id:
            tester.log("❌ Failed to create orange user")
            return 1
            
        # Set orange mode with max=3
        success, response = tester.set_orange_mode(orange_user_id, orange_token, max_contacts=3)
        if not success:
            tester.log("❌ Failed to set orange mode")
            return 1
            
        tester.orange_user_id = orange_user_id
        
        # Verify initial state
        current_contacts, max_contacts, mode, mode_started_at_1 = tester.get_user_info(orange_user_id)
        if mode != "orange" or current_contacts != 0 or max_contacts != 3:
            tester.log(f"❌ Orange user setup failed. Mode: {mode}, Contacts: {current_contacts}/{max_contacts}")
            return 1
            
        # Step 2: User 1, 2, 3 start chats and message
        tester.log("\n📋 STEP 2: User 1, 2, 3 start chats and message")
        user_emails = []
        user_tokens = []
        user_ids = []
        
        for i in range(1, 4):
            email = f"fresh_user_{i}_{timestamp}@test.com"
            user_id, token = tester.create_user(email, "password123", f"Fresh User {i}")
            
            if not user_id:
                tester.log(f"❌ Failed to create user {i}")
                return 1
                
            user_emails.append(email)
            user_tokens.append(token)
            user_ids.append(user_id)
            
            # Start chat with orange user
            conv_id = tester.start_chat(token, orange_user_id, should_succeed=True)
            if not conv_id:
                tester.log(f"❌ Failed to start chat for user {i}")
                return 1
            
            # Send message to actually burn the slot
            msg_id = tester.send_message(token, orange_user_id, f"Hello from Fresh User {i}!", should_succeed=True)
            if not msg_id:
                tester.log(f"❌ Failed to send message for user {i}")
                return 1
                
            # Verify count increased
            current_contacts, max_contacts, _, _ = tester.get_user_info(orange_user_id)
            expected_count = i
            if current_contacts != expected_count:
                tester.log(f"❌ Expected count {expected_count}, got {current_contacts}")
                return 1
            else:
                tester.log(f"✅ Count correctly updated to {current_contacts}/{max_contacts}")
        
        # Step 3: Verify count = 3/3
        tester.log("\n📋 STEP 3: Verify count = 3/3")
        current_contacts, max_contacts, mode, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 3 or max_contacts != 3:
            tester.log(f"❌ Expected 3/3, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Verified count is {current_contacts}/{max_contacts}")
        
        # Step 4: Set Max to 7 (via API) - This should trigger Fresh Start
        tester.log("\n📋 STEP 4: Set Max to 7 (via API) - Fresh Start")
        success, response = tester.set_orange_mode(orange_user_id, orange_token, max_contacts=7)
        if not success:
            tester.log("❌ Failed to update max contacts to 7")
            return 1
            
        # Step 5: Verify count resets to 0/7 (Fresh Start)
        tester.log("\n📋 STEP 5: Verify count resets to 0/7 (Fresh Start)")
        current_contacts, max_contacts, mode, mode_started_at_2 = tester.get_user_info(orange_user_id)
        
        if current_contacts != 0 or max_contacts != 7:
            tester.log(f"❌ Expected 0/7 after fresh start, got {current_contacts}/{max_contacts}")
            return 1
        
        if mode_started_at_2 <= mode_started_at_1:
            tester.log(f"❌ modeStartedAt should have been updated. Old: {mode_started_at_1}, New: {mode_started_at_2}")
            return 1
            
        tester.log(f"✅ Fresh Start successful! Count reset to {current_contacts}/{max_contacts}")
        tester.log(f"   modeStartedAt updated from {mode_started_at_1} to {mode_started_at_2}")
        
        # Step 6: User 4 messages -> 1/7
        tester.log("\n📋 STEP 6: User 4 messages -> 1/7")
        user4_email = f"fresh_user_4_{timestamp}@test.com"
        user4_id, user4_token = tester.create_user(user4_email, "password123", "Fresh User 4")
        
        if not user4_id:
            tester.log("❌ Failed to create user 4")
            return 1
            
        # Start chat and send message
        conv_id = tester.start_chat(user4_token, orange_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ Failed to start chat for user 4")
            return 1
            
        msg_id = tester.send_message(user4_token, orange_user_id, "Hello from Fresh User 4!", should_succeed=True)
        if not msg_id:
            tester.log("❌ Failed to send message for user 4")
            return 1
            
        # Verify count is now 1/7
        current_contacts, max_contacts, _, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 1 or max_contacts != 7:
            tester.log(f"❌ Expected 1/7 after user 4 message, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ User 4 message successful! Count is now {current_contacts}/{max_contacts}")
        
        # Step 7: User 1 (Old) messages again -> 2/7 (Counts as new in this session)
        tester.log("\n📋 STEP 7: User 1 (Old) messages again -> 2/7 (Counts as new in this session)")
        
        # User 1 sends another message (should count as new contact in fresh session)
        msg_id = tester.send_message(user_tokens[0], orange_user_id, "Hello again from Fresh User 1 (new session)!", should_succeed=True)
        if not msg_id:
            tester.log("❌ Failed to send message for user 1 (old)")
            return 1
            
        # Verify count is now 2/7
        current_contacts, max_contacts, _, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 2 or max_contacts != 7:
            tester.log(f"❌ Expected 2/7 after user 1 (old) message, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ User 1 (old) message successful! Count is now {current_contacts}/{max_contacts}")
            tester.log("   ✅ Old user correctly counts as NEW in fresh session")
        
        # Final verification
        tester.log("\n📋 FINAL VERIFICATION")
        current_contacts, max_contacts, mode, final_mode_started = tester.get_user_info(orange_user_id)
        tester.log(f"Final state - Mode: {mode}, Current Contacts: {current_contacts}/{max_contacts}")
        tester.log(f"Final modeStartedAt: {final_mode_started}")
        
        if current_contacts == 2 and max_contacts == 7 and mode == "orange":
            tester.log("✅ Orange Mode Fresh Start test PASSED!")
        else:
            tester.log("❌ Orange Mode Fresh Start test FAILED!")
            return 1
            
    except Exception as e:
        tester.log(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
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