from typing import Optional, TypeVar, Generic, Type, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import logging
from ..models.entities import PyObjectId

logger = logging.getLogger(__name__)

T = TypeVar('T')

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls, mongodb_url: str, db_name: str):
        try:
            cls.client = AsyncIOMotorClient(mongodb_url)
            cls.db = cls.client[db_name]
            logger.info("Connected to MongoDB.")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_database_connection(cls):
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection.")

class Repository(Generic[T]):
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection = MongoDB.db[collection_name]
        self.model_class = model_class

    async def create(self, data: Dict[str, Any]) -> T:
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(data)
        return await self.get_by_id(result.inserted_id)

    async def get_by_id(self, id: PyObjectId) -> Optional[T]:
        if data := await self.collection.find_one({"_id": id}):
            return self.model_class(**data)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return [self.model_class(**doc) async for doc in cursor]

    async def update(self, id: PyObjectId, data: Dict[str, Any]) -> Optional[T]:
        data["updated_at"] = datetime.utcnow()
        if result := await self.collection.update_one(
            {"_id": id}, {"$set": data}
        ):
            return await self.get_by_id(id)
        return None

    async def delete(self, id: PyObjectId) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        if data := await self.collection.find_one(query):
            return self.model_class(**data)
        return None

    async def find_many(
        self,
        query: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: int = DESCENDING
    ) -> List[T]:
        cursor = self.collection.find(query)
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
        cursor = cursor.skip(skip).limit(limit)
        return [self.model_class(**doc) async for doc in cursor]

    async def count(self, query: Dict[str, Any]) -> int:
        return await self.collection.count_documents(query)

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cursor = self.collection.aggregate(pipeline)
        return [doc async for doc in cursor] 