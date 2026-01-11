#!/usr/bin/env python3

import requests
import sys
import time
from datetime import datetime

class RatingModalDoubleShowTest:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                if 'auth/login' in endpoint:
                    # OAuth2PasswordRequestForm expects form data
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    response = requests.post(url, data=data, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, email, password):
        """Test login endpoint"""
        success, response = self.run_test(
            "Login API",
            "POST",
            "api/auth/login",
            200,
            data={"username": email, "password": password}
        )
        if success and isinstance(response, dict) and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
            print(f"   User: {response.get('user', {}).get('name', 'Unknown')}")
            return True, response
        return False, response

    def test_start_chat(self, target_user_id):
        """Test starting a chat with a user"""
        success, response = self.run_test(
            f"Start Chat with User {target_user_id}",
            "POST",
            "api/conversations/start",
            200,
            data={"userId": target_user_id}
        )
        return success, response

    def test_send_message(self, target_user_id, message_text):
        """Test sending a message to a user"""
        success, response = self.run_test(
            f"Send Message to User {target_user_id}",
            "POST",
            f"api/conversations/{target_user_id}/messages",
            200,
            data={"text": message_text}
        )
        return success, response

    def test_rate_conversation(self, target_user_id, is_good, reason):
        """Test rating a conversation"""
        success, response = self.run_test(
            f"Rate Conversation with User {target_user_id} ({'POSITIVE' if is_good else 'NEGATIVE'})",
            "POST",
            f"api/conversations/{target_user_id}/rate",
            200,
            data={"isGood": is_good, "reason": reason}
        )
        return success, response

    def test_get_conversations(self):
        """Test getting conversations"""
        success, response = self.run_test(
            "Get Conversations",
            "GET",
            "api/conversations",
            200
        )
        return success, response

def main():
    print("🎯 Starting Rating Modal Double Show Fix Test")
    print("=" * 60)
    
    # Setup
    tester = RatingModalDoubleShowTest()
    
    # Test 1: Login with demo credentials
    print("\n📋 Test 1: Login with demo credentials")
    login_success, login_response = tester.test_login("demo@aviato.com", "password")
    
    if not login_success:
        print("❌ Login failed - cannot proceed with other tests")
        print(f"\n📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
        return 1

    # Test 2: Start a chat with John (user id "6")
    print("\n📋 Test 2: Start chat with John (user id '6')")
    start_chat_success, start_chat_response = tester.test_start_chat("6")
    
    # Test 3: Send first message to start timer
    print("\n📋 Test 3: Send first message to start timer")
    send_msg1_success, send_msg1_response = tester.test_send_message("6", "Hello John! Testing rating modal fix - message 1")
    
    # Test 4: Get conversations to check timer started
    print("\n📋 Test 4: Check conversations after first message")
    conv_success, conv_response = tester.test_get_conversations()
    
    john_conversation = None
    if conv_success and isinstance(conv_response, list):
        for conv in conv_response:
            if conv.get('userId') == '6':  # John's conversation
                john_conversation = conv
                print(f"   Found John's conversation:")
                print(f"   - Timer Started: {conv.get('timerStarted')}")
                print(f"   - Rated: {conv.get('rated', False)}")
                print(f"   - Timer Expired: {conv.get('timerExpired', False)}")
                break
    
    if not john_conversation:
        print("❌ Could not find John's conversation")
        return 1
    
    # Test 5: Rate the conversation (simulate timer expiry)
    print("\n📋 Test 5: Rate the conversation (Good)")
    rate_success, rate_response = tester.test_rate_conversation("6", True, "Great conversation!")
    
    # Test 6: Check conversation state after rating
    print("\n📋 Test 6: Check conversation state after rating")
    conv_after_rating_success, conv_after_rating_response = tester.test_get_conversations()
    
    john_conversation_after_rating = None
    if conv_after_rating_success and isinstance(conv_after_rating_response, list):
        for conv in conv_after_rating_response:
            if conv.get('userId') == '6':  # John's conversation
                john_conversation_after_rating = conv
                print(f"   John's conversation after rating:")
                print(f"   - Timer Started: {conv.get('timerStarted')}")
                print(f"   - Rated: {conv.get('rated', False)}")
                print(f"   - Timer Expired: {conv.get('timerExpired', False)}")
                break
    
    if not john_conversation_after_rating:
        print("❌ Could not find John's conversation after rating")
        return 1
    
    # Verify conversation is marked as rated
    if john_conversation_after_rating.get('rated'):
        print("✅ Conversation correctly marked as rated")
        tester.tests_passed += 1
    else:
        print("❌ Conversation not marked as rated")
    tester.tests_run += 1
    
    # Test 7: Send ANOTHER message to restart timer (this is the key test)
    print("\n📋 Test 7: Send ANOTHER message to restart timer")
    send_msg2_success, send_msg2_response = tester.test_send_message("6", "Testing second message after rating - should restart timer")
    
    # Test 8: Check conversation state after second message (critical test)
    print("\n📋 Test 8: Check conversation state after second message")
    conv_after_second_msg_success, conv_after_second_msg_response = tester.test_get_conversations()
    
    john_conversation_after_second_msg = None
    if conv_after_second_msg_success and isinstance(conv_after_second_msg_response, list):
        for conv in conv_after_second_msg_response:
            if conv.get('userId') == '6':  # John's conversation
                john_conversation_after_second_msg = conv
                print(f"   John's conversation after second message:")
                print(f"   - Timer Started: {conv.get('timerStarted')}")
                print(f"   - Rated: {conv.get('rated', False)}")
                print(f"   - Timer Expired: {conv.get('timerExpired', False)}")
                break
    
    if not john_conversation_after_second_msg:
        print("❌ Could not find John's conversation after second message")
        return 1
    
    # CRITICAL TEST: Verify the fix is working
    print("\n" + "=" * 60)
    print("🎯 CRITICAL RATING MODAL DOUBLE SHOW FIX VERIFICATION")
    print("=" * 60)
    
    # Check if timer restarted properly (rated should be False, timerExpired should be False)
    timer_restarted_correctly = (
        john_conversation_after_second_msg.get('rated') == False and
        john_conversation_after_second_msg.get('timerExpired') == False and
        john_conversation_after_second_msg.get('timerStarted') is not None
    )
    
    if timer_restarted_correctly:
        print("✅ RATING MODAL DOUBLE SHOW FIX WORKING!")
        print("   - Timer restarted correctly after second message")
        print("   - Conversation reset to unrated state")
        print("   - Timer not expired")
        tester.tests_passed += 1
    else:
        print("❌ RATING MODAL DOUBLE SHOW FIX NOT WORKING!")
        print("   - Timer may not have restarted correctly")
        print("   - Conversation state may be incorrect")
    tester.tests_run += 1
    
    # Test 9: Verify messages are present
    print("\n📋 Test 9: Verify both messages are present in conversation")
    messages = john_conversation_after_second_msg.get('messages', [])
    message_texts = [msg.get('text', '') for msg in messages]
    
    expected_messages = [
        "Hello John! Testing rating modal fix - message 1",
        "Testing second message after rating - should restart timer"
    ]
    
    messages_found = 0
    for expected_msg in expected_messages:
        if any(expected_msg in msg_text for msg_text in message_texts):
            messages_found += 1
            print(f"   ✅ Found message: '{expected_msg}'")
        else:
            print(f"   ❌ Missing message: '{expected_msg}'")
    
    if messages_found == len(expected_messages):
        print("✅ All test messages found in conversation")
        tester.tests_passed += 1
    else:
        print(f"❌ Only {messages_found}/{len(expected_messages)} test messages found")
    tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Rating Modal Double Show Fix tests passed!")
        return 0
    else:
        print("⚠️  Some Rating Modal Double Show Fix tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())