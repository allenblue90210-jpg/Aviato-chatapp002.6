
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
from datetime import datetime
import time
import requests

BASE_URL = "http://localhost:8001/api"

def run_test():
    print("Testing Reset Logic...")
    ts = int(time.time())
    
    # 1. Create Orange User
    r = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"reset_test_{ts}@test.com", "password": "pass", "name": "ResetTarget"})
    token = r.json()['access_token']
    uid = r.json()['user']['id']
    
    # Set to Orange 3
    requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": 3}
    })
    
    # 2. Add 2 active users
    for i in range(2):
        r_u = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"u_{i}_{ts}@test.com", "password": "pass", "name": f"U{i}"})
        t_u = r_u.json()['access_token']
        # Send message
        requests.post(f"{BASE_URL}/conversations/{uid}/messages", headers={"Authorization": f"Bearer {t_u}"}, json={"text": "hi"})
        
    # 3. Verify 2/3
    u = requests.get(f"{BASE_URL}/users/{uid}").json()
    print(f"State 1: {u['availability']['currentContacts']}/{u['availability']['maxContact']}")
    if u['availability']['currentContacts'] != 2:
        print("FAIL: Expected 2")
        return

    # 4. Set to 7 (Should Reset to 0/7)
    print("Updating to 7...")
    # Add delay to ensure timestamps differ
    time.sleep(1.1) 
    
    resp = requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": 7}
    }).json()
    
    print(f"State 2 (Response): {resp['availability']['currentContacts']}/{resp['availability']['maxContact']}")
    
    if resp['availability']['currentContacts'] == 0 and resp['availability']['maxContact'] == 7:
        print("SUCCESS: Reset to 0/7 confirmed.")
    else:
        print("FAIL: Did not reset.")

if __name__ == "__main__":
    run_test()
