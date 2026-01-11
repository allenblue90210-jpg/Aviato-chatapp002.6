
import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def run_test():
    print("Testing Reset Logic with Simulated Frontend Payload...")
    ts = int(time.time())
    
    # 1. Create Orange User
    r = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"bug_repro_{ts}@test.com", "password": "pass", "name": "BugRepro"})
    token = r.json()['access_token']
    uid = r.json()['user']['id']
    
    print(f"Created User: {uid}")
    
    # Set to Orange 3
    r_put = requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": 3}
    })
    mode_start_1 = r_put.json()['availability'].get('modeStartedAt', 0)
    print(f"Mode Start 1: {mode_start_1}")
    
    # 2. Add active conversation (U1)
    r_u = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"u_bug_{ts}@test.com", "password": "pass", "name": "U_Bug"})
    t_u = r_u.json()['access_token']
    requests.post(f"{BASE_URL}/conversations/start", headers={"Authorization": f"Bearer {t_u}"}, json={"userId": uid})
    requests.post(f"{BASE_URL}/conversations/{uid}/messages", headers={"Authorization": f"Bearer {t_u}"}, json={"text": "hi"})
    
    # Verify 1/3
    u = requests.get(f"{BASE_URL}/users/{uid}").json()
    print(f"Count: {u['availability']['currentContacts']}/3")
    if u['availability']['currentContacts'] != 1:
        print("FAIL: Expected 1")
        return

    # 3. Simulate Frontend Update to Max=6
    # Frontend sends the FULL availability object including OLD modeStartedAt
    payload = {
        "availabilityMode": "orange",
        "availability": {
            "maxContact": 6,
            "modeStartedAt": mode_start_1, # OLD TIMESTAMP
            "currentContacts": 1 # Stale count
        }
    }
    
    print("Sending Update (Max=6) with OLD modeStartedAt...")
    time.sleep(1.1) # Ensure time passes
    
    r_update = requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json=payload)
    data = r_update.json()
    
    mode_start_2 = data['availability'].get('modeStartedAt', 0)
    print(f"Mode Start 2: {mode_start_2}")
    print(f"Count: {data['availability']['currentContacts']}/6")
    
    if mode_start_2 > mode_start_1:
        print("SUCCESS: Timestamp updated.")
    else:
        print("FAIL: Timestamp DID NOT update.")
        
    if data['availability']['currentContacts'] == 0:
        print("SUCCESS: Count reset to 0.")
    else:
        print(f"FAIL: Count is {data['availability']['currentContacts']}")

if __name__ == "__main__":
    run_test()
