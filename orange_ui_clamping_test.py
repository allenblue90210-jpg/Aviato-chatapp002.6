#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class OrangeUIClamping:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}
        self.user_ids = {}
        self.tests_run = 0
        self.tests_passed = 0
        self.orange_user_id = None
        self.user4_token = None

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
            self.log(f"   User {user_id}: Mode={mode}, CurrentContacts={current_contacts}, MaxContacts={max_contacts}")
            return current_contacts, max_contacts, mode
        return None, None, None

    def start_chat(self, from_token, target_user_id):
        """Start a chat with target user"""
        success, response = self.run_test(
            f"Start Chat with {target_user_id}",
            "POST",
            "conversations/start",
            200,
            data={"userId": target_user_id},
            token=from_token
        )
        
        if success:
            conv_id = response.get('id')
            status = response.get('status')
            self.log(f"   Chat started: ID={conv_id}, Status={status}")
            return conv_id
        return None

    def send_message(self, from_token, target_user_id, message_text):
        """Send a message to target user"""
        success, response = self.run_test(
            f"Send Message to {target_user_id}",
            "POST",
            f"conversations/{target_user_id}/messages",
            200,
            data={"text": message_text},
            token=from_token
        )
        
        if success:
            msg_id = response.get('id')
            self.log(f"   Message sent: ID={msg_id}")
            return msg_id
        return None

def main():
    tester = OrangeUIClamping()
    
    # Test timestamp for unique emails
    timestamp = int(time.time())
    
    try:
        tester.log("🚀 Starting Orange Mode UI Clamping Test")
        tester.log("=" * 60)
        
        # Step 1: Create Orange User (Max=2)
        tester.log("\n📋 STEP 1: Create Orange User (Max=2)")
        orange_email = f"orange_user_{timestamp}@test.com"
        orange_user_id, orange_token = tester.create_user(orange_email, "password123", "Orange User")
        
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
        if mode != "orange" or max_contacts != 2 or current_contacts != 0:
            tester.log(f"❌ Orange user setup failed. Mode: {mode}, Max: {max_contacts}, Current: {current_contacts}")
            return 1
            
        # Step 2: Create 3 conversations (via API to force state 3/2)
        tester.log("\n📋 STEP 2: Create 3 conversations to force 3/2 state")
        
        # Temporarily increase max to 3 to allow creation of 3 conversations
        tester.log("   Temporarily increasing max to 3...")
        if not tester.set_orange_mode(orange_user_id, orange_token, max_contacts=3):
            tester.log("❌ Failed to temporarily increase max contacts")
            return 1
        
        user_tokens = []
        
        for i in range(1, 4):
            email = f"user_{i}_{timestamp}@test.com"
            user_id, token = tester.create_user(email, "password123", f"User {i}")
            
            if not user_id:
                tester.log(f"❌ Failed to create user {i}")
                return 1
                
            user_tokens.append(token)
            
            # Start chat with orange user
            conv_id = tester.start_chat(token, orange_user_id)
            if not conv_id:
                tester.log(f"❌ Failed to start chat for user {i}")
                return 1
            
            # Send message to make it an active conversation
            msg_id = tester.send_message(token, orange_user_id, f"Hello from User {i}!")
            if not msg_id:
                tester.log(f"❌ Failed to send message for user {i}")
                return 1
                
            # Check current state
            current_contacts, max_contacts, _ = tester.get_user_info(orange_user_id)
            tester.log(f"   After User {i}: {current_contacts}/{max_contacts}")
        
        # Now reduce max back to 2 to create the 3/2 state
        tester.log("   Reducing max back to 2 to create 3/2 state...")
        if not tester.set_orange_mode(orange_user_id, orange_token, max_contacts=2):
            tester.log("❌ Failed to reduce max contacts back to 2")
            return 1
        
        # Step 3: Create User 4 for login
        tester.log("\n📋 STEP 3: Create User 4 for login")
        user4_email = f"user_4_{timestamp}@test.com"
        user4_id, user4_token = tester.create_user(user4_email, "password123", "User 4")
        
        if not user4_id:
            tester.log("❌ Failed to create user 4")
            return 1
            
        tester.user4_token = user4_token
        
        # Final verification of backend state
        tester.log("\n📋 BACKEND STATE VERIFICATION")
        current_contacts, max_contacts, mode = tester.get_user_info(orange_user_id)
        tester.log(f"Orange User Backend State: {current_contacts}/{max_contacts} (Mode: {mode})")
        
        if current_contacts == 3 and max_contacts == 2:
            tester.log("✅ Backend correctly shows 3/2 state (3 active conversations, max 2)")
        else:
            tester.log(f"❌ Expected 3/2 state, got {current_contacts}/{max_contacts}")
            return 1
            
        # Store data for UI test
        tester.log(f"\n📋 SETUP COMPLETE FOR UI TEST")
        tester.log(f"Orange User ID: {orange_user_id}")
        tester.log(f"User 4 Token: {user4_token}")
        tester.log(f"Backend State: {current_contacts}/{max_contacts}")
        tester.log(f"Expected UI Display: 2/2 (clamped)")
        
        return 0
            
    except Exception as e:
        tester.log(f"❌ Test failed with exception: {str(e)}")
        return 1
    
    finally:
        # Print results
        tester.log("\n" + "=" * 60)
        tester.log(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")

if __name__ == "__main__":
    sys.exit(main())