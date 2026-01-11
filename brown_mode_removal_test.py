#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta

class BrownModeRemovalTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.brown_user_id = "576cd246-e439-45f1-bfe1-104ba9438930"  # Existing brown user
        self.demo_user_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        if headers is None:
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
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_create_demo_user(self):
        """Create a new demo user to test messaging"""
        print("\n=== Creating Demo User ===")
        
        timestamp = datetime.now().strftime('%H%M%S')
        demo_user_data = {
            "email": f"demo_user_{timestamp}@test.com",
            "password": "TestPass123!",
            "name": f"Demo User {timestamp}"
        }
        
        success, response = self.run_test(
            "Create Demo User",
            "POST",
            "auth/signup",
            200,
            data=demo_user_data
        )
        
        if success:
            self.demo_user_token = response.get('access_token')
            print(f"✅ Demo user created successfully")
            return True
        return False

    def test_messaging_to_brown_user(self):
        """Test that messaging to brown user succeeds (logic removed)"""
        print("\n=== Testing Messaging to Brown User ===")
        
        if not self.demo_user_token or not self.brown_user_id:
            print("❌ Missing demo token or brown user ID")
            return False
            
        # Switch to demo user token
        original_token = self.token
        self.token = self.demo_user_token
        
        # Try to start chat with brown user
        success, response = self.run_test(
            "Start Chat with Brown User",
            "POST",
            "conversations/start",
            200,
            data={"userId": self.brown_user_id}
        )
        
        if not success:
            self.token = original_token
            return False
            
        # Try to send message to brown user
        success, response = self.run_test(
            "Send Message to Brown User",
            "POST",
            f"conversations/{self.brown_user_id}/messages",
            200,
            data={"text": "Test message to brown user - should succeed because brown mode logic is removed!"}
        )
        
        self.token = original_token
        return success

    def test_get_users_list(self):
        """Test that brown user appears in users list"""
        print("\n=== Testing Users List ===")
        
        success, response = self.run_test(
            "Get Users List",
            "GET",
            "users",
            200
        )
        
        if success and isinstance(response, list):
            brown_user = next((u for u in response if u.get('id') == self.brown_user_id), None)
            if brown_user:
                mode = brown_user.get('availabilityMode')
                print(f"✅ Brown user found in list with mode: {mode}")
                return True
            else:
                print("❌ Brown user not found in users list")
                return False
        
        return success

    def test_brown_user_details(self):
        """Test getting brown user details"""
        print("\n=== Testing Brown User Details ===")
        
        success, response = self.run_test(
            "Get Brown User Details",
            "GET",
            f"users/{self.brown_user_id}",
            200
        )
        
        if success:
            mode = response.get('availabilityMode')
            availability = response.get('availability', {})
            timed_hour = availability.get('timedHour')
            timed_minute = availability.get('timedMinute')
            
            print(f"✅ Brown user details - Mode: {mode}, TimedHour: {timed_hour}, TimedMinute: {timed_minute}")
            
            # Check if the deadline has passed (should be 1 hour ago based on the data)
            if timed_hour is not None and timed_minute is not None:
                current_time = datetime.now()
                deadline_time = current_time.replace(hour=timed_hour, minute=timed_minute, second=0, microsecond=0)
                
                if current_time > deadline_time:
                    print(f"✅ Brown mode deadline has passed - Current: {current_time.strftime('%H:%M')}, Deadline: {deadline_time.strftime('%H:%M')}")
                else:
                    print(f"⚠️  Brown mode deadline has NOT passed - Current: {current_time.strftime('%H:%M')}, Deadline: {deadline_time.strftime('%H:%M')}")
            
            return True
        
        return success

def main():
    print("🧪 Brown Mode Removal Testing")
    print("=" * 50)
    
    tester = BrownModeRemovalTester()
    
    # Test 1: Create demo user for testing
    if not tester.test_create_demo_user():
        print("❌ Demo user creation failed, stopping tests")
        return 1
    
    # Test 2: Get brown user details
    if not tester.test_brown_user_details():
        print("❌ Brown user details failed")
        return 1
    
    # Test 3: Test messaging to brown user (should succeed)
    if not tester.test_messaging_to_brown_user():
        print("❌ Messaging to brown user failed")
        return 1
    
    # Test 4: Verify brown user appears in users list
    if not tester.test_get_users_list():
        print("❌ Brown user not found in users list")
        return 1
    
    # Print results
    print(f"\n📊 Backend Tests Results: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ All backend tests passed! Brown mode removal working correctly.")
        print("✅ Key findings:")
        print("   - Brown user exists and is accessible")
        print("   - Messaging to brown user SUCCEEDS (blocking logic removed)")
        print("   - Brown user appears in users list")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())