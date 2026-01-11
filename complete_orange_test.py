import requests
import sys
import json
from datetime import datetime
import time

class CompleteOrangeModeTest:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 {name}")
        
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
                print(f"✅ Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False, {}

    def create_and_login_user(self, email, password, name, user_label):
        """Create a new user and login"""
        print(f"\n👤 Creating and logging in {user_label}")
        
        signup_data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        url = f"{self.base_url}/auth/signup"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=signup_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_label] = data['access_token']
                self.users[user_label] = data['user']
                print(f"✅ {user_label} created and logged in")
                print(f"   ID: {data['user']['id']}")
                print(f"   Email: {data['user']['email']}")
                return True
            else:
                print(f"❌ Signup failed: {response.status_code}")
                try:
                    print(f"   Error: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            return False

def main():
    print("🧪 COMPLETE Orange Mode End-to-End Test")
    print("=" * 50)
    
    tester = CompleteOrangeModeTest()
    
    # Create unique test users with timestamp
    timestamp = int(time.time())
    user_a_email = f"orange_test_a_{timestamp}@test.com"
    user_b_email = f"orange_test_b_{timestamp}@test.com"
    user_c_email = f"orange_test_c_{timestamp}@test.com"
    
    print(f"📋 Test Scenario:")
    print(f"   1. Create User A and set to Orange Mode (max contacts = 1)")
    print(f"   2. Create User B and start chat with User A (should succeed)")
    print(f"   3. Create User C and try to chat with User A (should fail - 403)")
    print(f"   4. User B rates conversation with User A (frees up slot)")
    print(f"   5. User C tries to chat with User A again (should succeed)")
    print()
    
    # Step 1: Create User A
    if not tester.create_and_login_user(user_a_email, "password123", "Orange Test User A", "user_a"):
        print("❌ Failed to create User A")
        return 1
    
    # Step 2: Set User A to Orange Mode with max contacts = 1
    user_a_id = tester.users["user_a"]["id"]
    update_data = {
        "availabilityMode": "orange",
        "availability": {
            "maxContact": 1,
            "currentContacts": 0
        }
    }
    
    success, updated_user = tester.run_test(
        "Set User A to Orange Mode (max contacts = 1)",
        "PUT",
        f"users/{user_a_id}",
        200,
        data=update_data,
        token=tester.tokens["user_a"]
    )
    
    if not success:
        print("❌ Failed to set User A to Orange Mode")
        return 1
    
    # Update user data
    tester.users["user_a"] = updated_user
    print(f"   ✅ User A mode: {updated_user.get('availabilityMode')}")
    print(f"   ✅ Max contacts: {updated_user.get('availability', {}).get('maxContact')}")
    
    # Step 3: Create User B
    if not tester.create_and_login_user(user_b_email, "password123", "Orange Test User B", "user_b"):
        print("❌ Failed to create User B")
        return 1
    
    # Step 4: User B starts chat with User A (should succeed)
    chat_data = {"userId": user_a_id}
    
    success, chat_response = tester.run_test(
        "User B starts chat with User A (should succeed)",
        "POST",
        "conversations/start",
        200,
        data=chat_data,
        token=tester.tokens["user_b"]
    )
    
    if not success:
        print("❌ User B should be able to start chat with User A")
        return 1
    
    print(f"   ✅ Chat created: {chat_response.get('status')}")
    
    # Step 5: Verify User A's current contacts increased
    success, user_a_status = tester.run_test(
        "Check User A status after User B's chat",
        "GET",
        f"users/{user_a_id}",
        200,
        token=tester.tokens["user_a"]
    )
    
    if success:
        current_contacts = user_a_status.get('availability', {}).get('currentContacts', 0)
        print(f"   ✅ User A current contacts: {current_contacts}")
        if current_contacts != 1:
            print(f"   ⚠️ Expected 1 contact, got {current_contacts}")
    
    # Step 6: Create User C
    if not tester.create_and_login_user(user_c_email, "password123", "Orange Test User C", "user_c"):
        print("❌ Failed to create User C")
        return 1
    
    # Step 7: User C tries to start chat with User A (should fail - 403)
    success, error_response = tester.run_test(
        "User C tries to chat with User A (should fail - 403 Forbidden)",
        "POST",
        "conversations/start",
        403,
        data=chat_data,
        token=tester.tokens["user_c"]
    )
    
    if not success:
        print("❌ User C should be blocked with 403 Forbidden")
        return 1
    
    print(f"   ✅ Correctly blocked: {error_response.get('detail', 'Max contacts reached')}")
    
    # Step 8: User B rates conversation with User A (to free up slot)
    rating_data = {
        "isGood": True,
        "reason": "Good conversation"
    }
    
    success, rating_response = tester.run_test(
        "User B rates conversation with User A (frees up slot)",
        "POST",
        f"conversations/{user_a_id}/rate",
        200,
        data=rating_data,
        token=tester.tokens["user_b"]
    )
    
    if not success:
        print("❌ Failed to rate conversation")
        return 1
    
    print(f"   ✅ Conversation rated: {rating_response.get('status')}")
    
    # Step 9: Verify User A's current contacts decreased
    success, user_a_status = tester.run_test(
        "Check User A status after rating",
        "GET",
        f"users/{user_a_id}",
        200,
        token=tester.tokens["user_a"]
    )
    
    if success:
        current_contacts = user_a_status.get('availability', {}).get('currentContacts', 0)
        print(f"   ✅ User A current contacts after rating: {current_contacts}")
        if current_contacts != 0:
            print(f"   ⚠️ Expected 0 contacts, got {current_contacts}")
    
    # Step 10: User C tries to start chat with User A again (should succeed now)
    success, chat_response = tester.run_test(
        "User C tries to chat with User A again (should succeed)",
        "POST",
        "conversations/start",
        200,
        data=chat_data,
        token=tester.tokens["user_c"]
    )
    
    if not success:
        print("❌ User C should now be able to start chat with User A")
        return 1
    
    print(f"   ✅ Chat created: {chat_response.get('status')}")
    
    # Step 11: Final verification
    success, final_status = tester.run_test(
        "Final verification of User A status",
        "GET",
        f"users/{user_a_id}",
        200,
        token=tester.tokens["user_a"]
    )
    
    if success:
        mode = final_status.get('availabilityMode')
        max_contacts = final_status.get('availability', {}).get('maxContact', 0)
        current_contacts = final_status.get('availability', {}).get('currentContacts', 0)
        
        print(f"\n📊 FINAL STATUS:")
        print(f"   User A Mode: {mode}")
        print(f"   Max Contacts: {max_contacts}")
        print(f"   Current Contacts: {current_contacts}")
        print(f"   Expected: orange mode, max=1, current=1")
        
        if mode == "orange" and max_contacts == 1 and current_contacts == 1:
            print("   ✅ All values correct!")
        else:
            print("   ⚠️ Some values unexpected")
    
    # Results Summary
    print(f"\n📈 TEST RESULTS: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL ORANGE MODE TESTS PASSED!")
        print("✅ Orange Mode contact limiting is working correctly")
        print("✅ 403 Forbidden response when max contacts reached")
        print("✅ Contact slots freed up when conversations are rated")
        print("✅ New chats allowed after slots become available")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"\n❌ {failed_tests} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())