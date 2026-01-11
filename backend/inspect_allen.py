
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def check_allen():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    users = await db.users.find({"name": {"$regex": "Allen Brown"}}).to_list(100)
    for u in users:
        print(f"Name: {u['name']}")
        print(f"Mode: {u.get('availabilityMode')}")
        print(f"Avail: {u.get('availability')}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(check_allen())
