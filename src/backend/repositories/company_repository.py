from typing import List, Optional, Dict, Any
from ..database.mongodb import Repository
from ..models.entities import Company, PyObjectId
from datetime import datetime

class CompanyRepository(Repository[Company]):
    def __init__(self):
        super().__init__("companies", Company)

    async def get_companies_by_industry(self, industry: str, limit: int = 10) -> List[Company]:
        query = {"industry": industry}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_companies_by_size(self, size: str, limit: int = 10) -> List[Company]:
        query = {"size": size}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_companies_by_location(self, location: str, limit: int = 10) -> List[Company]:
        query = {"location": location}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def search_companies(self, search_term: str, limit: int = 10) -> List[Company]:
        query = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"industry": {"$regex": search_term, "$options": "i"}},
                {"location": {"$regex": search_term, "$options": "i"}}
            ]
        }
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_company_statistics(self) -> Dict[str, Any]:
        pipeline = [
            {
                "$group": {
                    "_id": "$industry",
                    "count": {"$sum": 1},
                    "avg_size": {"$avg": "$employee_count"},
                    "total_revenue": {"$sum": "$annual_revenue"}
                }
            }
        ]
        return await self.aggregate(pipeline)

    async def get_companies_by_trend(self, trend_id: PyObjectId) -> List[Company]:
        query = {"related_trends": trend_id}
        return await self.find_many(query=query)

    async def get_companies_by_vc(self, vc_id: PyObjectId) -> List[Company]:
        query = {"investors": vc_id}
        return await self.find_many(query=query) 