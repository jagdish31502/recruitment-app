"""
MongoDB models for storing job descriptions and candidate data
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class JobDescriptionDocument(BaseModel):
    """MongoDB document model for job descriptions"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    job_description: str = Field(..., description="Job description text")
    source: str = Field(..., description="Source of job description (upload, manual, ai_generated)")
    filename: Optional[str] = Field(None, description="Original filename if uploaded")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CandidateDocument(BaseModel):
    """MongoDB document model for candidate data"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    job_description_id: PyObjectId = Field(..., description="Reference to job description")
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    phone: Optional[str] = Field(None, description="Candidate phone number")
    filename: str = Field(..., description="Resume filename")
    matching_score: float = Field(..., description="Matching score percentage")
    matching_skills: List[str] = Field(default=[], description="List of matching skills")
    missing_skills: List[str] = Field(default=[], description="List of missing skills")
    remarks: str = Field(..., description="AI-generated remarks about the candidate")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MatchingSessionDocument(BaseModel):
    """MongoDB document model for matching sessions"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    job_description_id: PyObjectId = Field(..., description="Reference to job description")
    total_candidates: int = Field(..., description="Total number of candidates processed")
    best_match_score: float = Field(..., description="Best matching score")
    best_match_candidate_id: Optional[PyObjectId] = Field(None, description="Reference to best match candidate")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
