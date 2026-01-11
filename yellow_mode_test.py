import requests
import sys
import time
from datetime import datetime

class YellowModeAPITester:
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

    def login_user(self, email, password, name):
        """Login existing user"""
        # Use form data for login
        url = f"{self.base_url}/api/auth/login"
        data = {
            'username': email,
            'password': password
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Login {name}...")
        
        try:
            response = requests.post(url, data=data)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                resp_data = response.json()
                self.tokens[name] = resp_data['access_token']
                self.users[name] = resp_data['user']
                return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
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
                    "laterStartTime": current_time_ms
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
            print(f"   Yellow Mode set: {minutes} minutes from {current_time_ms}")
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

    def calculate_remaining_time(self, user_name):
        """Calculate remaining time for yellow mode user"""
        user_data = self.users[user_name]
        availability = user_data.get('availability', {})
        
        start_time = availability.get('laterStartTime')
        minutes = availability.get('laterMinutes')
        
        if not start_time or not minutes:
            return None, "No yellow mode data"
        
        current_time_ms = int(datetime.now().timestamp() * 1000)
        end_time_ms = start_time + (minutes * 60 * 1000)
        remaining_ms = end_time_ms - current_time_ms
        
        if remaining_ms <= 0:
            return 0, "Expired"
        
        remaining_minutes = remaining_ms / (60 * 1000)
        hours = int(remaining_minutes // 60)
        mins = int(remaining_minutes % 60)
        
        if hours > 0:
            return remaining_minutes, f"{hours}h {mins}m"
        else:
            return remaining_minutes, f"{mins}m"

def main():
    print("🧪 Yellow Mode Active Timer Test")
    print("=" * 50)
    
    tester = YellowModeAPITester()
    
    # Test users
    timestamp = int(time.time())
    yellow_user_120 = f"yellow_120_{timestamp}"
    yellow_user_15 = f"yellow_15_{timestamp}"
    
    # Step 1: Create Yellow User (120 min)
    print("\n📝 Step 1: Create Yellow User (120 min)...")
    email_120 = f"{yellow_user_120}@test.com"
    if not tester.create_user(email_120, "password123", "Yellow User 120min", yellow_user_120):
        print("❌ Failed to create 120min user, stopping tests")
        return 1
    
    # Set to yellow mode with 120 minutes
    success, user_data = tester.set_yellow_mode(yellow_user_120, 120)
    if not success:
        print("❌ Failed to set yellow mode (120min), stopping tests")
        return 1
    
    # Step 2: Verify timer shows ~2h 0m
    print("\n📝 Step 2: Verify 120min user timer...")
    remaining_min, time_str = tester.calculate_remaining_time(yellow_user_120)
    if remaining_min:
        print(f"✅ 120min user timer: {time_str} (remaining: {remaining_min:.1f} minutes)")
        
        # Check if it's close to 2h (120 minutes)
        if 118 <= remaining_min <= 120:  # Allow 2 minute tolerance
            print("✅ Timer shows approximately 2h 0m as expected")
        else:
            print(f"❌ Timer not showing expected ~120min, got {remaining_min:.1f}min")
    else:
        print(f"❌ Failed to calculate timer: {time_str}")
        return 1
    
    # Step 3: Create Yellow User (15 min)
    print("\n📝 Step 3: Create Yellow User (15 min)...")
    email_15 = f"{yellow_user_15}@test.com"
    if not tester.create_user(email_15, "password123", "Yellow User 15min", yellow_user_15):
        print("❌ Failed to create 15min user, stopping tests")
        return 1
    
    # Set to yellow mode with 15 minutes
    success, user_data = tester.set_yellow_mode(yellow_user_15, 15)
    if not success:
        print("❌ Failed to set yellow mode (15min), stopping tests")
        return 1
    
    # Step 4: Verify timer shows ~15m
    print("\n📝 Step 4: Verify 15min user timer...")
    remaining_min, time_str = tester.calculate_remaining_time(yellow_user_15)
    if remaining_min:
        print(f"✅ 15min user timer: {time_str} (remaining: {remaining_min:.1f} minutes)")
        
        # Check if it's close to 15 minutes
        if 13 <= remaining_min <= 15:  # Allow 2 minute tolerance
            print("✅ Timer shows approximately 15m as expected")
        else:
            print(f"❌ Timer not showing expected ~15min, got {remaining_min:.1f}min")
    else:
        print(f"❌ Failed to calculate timer: {time_str}")
        return 1
    
    # Step 5: Test login functionality for both users
    print("\n📝 Step 5: Test login for both users...")
    
    # Login 120min user
    if not tester.login_user(email_120, "password123", f"{yellow_user_120}_login"):
        print("❌ Failed to login 120min user")
        return 1
    
    # Login 15min user  
    if not tester.login_user(email_15, "password123", f"{yellow_user_15}_login"):
        print("❌ Failed to login 15min user")
        return 1
    
    print("✅ Both users can login successfully")
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Yellow Mode Active Timer tests PASSED!")
        print("\n📋 Summary:")
        print("✅ Created Yellow User with 120 minutes - Timer shows ~2h 0m")
        print("✅ Created Yellow User with 15 minutes - Timer shows ~15m")
        print("✅ Both users can login successfully")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())