import requests
import sys
import time
from datetime import datetime, timedelta

class BrownModeExplicitFeedbackTester:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        req_headers = {'Content-Type': 'application/json'}
        if token:
            req_headers['Authorization'] = f'Bearer {token}'
        if headers:
            req_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=req_headers)

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
                try:
                    error_data = response.json()
                    print(f"Response: {error_data}")
                    return False, error_data
                except:
                    print(f"Response text: {response.text}")
                    return False, response.text

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
        if success and isinstance(response, dict) and 'access_token' in response:
            self.tokens[user_key] = response['access_token']
            self.users[user_key] = response['user']
            return True
        return False

    def set_brown_mode_deadline_passed(self, user_name, timezone_offset=0):
        """Set user to brown mode with deadline 1 hour AGO"""
        user_id = self.users[user_name]['id']
        token = self.tokens[user_name]
        
        # Calculate current time in user's timezone
        now_utc = datetime.utcnow()
        user_local_time = now_utc - timedelta(minutes=timezone_offset)
        
        # Set deadline 1 hour ago
        deadline_time = user_local_time - timedelta(hours=1)
        
        print(f"📅 Current UTC Time: {now_utc.strftime('%H:%M:%S')}")
        print(f"📅 User Local Time (Offset {timezone_offset}): {user_local_time.strftime('%H:%M:%S')}")
        print(f"📅 Setting Deadline: {deadline_time.strftime('%H:%M:%S')} (1 hour AGO)")
        
        success, response = self.run_test(
            f"Set {user_name} to Brown Mode (Deadline 1 hour AGO)",
            "PUT",
            f"users/{user_id}",
            200,
            data={
                "availabilityMode": "brown",
                "availability": {
                    "timedHour": deadline_time.hour,
                    "timedMinute": deadline_time.minute,
                    "timezoneOffset": timezone_offset
                }
            },
            token=token
        )
        if success:
            self.users[user_name] = response
        return success, response, deadline_time, user_local_time

    def attempt_message_with_explicit_feedback_check(self, sender_name, target_name, timezone_offset=0):
        """Attempt to message and verify explicit feedback"""
        target_id = self.users[target_name]['id']
        sender_token = self.tokens[sender_name]
        
        headers = {'x-timezone-offset': str(timezone_offset)}
        
        success, response = self.run_test(
            f"Attempt Message: {sender_name} -> {target_name} (Expect 403 with explicit feedback)",
            "POST",
            f"conversations/{target_id}/messages",
            403,
            data={"text": "Test message to brown user"},
            token=sender_token,
            headers=headers
        )
        
        return success, response

    def verify_error_message_format(self, error_response, expected_local_time):
        """Verify error message contains correct format and local time"""
        print(f"\n🔍 Verifying Error Message Format...")
        
        if isinstance(error_response, dict) and 'detail' in error_response:
            error_message = error_response['detail']
        elif isinstance(error_response, str):
            error_message = error_response
        else:
            print(f"❌ Unexpected error response format: {error_response}")
            return False
            
        print(f"📝 Error Message: {error_message}")
        
        # Check if message contains "Current User Time:"
        if "Current User Time:" not in error_message:
            print(f"❌ Error message missing 'Current User Time:' - Got: {error_message}")
            return False
            
        # Extract the time from error message
        try:
            time_part = error_message.split("Current User Time: ")[1]
            print(f"📝 Extracted Time from Error: {time_part}")
            
            # Verify the time matches expected local time (within 1 minute tolerance)
            expected_time_str = f"{expected_local_time.hour}:{expected_local_time.minute:02d}"
            if expected_time_str in time_part:
                print(f"✅ Time verification PASSED: Found expected time {expected_time_str}")
                return True
            else:
                print(f"❌ Time verification FAILED: Expected {expected_time_str}, got {time_part}")
                return False
                
        except Exception as e:
            print(f"❌ Error parsing time from message: {e}")
            return False

def main():
    print("🧪 Brown Mode Blocking with Explicit Feedback Test")
    print("=" * 60)
    print("Requirements:")
    print("1. Create Brown User (Deadline 1 hour AGO)")
    print("2. Attempt to message")
    print("3. Verify 403")
    print("4. Verify Error Message contains 'Current User Time: [Correct Local Time]'")
    print("=" * 60)
    
    tester = BrownModeExplicitFeedbackTester()
    
    # Test users
    timestamp = int(time.time())
    brown_user = f"brown_user_{timestamp}"
    sender_user = f"sender_{timestamp}"
    
    # Step 1: Create test users
    print("\n📝 Step 1: Creating test users...")
    
    if not tester.create_user(f"{brown_user}@test.com", "password123", "Brown User", brown_user):
        print("❌ Failed to create Brown User")
        return 1
        
    if not tester.create_user(f"{sender_user}@test.com", "password123", "Sender User", sender_user):
        print("❌ Failed to create Sender User")
        return 1
    
    # Step 2: Set Brown User to Brown Mode with deadline 1 hour AGO
    print("\n📝 Step 2: Setting Brown User to Brown Mode (Deadline 1 hour AGO)...")
    
    # Test with UTC timezone (offset 0)
    success, brown_data, deadline_time, user_local_time = tester.set_brown_mode_deadline_passed(brown_user, 0)
    if not success:
        print("❌ Failed to set Brown Mode")
        return 1
    
    # Step 3: Attempt to message and verify 403
    print("\n📝 Step 3: Attempting to message Brown User...")
    
    success, error_response = tester.attempt_message_with_explicit_feedback_check(sender_user, brown_user, 0)
    if not success:
        print("❌ Failed to get expected 403 response")
        return 1
    
    # Step 4: Verify Error Message contains "Current User Time: [Correct Local Time]"
    print("\n📝 Step 4: Verifying Error Message Format...")
    
    if not tester.verify_error_message_format(error_response, user_local_time):
        print("❌ Error message format verification failed")
        return 1
    
    # Additional test with different timezone
    print("\n" + "=" * 60)
    print("🧪 Additional Test: Different Timezone (UTC-5, Offset +300)")
    print("=" * 60)
    
    # Create new users for timezone test
    brown_user_tz = f"brown_user_tz_{timestamp}"
    sender_user_tz = f"sender_tz_{timestamp}"
    
    if not tester.create_user(f"{brown_user_tz}@test.com", "password123", "Brown User TZ", brown_user_tz):
        print("❌ Failed to create Brown User TZ")
        return 1
        
    if not tester.create_user(f"{sender_user_tz}@test.com", "password123", "Sender User TZ", sender_user_tz):
        print("❌ Failed to create Sender User TZ")
        return 1
    
    # Set Brown Mode with UTC-5 timezone (offset +300)
    success, brown_data_tz, deadline_time_tz, user_local_time_tz = tester.set_brown_mode_deadline_passed(brown_user_tz, 300)
    if not success:
        print("❌ Failed to set Brown Mode for timezone test")
        return 1
    
    # Attempt message with timezone header
    success, error_response_tz = tester.attempt_message_with_explicit_feedback_check(sender_user_tz, brown_user_tz, 300)
    if not success:
        print("❌ Failed to get expected 403 response for timezone test")
        return 1
    
    # Verify error message for timezone test
    if not tester.verify_error_message_format(error_response_tz, user_local_time_tz):
        print("❌ Error message format verification failed for timezone test")
        return 1
    
    # Final Results
    print(f"\n📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All Brown Mode Explicit Feedback tests PASSED!")
        print("\n✅ VERIFICATION SUMMARY:")
        print("   ✓ Brown User created with deadline 1 hour AGO")
        print("   ✓ Message attempt correctly blocked with 403 status")
        print("   ✓ Error message contains 'Current User Time: [Correct Local Time]'")
        print("   ✓ Timezone handling verified (UTC and UTC-5)")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())