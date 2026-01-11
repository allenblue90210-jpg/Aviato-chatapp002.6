
import requests
import time

BASE_URL = "http://localhost:8001/api"

def run_test():
    ts = int(time.time())
    print("Testing 'Set to 5 -> 0/5' Logic...")
    
    # 1. Create Orange User
    r = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"target5_{ts}@test.com", "password": "pass", "name": "Target"})
    token = r.json()['access_token']
    uid = r.json()['user']['id']
    
    requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": 3}
    })
    
    # 2. Fill it (User 1)
    r1 = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"u1_{ts}@test.com", "password": "pass", "name": "U1"})
    t1 = r1.json()['access_token']
    requests.post(f"{BASE_URL}/conversations/start", headers={"Authorization": f"Bearer {t1}"}, json={"userId": uid})
    requests.post(f"{BASE_URL}/conversations/{uid}/messages", headers={"Authorization": f"Bearer {t1}"}, json={"text": "hi"})
    
    # Verify 1/3
    u = requests.get(f"{BASE_URL}/users/{uid}").json()
    print(f"Status: {u['availability']['currentContacts']}/{u['availability']['maxContact']}")
    
    # 3. Set to 5
    requests.put(f"{BASE_URL}/users/{uid}", headers={"Authorization": f"Bearer {token}"}, json={
        "availabilityMode": "orange",
        "availability": {"maxContact": 5}
    })
    
    # 4. Verify 0/5
    u = requests.get(f"{BASE_URL}/users/{uid}").json()
    print(f"Status After Update: {u['availability']['currentContacts']}/{u['availability']['maxContact']}")
    
    if u['availability']['currentContacts'] == 0 and u['availability']['maxContact'] == 5:
        print("SUCCESS: 0/5 confirmed.")
    else:
        print("FAILURE.")

if __name__ == "__main__":
    run_test()
