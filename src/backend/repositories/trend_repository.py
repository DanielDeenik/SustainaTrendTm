from typing import List, Optional, Dict, Any
from ..database.mongodb import Repository
from ..models.entities import Trend, PyObjectId
from datetime import datetime

class TrendRepository(Repository[Trend]):
    def __init__(self):
        super().__init__("trends", Trend)

    async def get_active_trends(self, limit: int = 10) -> List[Trend]:
        query = {
            "status": "active",
            "end_date": {"$gt": datetime.utcnow()}
        }
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="start_date",
            sort_order=-1
        )

    async def get_trends_by_category(self, category: str, limit: int = 10) -> List[Trend]:
        query = {"category": category}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_trends_by_company(self, company_id: PyObjectId) -> List[Trend]:
        query = {"related_companies": company_id}
        return await self.find_many(query=query)

    async def get_trends_by_vc(self, vc_id: PyObjectId) -> List[Trend]:
        query = {"related_vcs": vc_id}
        return await self.find_many(query=query)

    async def search_trends(self, search_term: str, limit: int = 10) -> List[Trend]:
        query = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"category": {"$regex": search_term, "$options": "i"}}
            ]
        }
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_trend_statistics(self) -> Dict[str, Any]:
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "avg_duration": {
                        "$avg": {
                            "$subtract": ["$end_date", "$start_date"]
                        }
                    }
                }
            }
        ]
        return await self.aggregate(pipeline) 