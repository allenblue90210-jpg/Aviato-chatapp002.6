
import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def create_user(email, name):
    resp = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email, "password": "password", "name": name
    })
    return resp.json()['access_token'], resp.json()['user']['id']

def set_orange(token, user_id, max_c):
    requests.put(f"{BASE_URL}/users/{user_id}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": max_c}
    })

def start_chat(token, target_id):
    resp = requests.post(f"{BASE_URL}/conversations/start", headers={"Authorization": f"Bearer {token}"}, json={"userId": target_id})
    return resp.status_code

def send_message(token, target_id, text):
    resp = requests.post(f"{BASE_URL}/conversations/{target_id}/messages", headers={"Authorization": f"Bearer {token}"}, json={"text": text})
    return resp.status_code

def run_test():
    print("Running Orange Mode Existing User Bypass Test...")
    ts = int(time.time())
    
    # 1. Setup
    token_o, id_o = create_user(f"orange_{ts}@test.com", "Orange")
    set_orange(token_o, id_o, 3)
    
    tokens = []
    for i in range(1, 5):
        t, uid = create_user(f"user{i}_{ts}@test.com", f"User {i}")
        tokens.append((t, uid))
        
    # 2. Fill slots (User 1-3)
    for i in range(3):
        start_chat(tokens[i][0], id_o)
        code = send_message(tokens[i][0], id_o, "First msg")
        print(f"User {i+1} sent message: {code}")
        
    # 3. User 4 attempts (Should fail sending)
    start_chat(tokens[3][0], id_o) # Open chat
    code_4 = send_message(tokens[3][0], id_o, "First msg")
    print(f"User 4 (New) sent message: {code_4} (Expected 403)")
    
    # 4. User 1 attempts again (Should succeed despite limit)
    code_1_again = send_message(tokens[0][0], id_o, "Second msg")
    print(f"User 1 (Existing) sent message: {code_1_again} (Expected 200)")
    
    if code_4 == 403 and code_1_again == 200:
        print("SUCCESS: Logic verified.")
    else:
        print("FAILURE: Logic mismatch.")

if __name__ == "__main__":
    run_test()
