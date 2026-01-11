import requests
import sys
import time
from datetime import datetime

class YellowModeFrontendTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
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
                    error_response = response.json()
                    print(f"Response: {error_response}")
                    return False, error_response
                except:
                    print(f"Response text: {response.text}")
                    return False, {"detail": response.text}

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

    def set_yellow_mode(self, user_name, duration_minutes):
        """Set user to yellow mode with specified duration"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        # Set start time to now (as integer)
        start_time = int(datetime.now().timestamp() * 1000)
        
        success, response = self.run_test(
            f"Set {user_name} to Yellow Mode (Duration: {duration_minutes} min)",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "yellow",
                "availability": {
                    "laterMinutes": duration_minutes,
                    "laterStartTime": start_time
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
        return success, response

    def get_users_list(self):
        """Get all users to check their status"""
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "users",
            200
        )
        return success, response

def main():
    print("🧪 Yellow Mode Frontend Expiration Test")
    print("=" * 50)
    
    tester = YellowModeFrontendTester()
    
    # Test users
    timestamp = int(time.time())
    yellow_user = f"yellow_frontend_{timestamp}"
    test_user = f"test_frontend_{timestamp}"
    
    # Step 1: Create Yellow User and Test User
    print("\n📝 Step 1: Create test users...")
    
    if not tester.create_user(f"{yellow_user}@test.com", "password123", "Yellow Frontend User", yellow_user):
        print("❌ Failed to create Yellow User, stopping tests")
        return 1
    
    if not tester.create_user(f"{test_user}@test.com", "password123", "Test Frontend User", test_user):
        print("❌ Failed to create Test User, stopping tests")
        return 1
    
    print("✅ Both users created successfully")
    
    # Step 2: Set Yellow User to Yellow Mode (1 minute duration)
    print("\n📝 Step 2: Set Yellow User to Yellow Mode (1 minute)...")
    
    success, yellow_data = tester.set_yellow_mode(yellow_user, 1)
    if not success:
        print("❌ Failed to set yellow mode, stopping tests")
        return 1
    
    mode = yellow_data.get('availabilityMode')
    duration = yellow_data.get('availability', {}).get('laterMinutes')
    start_time = yellow_data.get('availability', {}).get('laterStartTime')
    
    print(f"✅ Yellow User set to mode: {mode}, duration: {duration} min")
    print(f"   Start time: {start_time} ({datetime.fromtimestamp(start_time/1000)})")
    
    # Step 3: Check initial status (should be available)
    print("\n📝 Step 3: Check initial status (should be available)...")
    
    success, users_data = tester.get_users_list()
    if success:
        yellow_user_data = next((u for u in users_data if u['name'] == 'Yellow Frontend User'), None)
        if yellow_user_data:
            print(f"✅ Found Yellow User: {yellow_user_data['name']}")
            print(f"   Mode: {yellow_user_data.get('availabilityMode')}")
            print(f"   Duration: {yellow_user_data.get('availability', {}).get('laterMinutes')} min")
        else:
            print("❌ Could not find Yellow User in users list")
            return 1
    else:
        print("❌ Failed to get users list")
        return 1
    
    # Step 4: Wait for expiration (70 seconds to be safe)
    print("\n📝 Step 4: Wait 70 seconds for Yellow Mode to expire...")
    
    for i in range(7):  # 7 * 10 = 70 seconds
        time.sleep(10)
        remaining = 70 - (i + 1) * 10
        print(f"   ⏳ {remaining} seconds remaining...")
    
    print("✅ Wait complete - Yellow mode should now be expired")
    
    # Step 5: Check status after expiration
    print("\n📝 Step 5: Check status after expiration...")
    
    success, users_data = tester.get_users_list()
    if success:
        yellow_user_data = next((u for u in users_data if u['name'] == 'Yellow Frontend User'), None)
        if yellow_user_data:
            print(f"✅ Found Yellow User after expiration:")
            print(f"   Mode: {yellow_user_data.get('availabilityMode')}")
            print(f"   Start Time: {yellow_user_data.get('availability', {}).get('laterStartTime')}")
            print(f"   Duration: {yellow_user_data.get('availability', {}).get('laterMinutes')} min")
            
            # Calculate if it should be expired
            start_time = yellow_user_data.get('availability', {}).get('laterStartTime')
            duration = yellow_user_data.get('availability', {}).get('laterMinutes')
            
            if start_time and duration:
                now_ms = datetime.now().timestamp() * 1000
                end_time = start_time + (duration * 60 * 1000)
                is_expired = now_ms > end_time
                
                print(f"   Current time: {now_ms}")
                print(f"   End time: {end_time}")
                print(f"   Should be expired: {is_expired}")
                
                if is_expired:
                    print("✅ Yellow Mode should be expired based on timestamps")
                else:
                    print("❌ Yellow Mode should not be expired yet - timing issue")
            
            # Store user data for frontend test
            tester.expired_yellow_user = yellow_user_data
            
        else:
            print("❌ Could not find Yellow User in users list after expiration")
            return 1
    else:
        print("❌ Failed to get users list after expiration")
        return 1
    
    # Step 6: Provide credentials for frontend testing
    print("\n📝 Step 6: Frontend test credentials...")
    print(f"✅ Test User Email: {test_user}@test.com")
    print(f"✅ Test User Password: password123")
    print(f"✅ Yellow User Name: Yellow Frontend User")
    print(f"✅ Yellow User ID: {tester.users[yellow_user]['id']}")
    
    # Final Results
    print(f"\n📊 Backend Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 Backend setup for frontend test COMPLETED!")
        print("\n✅ Summary:")
        print("   - Yellow user created and set to 1-minute duration")
        print("   - Waited for expiration")
        print("   - Yellow user should now show 'Expired' status in frontend")
        print("   - Test user credentials provided for frontend login")
        return 0
    else:
        print("❌ Some backend tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())