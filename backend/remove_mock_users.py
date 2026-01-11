import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def remove_mock_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    mock_ids = ["current-user", "1", "2", "6"]
    result = await db.users.delete_many({"_id": {"$in": mock_ids}})
    
    print(f"Removed {result.deleted_count} mock users.")

if __name__ == "__main__":
    asyncio.run(remove_mock_users())