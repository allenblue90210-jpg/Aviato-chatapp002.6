import requests
import sys
import json
from datetime import datetime

class FocusedOrangeModeTest:
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

    def login_user(self, email, password, user_label):
        """Login user using form data"""
        print(f"\n🔐 Logging in {user_label}")
        
        form_data = {
            'username': email,
            'password': password
        }
        
        url = f"{self.base_url}/auth/login"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(url, data=form_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_label] = data['access_token']
                self.users[user_label] = data['user']
                print(f"✅ {user_label} logged in - ID: {data['user']['id']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def create_user(self, email, password, name, user_label):
        """Create a new user"""
        print(f"\n👤 Creating {user_label}")
        
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
                print(f"✅ {user_label} created - ID: {data['user']['id']}")
                return True
            else:
                print(f"❌ Signup failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            return False

def main():
    print("🧪 FOCUSED Orange Mode Test")
    print("=" * 40)
    
    tester = FocusedOrangeModeTest()
    
    # Use demo user as User A (already exists)
    demo_email = "demo@aviato.com"
    demo_password = "password"
    
    # Create unique test users
    timestamp = datetime.now().strftime('%H%M%S')
    user_b_email = f"testb_{timestamp}@test.com"
    user_c_email = f"testc_{timestamp}@test.com"
    
    print(f"📋 Test Plan:")
    print(f"   User A (Demo): {demo_email}")
    print(f"   User B: {user_b_email}")
    print(f"   User C: {user_c_email}")
    
    # Step 1: Login as Demo User (User A)
    if not tester.login_user(demo_email, demo_password, "user_a"):
        print("❌ Failed to login as demo user")
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
    
    success, _ = tester.run_test(
        "Set User A to Orange Mode (max=1)",
        "PUT",
        f"users/{user_a_id}",
        200,
        data=update_data,
        token=tester.tokens["user_a"]
    )
    
    if not success:
        print("❌ Failed to set Orange Mode")
        return 1
    
    # Step 3: Create User B
    if not tester.create_user(user_b_email, "password123", "Test User B", "user_b"):
        print("❌ Failed to create User B")
        return 1
    
    # Step 4: User B starts chat with User A (should succeed)
    user_a_id = tester.users["user_a"]["id"]
    chat_data = {"userId": user_a_id}
    
    success, _ = tester.run_test(
        "User B starts chat with User A (should succeed)",
        "POST",
        "conversations/start",
        200,
        data=chat_data,
        token=tester.tokens["user_b"]
    )
    
    if not success:
        print("❌ User B should be able to chat with User A")
        return 1
    
    # Step 5: Create User C
    if not tester.create_user(user_c_email, "password123", "Test User C", "user_c"):
        print("❌ Failed to create User C")
        return 1
    
    # Step 6: User C tries to start chat with User A (should fail - 403)
    success, _ = tester.run_test(
        "User C tries to chat with User A (should fail - 403)",
        "POST",
        "conversations/start",
        403,
        data=chat_data,
        token=tester.tokens["user_c"]
    )
    
    if not success:
        print("❌ User C should be blocked (403 Forbidden)")
        return 1
    
    # Step 7: User B rates conversation with User A (to free up slot)
    user_a_id = tester.users["user_a"]["id"]
    rating_data = {
        "isGood": True,
        "reason": "Good conversation"
    }
    
    success, _ = tester.run_test(
        "User B rates conversation with User A",
        "POST",
        f"conversations/{user_a_id}/rate",
        200,
        data=rating_data,
        token=tester.tokens["user_b"]
    )
    
    if not success:
        print("❌ Failed to rate conversation")
        return 1
    
    # Step 8: User C tries to start chat with User A again (should succeed now)
    success, _ = tester.run_test(
        "User C tries to chat with User A again (should succeed)",
        "POST",
        "conversations/start",
        200,
        data=chat_data,
        token=tester.tokens["user_c"]
    )
    
    if not success:
        print("❌ User C should now be able to chat with User A")
        return 1
    
    # Final verification - check User A's current contacts
    success, user_a_info = tester.run_test(
        "Get User A final status",
        "GET",
        f"users/{user_a_id}",
        200,
        token=tester.tokens["user_a"]
    )
    
    if success:
        mode = user_a_info.get('availabilityMode')
        max_contacts = user_a_info.get('availability', {}).get('maxContact', 0)
        current_contacts = user_a_info.get('availability', {}).get('currentContacts', 0)
        print(f"\n📊 Final Status:")
        print(f"   Mode: {mode}")
        print(f"   Max Contacts: {max_contacts}")
        print(f"   Current Contacts: {current_contacts}")
    
    # Results
    print(f"\n📈 Test Results: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL ORANGE MODE TESTS PASSED!")
        print("✅ Orange Mode logic is working correctly")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())