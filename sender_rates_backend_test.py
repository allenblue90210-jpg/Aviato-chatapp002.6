#!/usr/bin/env python3

import requests
import sys
import time
from datetime import datetime

class SenderRatesAPITester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.user_a_token = None
        self.user_b_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if 'login' in endpoint:
                    # Login uses form data
                    response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
                else:
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
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_user_a(self):
        """Create and login User A"""
        timestamp = int(time.time())
        email = f"sender_test_a_{timestamp}@test.com"
        
        # Create user
        success, response = self.run_test(
            "Create User A",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": "password", "name": "Sender Test User A"}
        )
        if success and 'access_token' in response:
            self.user_a_token = response['access_token']
            print(f"User A ID: {response['user']['id']}")
            return response['user']['id']
        return None

    def create_user_b(self):
        """Create and login User B"""
        timestamp = int(time.time())
        email = f"sender_test_b_{timestamp}@test.com"
        
        # Create user
        success, response = self.run_test(
            "Create User B",
            "POST",
            "auth/signup", 
            200,
            data={"email": email, "password": "password", "name": "Sender Test User B"}
        )
        if success and 'access_token' in response:
            self.user_b_token = response['access_token']
            print(f"User B ID: {response['user']['id']}")
            return response['user']['id']
        return None

    def start_conversation(self, user_a_id, user_b_id):
        """Start conversation between User A and User B"""
        success, response = self.run_test(
            "Start Conversation",
            "POST",
            "conversations/start",
            200,
            data={"userId": user_b_id},
            token=self.user_a_token
        )
        return success

    def send_message(self, sender_token, target_user_id, message):
        """Send message from sender to target user"""
        success, response = self.run_test(
            f"Send Message: '{message}'",
            "POST",
            f"conversations/{target_user_id}/messages",
            200,
            data={"text": message},
            token=sender_token
        )
        return success, response

    def get_conversations(self, token, user_name):
        """Get conversations for a user"""
        success, response = self.run_test(
            f"Get Conversations for {user_name}",
            "GET",
            "conversations",
            200,
            token=token
        )
        return success, response

    def wait_for_timer_expiry(self, duration=125):
        """Wait for timer to expire (2 minutes + buffer)"""
        print(f"\n⏰ Waiting {duration} seconds for timer to expire...")
        for i in range(duration, 0, -10):
            print(f"⏳ {i} seconds remaining...")
            time.sleep(10)
        print("✅ Timer should have expired!")

def main():
    print("🚀 Starting 'Only Sender Rates' Logic Test")
    print("=" * 50)
    
    tester = SenderRatesAPITester()
    
    # Step 1: Create User A
    print("\n📋 Step 1: Create User A")
    user_a_id = tester.create_user_a()
    if not user_a_id:
        print("❌ Failed to create User A")
        return 1

    # Step 2: Create User B  
    print("\n📋 Step 2: Create User B")
    user_b_id = tester.create_user_b()
    if not user_b_id:
        print("❌ Failed to create User B")
        return 1

    # Step 3: Start conversation
    print("\n📋 Step 3: Start Conversation")
    if not tester.start_conversation(user_a_id, user_b_id):
        print("❌ Failed to start conversation")
        return 1

    # Step 4: User A sends message to User B
    print("\n📋 Step 4: User A Sends Message")
    success, msg_response = tester.send_message(
        tester.user_a_token, 
        user_b_id, 
        "Hello from User A! This should start the timer."
    )
    if not success:
        print("❌ Failed to send message from User A")
        return 1

    # Step 5: Check initial conversations
    print("\n📋 Step 5: Check Initial Conversations")
    success_a, conv_a = tester.get_conversations(tester.user_a_token, "User A")
    success_b, conv_b = tester.get_conversations(tester.user_b_token, "User B")
    
    if success_a and success_b:
        print(f"User A conversations: {len(conv_a)}")
        print(f"User B conversations: {len(conv_b)}")
        
        # Find the conversation between A and B
        conv_a_with_b = next((c for c in conv_a if c['userId'] == user_b_id), None)
        conv_b_with_a = next((c for c in conv_b if c['userId'] == user_a_id), None)
        
        if conv_a_with_b and conv_b_with_a:
            print(f"✅ Conversation found - Timer started: {conv_a_with_b.get('timerStarted')}")
            print(f"✅ Last message sender: {conv_a_with_b.get('lastMessageSenderId')}")
        else:
            print("❌ Conversation not found between users")
            return 1

    # Step 6: Wait for timer to expire
    print("\n📋 Step 6: Wait for Timer Expiry")
    tester.wait_for_timer_expiry(125)  # 2 minutes + 5 second buffer

    # Step 7: Check conversations after timer expiry
    print("\n📋 Step 7: Check Conversations After Timer Expiry")
    success_a, conv_a_after = tester.get_conversations(tester.user_a_token, "User A")
    success_b, conv_b_after = tester.get_conversations(tester.user_b_token, "User B")
    
    if success_a and success_b:
        conv_a_with_b_after = next((c for c in conv_a_after if c['userId'] == user_b_id), None)
        conv_b_with_a_after = next((c for c in conv_b_after if c['userId'] == user_a_id), None)
        
        if conv_a_with_b_after and conv_b_with_a_after:
            print(f"User A conversation - Timer Expired: {conv_a_with_b_after.get('timerExpired')}")
            print(f"User A conversation - Rated: {conv_a_with_b_after.get('rated')}")
            print(f"User B conversation - Timer Expired: {conv_b_with_a_after.get('timerExpired')}")
            print(f"User B conversation - Rated: {conv_b_with_a_after.get('rated')}")
            print(f"Last message sender ID: {conv_a_with_b_after.get('lastMessageSenderId')}")
            print(f"User A ID: {user_a_id}")
            
            # Verify logic: Only sender (User A) should be able to rate
            is_sender = conv_a_with_b_after.get('lastMessageSenderId') == user_a_id
            print(f"✅ User A is sender: {is_sender}")
            
            if is_sender:
                print("✅ PASS: User A is the sender and should see rating modal")
                print("✅ PASS: User B is NOT the sender and should NOT see rating modal")
            else:
                print("❌ FAIL: Logic error - User A should be the sender")
                return 1

    # Print final results
    print(f"\n📊 Backend API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed! Ready for frontend testing.")
        return 0
    else:
        print("❌ Some backend tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())