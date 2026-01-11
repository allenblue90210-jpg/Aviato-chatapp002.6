import requests
import sys
import time

class UITestUserCreator:
    def __init__(self, base_url="https://chat-messenger-306.preview.emergentagent.com"):
        self.base_url = base_url

    def create_test_user(self):
        """Create a test user without profile picture for UI testing"""
        timestamp = int(time.time())
        email = f"uitest_{timestamp}@test.com"
        password = "password123"
        name = f"UI Test User"
        
        url = f"{self.base_url}/api/auth/signup"
        data = {"email": email, "password": password, "name": name}
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                user = result['user']
                print(f"✅ Created UI test user:")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"   Name: {name}")
                print(f"   ID: {user.get('id')}")
                print(f"   Profile Pic: {user.get('profilePic', 'None')}")
                return email, password, user
            else:
                print(f"❌ Failed to create user: {response.status_code}")
                return None, None, None
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return None, None, None

def main():
    creator = UITestUserCreator()
    email, password, user = creator.create_test_user()
    
    if email and password:
        print(f"\n🎯 Use these credentials for UI testing:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())