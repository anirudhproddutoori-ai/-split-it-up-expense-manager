import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://splitup_user:preetham3011@splitup-cluster.ohgqeud.mongodb.net/?appName=splitup-cluster"
DB_NAME = "splitup"

async def test():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    result = await db.test_collection.insert_one({
        "hello": "world"
    })

    print("Inserted ID:", result.inserted_id)

    doc = await db.test_collection.find_one({"hello": "world"})
    print("Fetched doc:", doc)

asyncio.run(test())
