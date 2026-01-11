
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

ALLOWED_EMAILS = [
    "allenbrown530@gmail.com",
    "allendharak9@gmail.com",
    "allenbrowndharak@gmail.com",
    "manbirdglobal@gmail.com",
    "allenkinetic001@gmail.com",
    "allenred90210@gmail.com"
]

async def cleanup_all():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Starting Universal Cleanup of Mock Users...")
    
    # 1. Identify users to delete
    # Find all users whose email is NOT in ALLOWED_EMAILS
    users_to_delete = await db.users.find({
        "email": {"$nin": ALLOWED_EMAILS}
    }).to_list(10000)
    
    ids_to_delete = [u["_id"] for u in users_to_delete]
    
    print(f"Found {len(ids_to_delete)} mock/test users to delete.")
    for u in users_to_delete:
        print(f" - Deleting: {u.get('name')} ({u.get('email')})")
        
    if ids_to_delete:
        # 2. Delete Users
        result = await db.users.delete_many({"_id": {"$in": ids_to_delete}})
        print(f"Deleted {result.deleted_count} users from DB.")
        
        # 3. Delete Conversations
        # Delete any conversation where ANY participant is in ids_to_delete
        conv_result = await db.conversations.delete_many({
            "participants": {"$in": ids_to_delete}
        })
        print(f"Deleted {conv_result.deleted_count} conversations involving mock users.")
        
    print("\nRemaining Real Users:")
    real_users = await db.users.find({}).to_list(1000)
    for u in real_users:
        print(f" + {u.get('name')} ({u.get('email')})")

    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_all())
