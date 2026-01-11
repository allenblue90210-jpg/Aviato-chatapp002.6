import requests
import sys
import time
from datetime import datetime

class ProfilePictureRemovalTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

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

    def create_test_user(self):
        """Create a test user for profile picture testing"""
        timestamp = int(time.time())
        email = f"profile_test_{timestamp}@test.com"
        password = "testpass123"
        name = f"Profile Test User {timestamp}"
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            return True
        return False

    def get_current_user(self):
        """Get current user data"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200,
            token=self.token
        )
        if success:
            self.user_data = response
        return success, response

    def update_profile_picture(self, profile_pic_url):
        """Update user profile picture"""
        user_id = self.user_data['id']
        
        success, response = self.run_test(
            f"Update Profile Picture to: {profile_pic_url or 'None (Remove)'}",
            "PUT",
            f"users/{user_id}",
            200,
            data={"profilePic": profile_pic_url},
            token=self.token
        )
        if success:
            self.user_data = response
        return success, response

    def verify_profile_picture(self, expected_value):
        """Verify profile picture value"""
        success, user_data = self.get_current_user()
        if not success:
            return False
            
        actual_value = user_data.get('profilePic')
        
        if expected_value is None:
            # Expecting null/None
            if actual_value is None:
                print(f"✅ Profile picture correctly set to None (removed)")
                return True
            else:
                print(f"❌ Expected profile picture to be None, but got: {actual_value}")
                return False
        else:
            # Expecting specific URL
            if actual_value == expected_value:
                print(f"✅ Profile picture correctly set to: {actual_value}")
                return True
            else:
                print(f"❌ Expected profile picture to be '{expected_value}', but got: {actual_value}")
                return False

def main():
    print("🧪 Profile Picture Removal Test")
    print("=" * 50)
    
    tester = ProfilePictureRemovalTester()
    
    # Step 1: Create test user
    print("\n📝 Step 1: Create test user...")
    if not tester.create_test_user():
        print("❌ Failed to create test user, stopping tests")
        return 1
    
    # Step 2: Check initial profile picture
    print("\n📝 Step 2: Check initial profile picture...")
    success, initial_user = tester.get_current_user()
    if not success:
        print("❌ Failed to get user data")
        return 1
    
    initial_pic = initial_user.get('profilePic')
    print(f"Initial profile picture: {initial_pic}")
    
    # Step 3: Set a profile picture first (if not already set)
    if not initial_pic:
        print("\n📝 Step 3: Setting a profile picture first...")
        test_pic_url = "https://i.pravatar.cc/150?u=test-user"
        success, _ = tester.update_profile_picture(test_pic_url)
        if not success:
            print("❌ Failed to set initial profile picture")
            return 1
        
        # Verify it was set
        if not tester.verify_profile_picture(test_pic_url):
            print("❌ Failed to verify initial profile picture was set")
            return 1
    else:
        print(f"✅ User already has profile picture: {initial_pic}")
    
    # Step 4: Remove profile picture (set to null)
    print("\n📝 Step 4: Removing profile picture...")
    success, _ = tester.update_profile_picture(None)
    if not success:
        print("❌ Failed to remove profile picture")
        return 1
    
    # Step 5: Verify profile picture was removed
    print("\n📝 Step 5: Verifying profile picture was removed...")
    if not tester.verify_profile_picture(None):
        print("❌ Profile picture was not properly removed")
        return 1
    
    # Step 6: Test setting it back
    print("\n📝 Step 6: Setting profile picture back...")
    new_pic_url = "https://i.pravatar.cc/150?u=restored-user"
    success, _ = tester.update_profile_picture(new_pic_url)
    if not success:
        print("❌ Failed to restore profile picture")
        return 1
    
    # Step 7: Verify it was restored
    print("\n📝 Step 7: Verifying profile picture was restored...")
    if not tester.verify_profile_picture(new_pic_url):
        print("❌ Profile picture was not properly restored")
        return 1
    
    # Step 8: Remove it again to test the full flow
    print("\n📝 Step 8: Final removal test...")
    success, _ = tester.update_profile_picture(None)
    if not success:
        print("❌ Failed final removal")
        return 1
    
    # Step 9: Final verification
    print("\n📝 Step 9: Final verification...")
    if not tester.verify_profile_picture(None):
        print("❌ Final verification failed")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Profile Picture Removal tests PASSED!")
        print("\n✅ VERIFICATION SUMMARY:")
        print("   ✓ Successfully created test user")
        print("   ✓ Successfully set profile picture")
        print("   ✓ Successfully removed profile picture (set to null)")
        print("   ✓ Successfully verified removal")
        print("   ✓ Successfully restored profile picture")
        print("   ✓ Successfully removed profile picture again")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())