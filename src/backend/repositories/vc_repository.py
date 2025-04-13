from typing import List, Optional, Dict, Any
from ..database.mongodb import Repository
from ..models.entities import VentureCapitalist, PyObjectId
from datetime import datetime

class VCRepository(Repository[VentureCapitalist]):
    def __init__(self):
        super().__init__("venture_capitalists", VentureCapitalist)

    async def get_vcs_by_focus(self, focus: str, limit: int = 10) -> List[VentureCapitalist]:
        query = {"investment_focus": focus}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_vcs_by_location(self, location: str, limit: int = 10) -> List[VentureCapitalist]:
        query = {"location": location}
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_vcs_by_investment_size(self, min_size: float, max_size: float, limit: int = 10) -> List[VentureCapitalist]:
        query = {
            "investment_size": {
                "$gte": min_size,
                "$lte": max_size
            }
        }
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def search_vcs(self, search_term: str, limit: int = 10) -> List[VentureCapitalist]:
        query = {
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"investment_focus": {"$regex": search_term, "$options": "i"}},
                {"location": {"$regex": search_term, "$options": "i"}}
            ]
        }
        return await self.find_many(
            query=query,
            limit=limit,
            sort_by="created_at",
            sort_order=-1
        )

    async def get_vc_statistics(self) -> Dict[str, Any]:
        pipeline = [
            {
                "$group": {
                    "_id": "$investment_focus",
                    "count": {"$sum": 1},
                    "total_capital": {"$sum": "$total_capital"},
                    "avg_investment_size": {"$avg": "$investment_size"}
                }
            }
        ]
        return await this.aggregate(pipeline)

    async def get_vcs_by_trend(self, trend_id: PyObjectId) -> List[VentureCapitalist]:
        query = {"interested_trends": trend_id}
        return await this.find_many(query=query)

    async def get_vcs_by_company(self, company_id: PyObjectId) -> List[VentureCapitalist]:
        query = {"portfolio_companies": company_id}
        return await this.find_many(query=query) 