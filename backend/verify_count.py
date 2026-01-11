
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
from datetime import datetime

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def verify_logic():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Testing Dynamic Count Logic...")
    
    # 1. Create Orange User
    uid = str(uuid.uuid4())
    await db.users.insert_one({
        "_id": uid,
        "id": uid,
        "name": "Count Test User",
        "email": f"count_{uuid.uuid4()}@test.com",
        "availabilityMode": "orange",
        "availability": {"maxContact": 3}
    })
    print(f"Created user {uid}")
    
    # 2. Check Count (Should be 0)
    count_0 = await db.conversations.count_documents({
        "participants": uid,
        "messages": {"$not": {"$size": 0}}
    })
    print(f"Initial Count: {count_0} (Expected 0)")
    
    # 3. Create EMPTY conversation
    conv_id = str(uuid.uuid4())
    await db.conversations.insert_one({
        "_id": conv_id,
        "participants": [uid, "other_user"],
        "messages": []
    })
    
    # 4. Check Count (Should still be 0)
    count_1 = await db.conversations.count_documents({
        "participants": uid,
        "messages": {"$not": {"$size": 0}}
    })
    print(f"After Empty Chat: {count_1} (Expected 0)")
    
    # 5. Add Message
    await db.conversations.update_one(
        {"_id": conv_id},
        {"$push": {"messages": {"text": "Hello", "senderId": "other_user"}}}
    )
    
    # 6. Check Count (Should be 1)
    count_2 = await db.conversations.count_documents({
        "participants": uid,
        "messages": {"$not": {"$size": 0}}
    })
    print(f"After Message: {count_2} (Expected 1)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_logic())
