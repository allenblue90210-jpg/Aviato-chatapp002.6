
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def cleanup_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Cleaning up demo users...")
    
    # Logic: Delete users where _id is "current-user" OR length is small (single digits)
    # Real UUIDs are 36 chars. "current-user" is 12. "1" is 1.
    # We'll just delete specific IDs found in the previous step to be safe, or regex.
    
    # Safer: Delete known demo IDs
    demo_ids = ["current-user", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    
    result = await db.users.delete_many({
        "_id": {"$in": demo_ids}
    })
    
    print(f"Deleted {result.deleted_count} demo users.")
    
    # Also clean up conversations involving these users?
    # Ideally yes, but maybe not strictly required. Let's leave chats for now or they might break if one party is missing.
    # Actually, if a real user chatted with a demo user, that chat is now broken.
    # Let's remove conversations where any participant is missing.
    
    print("Cleaning up orphaned conversations...")
    
    # Get all valid user IDs
    valid_users = await db.users.find({}, {"_id": 1}).to_list(10000)
    valid_ids = [u["_id"] for u in valid_users]
    
    # Find chats where ANY participant is NOT in valid_ids
    # This is hard to do in one query without lookups.
    # Iterate and delete.
    
    convs = await db.conversations.find({}).to_list(10000)
    deleted_convs = 0
    for c in convs:
        participants = c.get("participants", [])
        if any(p not in valid_ids for p in participants):
            await db.conversations.delete_one({"_id": c["_id"]})
            deleted_convs += 1
            
    print(f"Deleted {deleted_convs} orphaned conversations.")

    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_users())
