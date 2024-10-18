from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from ..config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        
    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            
    @classmethod
    def get_db(cls):
        if cls.client is None:
            raise ConnectionError("Database not initialized")
        return cls.client[settings.DB_NAME]

    @classmethod
    def get_rules_collection(cls):
        return cls.get_db()["rules"]

async def init_db():
    await Database.connect_db()
    db = Database.get_db()
    
    # Create indexes
    await db.rules.create_index("id", unique=True)
    await db.rules.create_index([("name", "text")])