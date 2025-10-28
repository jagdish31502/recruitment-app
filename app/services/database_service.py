"""
MongoDB service for database operations
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from bson import ObjectId

from app.models.database import (
    JobDescriptionDocument, 
    CandidateDocument, 
    MatchingSessionDocument
)
from app.utilities.logger import setup_logger

logger = setup_logger()


class MongoDBService:
    """MongoDB service for handling database operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "recruitment_app")
            
            self.client = AsyncIOMotorClient(mongodb_url)
            self.db = self.client[database_name]
            
            logger.info(f"Connected to MongoDB: {database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    # Job Description Operations
    async def save_job_description(
        self, 
        job_description: str, 
        source: str, 
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save job description to MongoDB"""
        try:
            doc = JobDescriptionDocument(
                job_description=job_description,
                source=source,
                filename=filename,
                metadata=metadata or {}
            )
            
            result = await self.db.job_descriptions.insert_one(doc.dict(by_alias=True))
            logger.info(f"Job description saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving job description: {e}")
            raise
    
    async def get_job_description(self, job_description_id: str) -> Optional[Dict[str, Any]]:
        """Get job description by ID"""
        try:
            doc = await self.db.job_descriptions.find_one({"_id": ObjectId(job_description_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            logger.error(f"Error getting job description: {e}")
            return None
    
    async def get_all_job_descriptions(self) -> List[Dict[str, Any]]:
        """Get all job descriptions"""
        try:
            cursor = self.db.job_descriptions.find().sort("created_at", -1)
            docs = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                docs.append(doc)
            return docs
        except Exception as e:
            logger.error(f"Error getting all job descriptions: {e}")
            return []
    
    # Candidate Operations
    async def save_candidate(
        self,
        job_description_id: str,
        name: str,
        email: str,
        phone: Optional[str],
        filename: str,
        matching_score: float,
        matching_skills: List[str],
        missing_skills: List[str],
        remarks: str
    ) -> str:
        """Save candidate data to MongoDB"""
        try:
            doc = CandidateDocument(
                job_description_id=ObjectId(job_description_id),
                name=name,
                email=email,
                phone=phone,
                filename=filename,
                matching_score=matching_score,
                matching_skills=matching_skills,
                missing_skills=missing_skills,
                remarks=remarks
            )
            
            result = await self.db.candidates.insert_one(doc.dict(by_alias=True))
            logger.info(f"Candidate saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving candidate: {e}")
            raise
    
    async def get_candidates_by_job_description(self, job_description_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for a specific job description"""
        try:
            cursor = self.db.candidates.find(
                {"job_description_id": ObjectId(job_description_id)}
            ).sort("matching_score", -1)
            
            candidates = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["job_description_id"] = str(doc["job_description_id"])
                candidates.append(doc)
            return candidates
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return []
    
    async def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Get all candidates"""
        try:
            cursor = self.db.candidates.find().sort("created_at", -1)
            candidates = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["job_description_id"] = str(doc["job_description_id"])
                candidates.append(doc)
            return candidates
        except Exception as e:
            logger.error(f"Error getting all candidates: {e}")
            return []
    
    # Matching Session Operations
    async def save_matching_session(
        self,
        job_description_id: str,
        total_candidates: int,
        best_match_score: float,
        best_match_candidate_id: Optional[str] = None
    ) -> str:
        """Save matching session data"""
        try:
            doc = MatchingSessionDocument(
                job_description_id=ObjectId(job_description_id),
                total_candidates=total_candidates,
                best_match_score=best_match_score,
                best_match_candidate_id=ObjectId(best_match_candidate_id) if best_match_candidate_id else None
            )
            
            result = await self.db.matching_sessions.insert_one(doc.dict(by_alias=True))
            logger.info(f"Matching session saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving matching session: {e}")
            raise
    
    async def get_matching_sessions(self) -> List[Dict[str, Any]]:
        """Get all matching sessions"""
        try:
            cursor = self.db.matching_sessions.find().sort("created_at", -1)
            sessions = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["job_description_id"] = str(doc["job_description_id"])
                if doc.get("best_match_candidate_id"):
                    doc["best_match_candidate_id"] = str(doc["best_match_candidate_id"])
                sessions.append(doc)
            return sessions
        except Exception as e:
            logger.error(f"Error getting matching sessions: {e}")
            return []
    
    # Combined Operations
    async def get_job_description_with_candidates(self, job_description_id: str) -> Optional[Dict[str, Any]]:
        """Get job description with all its candidates"""
        try:
            job_desc = await self.get_job_description(job_description_id)
            if not job_desc:
                return None
            
            candidates = await self.get_candidates_by_job_description(job_description_id)
            job_desc["candidates"] = candidates
            
            return job_desc
        except Exception as e:
            logger.error(f"Error getting job description with candidates: {e}")
            return None
    
    async def get_all_data_summary(self) -> Dict[str, Any]:
        """Get summary of all data"""
        try:
            job_descriptions = await self.get_all_job_descriptions()
            candidates = await self.get_all_candidates()
            sessions = await self.get_matching_sessions()
            
            return {
                "total_job_descriptions": len(job_descriptions),
                "total_candidates": len(candidates),
                "total_sessions": len(sessions),
                "job_descriptions": job_descriptions,
                "candidates": candidates,
                "sessions": sessions
            }
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}


# Global MongoDB service instance
mongodb_service = MongoDBService()
