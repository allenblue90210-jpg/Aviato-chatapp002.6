
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def reset_profile_pics():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Resetting All Profile Pictures to None...")
    result = await db.users.update_many(
        {},
        {
            "$set": {
                "profilePic": None
            }
        }
    )
    
    print(f"Reset complete. Updated {result.modified_count} users.")
    client.close()

if __name__ == "__main__":
    asyncio.run(reset_profile_pics())
