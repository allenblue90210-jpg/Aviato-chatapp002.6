
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def remove_test_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Identifying test users...")
    
    # Logic: Remove users with @test.com email OR "Test" in name
    # The user specifically said "all these test user people"
    
    query = {
        "$or": [
            {"email": {"$regex": "@test.com$"}},
            {"name": {"$regex": "Test User"}},
            {"name": {"$regex": "Fresh User"}}
        ]
    }
    
    users_to_delete = await db.users.find(query).to_list(1000)
    
    if not users_to_delete:
        print("No test users found.")
        return

    ids_to_delete = [u["_id"] for u in users_to_delete]
    
    print(f"Found {len(ids_to_delete)} test users to delete:")
    for u in users_to_delete:
        print(f" - {u.get('name')} ({u.get('email')})")
        
    # Delete users
    result = await db.users.delete_many({"_id": {"$in": ids_to_delete}})
    print(f"Deleted {result.deleted_count} users.")
    
    # Delete conversations involving these users
    print("Cleaning up conversations...")
    
    # If a conversation has ANY participant in the deleted list, delete it?
    # Or just remove the conversation? Yes, delete the conversation.
    
    # Find conversations where 'participants' array contains any of ids_to_delete
    conv_result = await db.conversations.delete_many({
        "participants": {"$in": ids_to_delete}
    })
    
    print(f"Deleted {conv_result.deleted_count} conversations involving test users.")
    
    # Verify remaining
    remaining = await db.users.find({}).to_list(1000)
    print("\nRemaining Users (Real):")
    for u in remaining:
        print(f" - {u.get('name')} ({u.get('email')})")

    client.close()

if __name__ == "__main__":
    asyncio.run(remove_test_users())
