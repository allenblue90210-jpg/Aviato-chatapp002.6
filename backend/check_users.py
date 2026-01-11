
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aviato_db')

async def list_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    users = await db.users.find({}, {"_id": 1, "name": 1, "email": 1}).to_list(1000)
    print("Current Users:")
    for u in users:
        print(f"ID: {u['_id']}, Name: {u.get('name')}, Email: {u.get('email')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(list_users())
