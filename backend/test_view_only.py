
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
from datetime import datetime
import time

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def reproduce_issue():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Testing 'View Only' Count Logic...")
    
    # 1. Create Orange User
    uid = str(uuid.uuid4())
    mode_start = datetime.now().timestamp() * 1000
    await db.users.insert_one({
        "_id": uid,
        "id": uid,
        "name": "View Only Test",
        "email": f"view_{uuid.uuid4()}@test.com",
        "availabilityMode": "orange",
        "availability": {
            "maxContact": 5,
            "modeStartedAt": mode_start
        }
    })
    
    # 2. Start Chat (User 2)
    user2_id = str(uuid.uuid4())
    await db.conversations.insert_one({
        "_id": str(uuid.uuid4()),
        "participants": [uid, user2_id],
        "messages": [],
        # No timerStarted
    })
    
    # 3. Check Count
    count = await db.conversations.count_documents({
        "participants": uid,
        "messages": {"$not": {"$size": 0}},
        "timerStarted": {"$gt": mode_start}
    })
    
    print(f"Count after Start Chat (Empty): {count}")
    
    if count == 0:
        print("SUCCESS: 0/5")
    else:
        print(f"FAILURE: {count}/5")

    client.close()

if __name__ == "__main__":
    asyncio.run(reproduce_issue())
