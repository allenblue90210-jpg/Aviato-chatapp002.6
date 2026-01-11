import requests
import sys
import time
from datetime import datetime

class YellowTimerTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
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

    def create_user(self, email, password, name, user_key):
        """Create a new user and get token"""
        success, response = self.run_test(
            f"Create User {name}",
            "POST",
            "auth/signup",
            200,
            data={"email": email, "password": password, "name": name}
        )
        if success and 'access_token' in response:
            self.tokens[user_key] = response['access_token']
            self.users[user_key] = response['user']
            return True
        return False

    def set_yellow_mode(self, user_name, minutes):
        """Set user to yellow mode with specified minutes"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        # Set laterStartTime to current timestamp
        current_time_ms = int(datetime.now().timestamp() * 1000)
        
        success, response = self.run_test(
            f"Set {user_name} to Yellow Mode ({minutes} min)",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "yellow",
                "availability": {
                    "laterMinutes": minutes,
                    "laterStartTime": current_time_ms,
                    "maxContact": 10,
                    "currentContacts": 0
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
            print(f"   Yellow mode set with {minutes} minutes starting at {current_time_ms}")
            
            # Calculate remaining time
            now_ms = datetime.now().timestamp() * 1000
            end_time = current_time_ms + (minutes * 60 * 1000)
            remaining_ms = max(0, end_time - now_ms)
            remaining_mins = remaining_ms / (60 * 1000)
            print(f"   Remaining time: {remaining_mins:.1f} minutes")
            
        return success, response

    def get_user_info(self, user_name):
        """Get current user info"""
        user_id = self.users[user_name]['id']
        
        success, response = self.run_test(
            f"Get {user_name} Info",
            "GET",
            f"users/{user_id}",
            200
        )
        if success:
            self.users[user_name] = response
        return success, response

    def get_all_users(self):
        """Get all users to check yellow user in list"""
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "users",
            200
        )
        return success, response

def main():
    print("🧪 Yellow Timer Alignment Test")
    print("=" * 50)
    
    tester = YellowTimerTester()
    
    # Test user
    timestamp = int(time.time())
    yellow_user = f"yellow_user_{timestamp}"
    
    # Step 1: Create Yellow User
    print("\n📝 Step 1: Creating Yellow User...")
    if not tester.create_user(f"{yellow_user}@test.com", "password123", "Yellow User", yellow_user):
        print("❌ Failed to create Yellow User, stopping tests")
        return 1
    
    # Step 2: Set to Yellow Mode with 120 minutes
    print("\n📝 Step 2: Set to Yellow Mode (120 minutes)...")
    success, yellow_data = tester.set_yellow_mode(yellow_user, 120)
    if not success:
        print("❌ Failed to set yellow mode, stopping tests")
        return 1
    
    # Verify yellow mode settings
    availability = yellow_data.get('availability', {})
    later_minutes = availability.get('laterMinutes', 0)
    later_start_time = availability.get('laterStartTime', 0)
    
    print(f"✅ Yellow User created with:")
    print(f"   - laterMinutes: {later_minutes}")
    print(f"   - laterStartTime: {later_start_time}")
    print(f"   - availabilityMode: {yellow_data.get('availabilityMode')}")
    
    # Step 3: Verify user appears in users list with correct timer
    print("\n📝 Step 3: Verify user in users list...")
    success, users_data = tester.get_all_users()
    if success:
        yellow_user_in_list = None
        for user in users_data:
            if user.get('id') == yellow_data.get('id'):
                yellow_user_in_list = user
                break
        
        if yellow_user_in_list:
            print(f"✅ Yellow user found in users list")
            avail = yellow_user_in_list.get('availability', {})
            print(f"   - laterMinutes: {avail.get('laterMinutes')}")
            print(f"   - laterStartTime: {avail.get('laterStartTime')}")
            print(f"   - availabilityMode: {yellow_user_in_list.get('availabilityMode')}")
            
            # Calculate expected timer display
            if avail.get('laterStartTime') and avail.get('laterMinutes'):
                now_ms = datetime.now().timestamp() * 1000
                end_time = avail.get('laterStartTime') + (avail.get('laterMinutes') * 60 * 1000)
                remaining_ms = max(0, end_time - now_ms)
                remaining_mins = remaining_ms / (60 * 1000)
                
                hours = int(remaining_mins // 60)
                mins = int(remaining_mins % 60)
                
                print(f"   - Calculated remaining time: {hours}h {mins}m")
                print(f"   - Expected display format: 'Active: {hours}h {mins}m'")
                
                # Check if it's close to expected (should be close to 1h 59m)
                if hours == 1 and mins >= 58:  # Allow some margin for test execution time
                    print(f"✅ Timer shows expected format: Active: {hours}h {mins}m")
                else:
                    print(f"⚠️  Timer shows: Active: {hours}h {mins}m (expected ~1h 59m)")
        else:
            print("❌ Yellow user not found in users list")
            return 1
    else:
        print("❌ Failed to get users list")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 Yellow Timer Backend tests PASSED!")
        print(f"\n📋 Summary for Frontend Testing:")
        print(f"   - Yellow User ID: {yellow_data.get('id')}")
        print(f"   - Expected Timer Format: 'Active: 1h 59m' (approximately)")
        print(f"   - Backend URL: {tester.base_url}")
        return 0
    else:
        print("❌ Some backend tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())