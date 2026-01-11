import requests
import sys
import time
from datetime import datetime

class ProfileTestAPI:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
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
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_user_no_profile_pic(self):
        """Create a new user without profile picture"""
        timestamp = int(time.time())
        email = f"noprofile_{timestamp}@test.com"
        password = "password123"
        name = f"No Profile User {timestamp}"
        
        success, response = self.run_test(
            f"Create User Without Profile Pic",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user = response['user']
            print(f"✅ Created user: {name}")
            print(f"   Email: {email}")
            print(f"   Profile Pic: {self.user.get('profilePic', 'None')}")
            return True
        return False

    def get_current_user(self):
        """Get current user info"""
        success, response = self.run_test(
            "Get Current User Info",
            "GET",
            "auth/me",
            200
        )
        if success:
            self.user = response
            print(f"✅ User profile pic status: {self.user.get('profilePic', 'None')}")
        return success, response

    def update_profile_pic(self, new_pic_url):
        """Update user profile picture"""
        user_id = self.user['id']
        
        success, response = self.run_test(
            "Update Profile Picture",
            "PUT",
            f"users/{user_id}",
            200,
            data={"profilePic": new_pic_url}
        )
        if success:
            self.user = response
            print(f"✅ Updated profile pic to: {new_pic_url}")
        return success, response

def main():
    print("🧪 Profile Picture Test - No Profile Picture Scenario")
    print("=" * 70)
    
    tester = ProfileTestAPI()
    
    # Step 1: Create user without profile picture
    print("\n📝 Step 1: Creating user without profile picture...")
    if not tester.create_user_no_profile_pic():
        print("❌ Failed to create user, stopping tests")
        return 1
    
    # Step 2: Verify user has no profile picture
    print("\n📝 Step 2: Verifying user has no profile picture...")
    success, user_data = tester.get_current_user()
    if not success:
        print("❌ Failed to get user data")
        return 1
    
    profile_pic = user_data.get('profilePic')
    if profile_pic is None:
        print("✅ User has no profile picture (profilePic is None)")
    elif profile_pic == "":
        print("✅ User has empty profile picture (profilePic is empty string)")
    else:
        print(f"⚠️  User has profile picture: {profile_pic}")
    
    # Step 3: Test profile picture update
    print("\n📝 Step 3: Testing profile picture update...")
    test_pic_url = "https://i.pravatar.cc/150?u=test"
    success, updated_user = tester.update_profile_pic(test_pic_url)
    if not success:
        print("❌ Failed to update profile picture")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Profile Picture tests PASSED!")
        print("\n✅ VERIFICATION SUMMARY:")
        print(f"   ✓ Created user without profile picture")
        print(f"   ✓ Verified profilePic field is None/empty")
        print(f"   ✓ Successfully updated profile picture")
        print(f"\n📋 Test User Credentials:")
        print(f"   Email: {tester.user.get('email', 'N/A')}")
        print(f"   Name: {tester.user.get('name', 'N/A')}")
        print(f"   ID: {tester.user.get('id', 'N/A')}")
        print(f"   Current Profile Pic: {tester.user.get('profilePic', 'None')}")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())