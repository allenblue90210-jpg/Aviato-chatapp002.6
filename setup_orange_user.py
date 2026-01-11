#!/usr/bin/env python3

import requests
import sys

def setup_orange_user():
    base_url = "https://chat-messenger-306.preview.emergentagent.com/api"
    
    # Login as existing user (Asuab)
    login_data = {"username": "asuab@test.com", "password": "password"}
    response = requests.post(f"{base_url}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print("Failed to login as Asuab")
        return False
        
    token = response.json()['access_token']
    user_id = response.json()['user']['id']
    
    # Set Asuab to orange mode with max 3 contacts
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    update_data = {
        "availabilityMode": "orange",
        "availability": {
            "maxContact": 3,
            "currentContacts": 0
        }
    }
    
    response = requests.put(f"{base_url}/users/{user_id}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Successfully set Asuab (ID: {user_id}) to Orange Mode (max=3)")
        return True
    else:
        print(f"❌ Failed to set orange mode: {response.status_code}")
        return False

if __name__ == "__main__":
    setup_orange_user()