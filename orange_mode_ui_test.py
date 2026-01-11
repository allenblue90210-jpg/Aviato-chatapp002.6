#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class OrangeModeUITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}
        self.user_ids = {}
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

    def set_orange_mode(self, user_id, token, max_contacts=2):
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
    """Test Orange Mode UI Clamping as per review request:
    1. Create Orange User (Max=2).
    2. User 1 sends message. Count 1/2.
    3. User 2 sends message. Count 2/2.
    4. User 3 (New) tries to send message.
    5. Should Fail (403).
    6. Verify Top Bar shows "2/2 max contact" (NOT 3/2).
    """
    tester = OrangeModeUITester()
    
    # Test timestamp for unique emails
    timestamp = int(time.time())
    
    try:
        tester.log("🚀 Starting Orange Mode UI Clamping Test (Max=2)")
        tester.log("=" * 60)
        
        # Step 1: Create Orange User (Max=2)
        tester.log("\n📋 STEP 1: Create Orange User (Max=2)")
        orange_email = f"orange_ui_user_{timestamp}@test.com"
        orange_user_id, orange_token = tester.create_user(orange_email, "password123", "Orange UI User")
        
        if not orange_user_id:
            tester.log("❌ Failed to create orange user")
            return 1
            
        # Set orange mode with max=2
        if not tester.set_orange_mode(orange_user_id, orange_token, max_contacts=2):
            tester.log("❌ Failed to set orange mode")
            return 1
            
        tester.orange_user_id = orange_user_id
        
        # Verify initial state
        current_contacts, max_contacts, mode = tester.get_user_info(orange_user_id)
        if mode != "orange" or current_contacts != 0 or max_contacts != 2:
            tester.log(f"❌ Orange user setup failed. Mode: {mode}, Contacts: {current_contacts}/{max_contacts}")
            return 1
            
        # Step 2: User 1 sends message. Count 1/2.
        tester.log("\n📋 STEP 2: User 1 sends message. Count 1/2.")
        user1_email = f"user_1_{timestamp}@test.com"
        user1_id, user1_token = tester.create_user(user1_email, "password123", "User 1")
        
        if not user1_id:
            tester.log("❌ Failed to create user 1")
            return 1
            
        # Start chat and send message
        conv_id = tester.start_chat(user1_token, orange_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ Failed to start chat for user 1")
            return 1
        
        msg_id = tester.send_message(user1_token, orange_user_id, "Hello from User 1!", should_succeed=True)
        if not msg_id:
            tester.log("❌ Failed to send message for user 1")
            return 1
            
        # Verify count is 1/2
        current_contacts, max_contacts, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 1 or max_contacts != 2:
            tester.log(f"❌ Expected count 1/2, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Count correctly shows {current_contacts}/{max_contacts}")
        
        # Step 3: User 2 sends message. Count 2/2.
        tester.log("\n📋 STEP 3: User 2 sends message. Count 2/2.")
        user2_email = f"user_2_{timestamp}@test.com"
        user2_id, user2_token = tester.create_user(user2_email, "password123", "User 2")
        
        if not user2_id:
            tester.log("❌ Failed to create user 2")
            return 1
            
        # Start chat and send message
        conv_id = tester.start_chat(user2_token, orange_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ Failed to start chat for user 2")
            return 1
        
        msg_id = tester.send_message(user2_token, orange_user_id, "Hello from User 2!", should_succeed=True)
        if not msg_id:
            tester.log("❌ Failed to send message for user 2")
            return 1
            
        # Verify count is 2/2
        current_contacts, max_contacts, _ = tester.get_user_info(orange_user_id)
        if current_contacts != 2 or max_contacts != 2:
            tester.log(f"❌ Expected count 2/2, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Count correctly shows {current_contacts}/{max_contacts}")
        
        # Step 4-5: User 3 (New) tries to send message. Should Fail (403).
        tester.log("\n📋 STEP 4-5: User 3 (New) tries to send message. Should Fail (403).")
        user3_email = f"user_3_{timestamp}@test.com"
        user3_id, user3_token = tester.create_user(user3_email, "password123", "User 3")
        
        if not user3_id:
            tester.log("❌ Failed to create user 3")
            return 1
            
        # Start chat should succeed (viewing is allowed)
        conv_id = tester.start_chat(user3_token, orange_user_id, should_succeed=True)
        if not conv_id:
            tester.log("❌ User 3 should be able to start chat (view mode)")
            return 1
            
        # But sending message should fail with 403
        msg_id = tester.send_message(user3_token, orange_user_id, "Hello from User 3!", should_succeed=False)
        if msg_id is not None:
            tester.log("❌ User 3 should not have been able to send message")
            return 1
            
        # Step 6: Verify Top Bar shows "2/2 max contact" (NOT 3/2).
        tester.log("\n📋 STEP 6: Verify Top Bar shows '2/2 max contact' (NOT 3/2).")
        current_contacts, max_contacts, mode = tester.get_user_info(orange_user_id)
        if current_contacts != 2 or max_contacts != 2:
            tester.log(f"❌ Expected count to remain 2/2, got {current_contacts}/{max_contacts}")
            return 1
        else:
            tester.log(f"✅ Count correctly shows {current_contacts}/{max_contacts} (NOT 3/2)")
            
        # Store user credentials for UI testing
        tester.log("\n📋 STORING USER CREDENTIALS FOR UI TESTING")
        credentials = {
            "orange_user": {"email": orange_email, "password": "password123", "id": orange_user_id},
            "user1": {"email": user1_email, "password": "password123", "id": user1_id},
            "user2": {"email": user2_email, "password": "password123", "id": user2_id},
            "user3": {"email": user3_email, "password": "password123", "id": user3_id}
        }
        
        with open('/app/test_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        tester.log("✅ Credentials saved to /app/test_credentials.json")
        tester.log("✅ Orange Mode UI Clamping Backend Test PASSED!")
            
    except Exception as e:
        tester.log(f"❌ Test failed with exception: {str(e)}")
        return 1
    
    finally:
        # Print results
        tester.log("\n" + "=" * 60)
        tester.log(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
        
        if tester.tests_passed == tester.tests_run:
            tester.log("🎉 ALL BACKEND TESTS PASSED!")
            return 0
        else:
            tester.log("💥 SOME BACKEND TESTS FAILED!")
            return 1

if __name__ == "__main__":
    sys.exit(main())