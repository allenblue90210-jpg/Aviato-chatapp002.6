#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class OrangeModeSettingsUpdateTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.orange_user_id = None
        self.other_user_token = None

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

    def login_as_orange_user(self):
        """Create a new user for testing"""
        timestamp = int(time.time())
        email = f"orange_test_{timestamp}@test.com"
        
        # Create new user
        success, response = self.run_test(
            "Create Orange Test User",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password123", "name": "Orange Test User"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.orange_user_id = self.user_id
            self.log(f"   Created user ID: {self.user_id}")
            return True
        return False

    def set_orange_mode(self, max_contacts=3):
        """Set user to orange mode with specified max contacts"""
        success, response = self.run_test(
            f"Set Orange Mode (max={max_contacts})",
            "PUT",
            f"users/{self.user_id}",
            200,
            data={
                "availabilityMode": "orange",
                "availability": {
                    "maxContact": max_contacts,
                    "currentContacts": 0
                }
            },
            token=self.token
        )
        return success, response

    def get_user_profile(self):
        """Get current user profile to check slots"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            f"users/{self.user_id}",
            200,
            token=self.token
        )
        if success:
            current_contacts = response.get('availability', {}).get('currentContacts', 0)
            max_contacts = response.get('availability', {}).get('maxContact', 0)
            mode = response.get('availabilityMode', 'unknown')
            self.log(f"   Profile: Mode={mode}, Slots={current_contacts}/{max_contacts}")
            return current_contacts, max_contacts, mode
        return None, None, None

    def create_other_user(self):
        """Create another user for testing conversations"""
        timestamp = int(time.time())
        email = f"test_user_{timestamp}@test.com"
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password123", "name": "Test User"}
        )
        
        if success and 'access_token' in response:
            self.other_user_token = response['access_token']
            other_user_id = response['user']['id']
            self.log(f"   Created test user ID: {other_user_id}")
            return other_user_id
        return None

    def start_conversation_and_send_message(self, other_user_id):
        """Start conversation and send message from other user to orange user"""
        # Start conversation
        success, response = self.run_test(
            "Start Conversation",
            "POST",
            "conversations/start",
            200,
            data={"userId": self.orange_user_id},
            token=self.other_user_token
        )
        
        if not success:
            return False
            
        # Send message to create active conversation
        success, response = self.run_test(
            "Send Message",
            "POST",
            f"conversations/{self.orange_user_id}/messages",
            200,
            data={"text": "Hello from test user!"},
            token=self.other_user_token
        )
        
        return success

def main():
    tester = OrangeModeSettingsUpdateTester()
    
    try:
        tester.log("🚀 Starting Orange Mode Settings Update Test")
        tester.log("=" * 60)
        
        # Step 1: Login as Orange User
        tester.log("\n📋 STEP 1: Login as Orange User")
        if not tester.login_as_orange_user():
            tester.log("❌ Failed to login as orange user")
            return 1
        
        # Step 2: Set to Orange Mode with 3 slots and verify "0/3 slots"
        tester.log("\n📋 STEP 2: Set Orange Mode (3 slots) and verify '0/3 slots'")
        success, response = tester.set_orange_mode(max_contacts=3)
        if not success:
            tester.log("❌ Failed to set orange mode")
            return 1
            
        current, max_contacts, mode = tester.get_user_profile()
        if mode != "orange" or current != 0 or max_contacts != 3:
            tester.log(f"❌ Expected orange mode with 0/3 slots, got {mode} with {current}/{max_contacts}")
            return 1
        tester.log("✅ Profile shows '0/3 slots' correctly")
        
        # Step 3: Change Limit to 2
        tester.log("\n📋 STEP 3: Change Limit to 2")
        success, response = tester.set_orange_mode(max_contacts=2)
        if not success:
            tester.log("❌ Failed to update limit to 2")
            return 1
            
        # Step 4: Verify Profile shows "0/2 slots" IMMEDIATELY
        tester.log("\n📋 STEP 4: Verify Profile shows '0/2 slots' IMMEDIATELY")
        current, max_contacts, mode = tester.get_user_profile()
        if mode != "orange" or current != 0 or max_contacts != 2:
            tester.log(f"❌ Expected orange mode with 0/2 slots, got {mode} with {current}/{max_contacts}")
            return 1
        tester.log("✅ Profile shows '0/2 slots' correctly after update")
        
        # Step 5: Create 1 conversation (User 1)
        tester.log("\n📋 STEP 5: Create 1 conversation (User 1)")
        other_user_id = tester.create_other_user()
        if not other_user_id:
            tester.log("❌ Failed to create other user")
            return 1
            
        if not tester.start_conversation_and_send_message(other_user_id):
            tester.log("❌ Failed to start conversation and send message")
            return 1
            
        # Wait a moment for backend to update
        time.sleep(1)
        
        # Step 6: Verify Profile shows "1/2 slots"
        tester.log("\n📋 STEP 6: Verify Profile shows '1/2 slots'")
        current, max_contacts, mode = tester.get_user_profile()
        if mode != "orange" or current != 1 or max_contacts != 2:
            tester.log(f"❌ Expected orange mode with 1/2 slots, got {mode} with {current}/{max_contacts}")
            return 1
        tester.log("✅ Profile shows '1/2 slots' correctly after conversation")
        
        # Step 7: Change Limit to 10
        tester.log("\n📋 STEP 7: Change Limit to 10")
        success, response = tester.set_orange_mode(max_contacts=10)
        if not success:
            tester.log("❌ Failed to update limit to 10")
            return 1
            
        # Step 8: Verify Profile shows "1/10 slots"
        tester.log("\n📋 STEP 8: Verify Profile shows '1/10 slots'")
        current, max_contacts, mode = tester.get_user_profile()
        if mode != "orange" or current != 1 or max_contacts != 10:
            tester.log(f"❌ Expected orange mode with 1/10 slots, got {mode} with {current}/{max_contacts}")
            return 1
        tester.log("✅ Profile shows '1/10 slots' correctly after limit increase")
        
        # Final verification
        tester.log("\n📋 FINAL VERIFICATION")
        tester.log(f"Final state - Mode: {mode}, Current Contacts: {current}, Max Contacts: {max_contacts}")
        
        if current == 1 and max_contacts == 10 and mode == "orange":
            tester.log("✅ Orange Mode Settings Update test PASSED!")
        else:
            tester.log("❌ Orange Mode Settings Update test FAILED!")
            return 1
            
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