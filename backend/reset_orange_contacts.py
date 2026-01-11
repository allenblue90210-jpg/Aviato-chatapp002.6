
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def reset_contacts():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Resetting Orange Mode contact counters...")
    
    # Reset currentContacts to 0 for ALL users
    result = await db.users.update_many(
        {},
        {
            "$set": {
                "availability.currentContacts": 0
            }
        }
    )
    
    print(f"Reset complete. Updated {result.modified_count} users.")
    
    # Optional: Verify
    users = await db.users.find({"availabilityMode": "orange"}).to_list(100)
    for u in users:
        print(f"User {u.get('name')}: Current Contacts = {u.get('availability', {}).get('currentContacts')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_contacts())
