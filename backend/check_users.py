import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def check_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    users = await db.users.find({}, {"email": 1, "password": 1}).to_list(100)
    print("Users found:", len(users))
    for u in users:
        print(f"User: {u.get('email')}, Hash len: {len(u.get('password', ''))}")

if __name__ == "__main__":
    asyncio.run(check_users())