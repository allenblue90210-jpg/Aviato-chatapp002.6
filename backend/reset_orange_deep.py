
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def reset_orange_state():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Resetting Orange Mode state (Deep Clean)...")
    
    # 1. Find all Orange Mode users
    orange_users = await db.users.find({"availabilityMode": "orange"}).to_list(1000)
    orange_ids = [u["_id"] for u in orange_users]
    
    print(f"Found {len(orange_ids)} Orange Mode users.")
    
    if orange_ids:
        # 2. Delete ALL conversations involving these users
        result = await db.conversations.delete_many({
            "participants": {"$in": orange_ids}
        })
        print(f"Deleted {result.deleted_count} conversations involving Orange users.")
        
        # 3. Reset the fallback 'currentContacts' AND update 'modeStartedAt' to now
        # This ensures any 'ghost' conversations are strictly ignored
        now_ts = datetime.now().timestamp() * 1000
        await db.users.update_many(
            {"_id": {"$in": orange_ids}},
            {
                "$set": {
                    "availability.currentContacts": 0,
                    "availability.modeStartedAt": now_ts
                }
            }
        )
        print(f"Reset availability.currentContacts to 0 and modeStartedAt to {now_ts}.")

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_orange_state())
