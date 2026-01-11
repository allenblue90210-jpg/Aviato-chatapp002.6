
import requests
import json

BASE_URL = "http://localhost:8001/api"

def check_allen():
    print("Checking Allen Brown Availability...")
    
    # 1. Login Smeagol
    # Need Smeagol's email? "smeagol" -> "allenbrowndharak@gmail.com" from earlier log
    # But I don't know password.
    # I will signup Smeagol2 to test.
    
    import time
    ts = int(time.time())
    r = requests.post(f"{BASE_URL}/auth/signup", json={"email": f"smeagol_test_log_{ts}@test.com", "password": "pass", "name": "Smeagol Test"})
    token = r.json()['access_token']
    
    # Allen Brown ID (from inspect)
    # I need to get it dynamically or hardcode if I saw it?
    # I didn't see the full ID in `inspect_allen.py` output (I printed it but truncated?).
    # Wait, `get_users` returns list.
    
    users = requests.get(f"{BASE_URL}/users").json()
    allen = next((u for u in users if "Allen Brown" in u['name']), None)
    
    if not allen:
        print("Allen not found.")
        return
        
    uid = allen['id']
    print(f"Allen ID: {uid}")
    print(f"Allen Mode: {allen.get('availabilityMode')}")
    print(f"Allen Time: {allen['availability'].get('timedHour')}:{allen['availability'].get('timedMinute')}")
    
    # 2. Try Start Chat (Header Offset 0 -> UTC)
    # UTC is ~20:50. Allen 15:15.
    # 20 > 15. Should block.
    
    headers = {"Authorization": f"Bearer {token}", "x-timezone-offset": "0"}
    resp = requests.post(f"{BASE_URL}/conversations/start", headers=headers, json={"userId": uid})
    
    print(f"Start Chat (Offset 0): {resp.status_code}")
    if resp.status_code == 403:
        print("Blocked correctly (UTC).")
    else:
        print(f"FAILED (UTC). Msg: {resp.text}")
        
    # 3. Try Offset 300 (EST).
    # UTC 20:50 - 5h = 15:50.
    # 15:50 >= 15:15. Should block.
    headers = {"Authorization": f"Bearer {token}", "x-timezone-offset": "300"}
    resp = requests.post(f"{BASE_URL}/conversations/start", headers=headers, json={"userId": uid})
    print(f"Start Chat (Offset 300): {resp.status_code}. Msg: {resp.text}")
    
    # 4. Try Offset -60 (UTC+1).
    # UTC 20:50 + 1h = 21:50.
    # 21 > 15. Should block.
    
    # 5. Try Offset that opens it?
    # Need Local < 15:15.
    # UTC 20:50. Need < 15:15.
    # Offset > 5h 35m.
    # Try Offset 600 (10h behind). 10:50 AM.
    # 10 < 15. Should Open.
    headers = {"Authorization": f"Bearer {token}", "x-timezone-offset": "600"}
    resp = requests.post(f"{BASE_URL}/conversations/start", headers=headers, json={"userId": uid})
    print(f"Start Chat (Offset 600): {resp.status_code}")

if __name__ == "__main__":
    check_allen()
