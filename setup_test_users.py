#!/usr/bin/env python3

import requests
import sys
import time

def setup_test_users():
    base_url = "https://chat-messenger-306.preview.emergentagent.com/api"
    timestamp = int(time.time())
    
    # Create Orange User
    orange_email = f"orange_test_{timestamp}@test.com"
    signup_data = {
        "email": orange_email,
        "password": "password123",
        "name": "Orange Test User"
    }
    
    response = requests.post(f"{base_url}/auth/signup", json=signup_data)
    if response.status_code != 200:
        print(f"Failed to create orange user: {response.status_code}")
        return False
        
    orange_token = response.json()['access_token']
    orange_user_id = response.json()['user']['id']
    
    # Set to orange mode
    headers = {'Authorization': f'Bearer {orange_token}', 'Content-Type': 'application/json'}
    update_data = {
        "availabilityMode": "orange",
        "availability": {
            "maxContact": 3,
            "currentContacts": 0
        }
    }
    
    response = requests.put(f"{base_url}/users/{orange_user_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to set orange mode: {response.status_code}")
        return False
        
    print(f"✅ Orange User created: {orange_email} (ID: {orange_user_id})")
    
    # Create 4 test users
    test_users = []
    for i in range(1, 5):
        email = f"testuser{i}_{timestamp}@test.com"
        signup_data = {
            "email": email,
            "password": "password123",
            "name": f"Test User {i}"
        }
        
        response = requests.post(f"{base_url}/auth/signup", json=signup_data)
        if response.status_code != 200:
            print(f"Failed to create test user {i}: {response.status_code}")
            continue
            
        user_data = {
            "email": email,
            "password": "password123",
            "name": f"Test User {i}",
            "id": response.json()['user']['id'],
            "token": response.json()['access_token']
        }
        test_users.append(user_data)
        print(f"✅ Test User {i} created: {email} (ID: {user_data['id']})")
    
    # Save credentials to file for frontend testing
    with open('/app/test_credentials.txt', 'w') as f:
        f.write(f"ORANGE_USER_EMAIL={orange_email}\n")
        f.write(f"ORANGE_USER_ID={orange_user_id}\n")
        f.write(f"ORANGE_USER_PASSWORD=password123\n\n")
        
        for i, user in enumerate(test_users, 1):
            f.write(f"TEST_USER_{i}_EMAIL={user['email']}\n")
            f.write(f"TEST_USER_{i}_ID={user['id']}\n")
            f.write(f"TEST_USER_{i}_PASSWORD=password123\n\n")
    
    print("✅ Test setup complete! Credentials saved to test_credentials.txt")
    return True

if __name__ == "__main__":
    setup_test_users()