"""
Pydantic models for Job Description
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmploymentType(str, Enum):
    """Employment type enum"""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    TEMPORARY = "Temporary"


class JobDescriptionGenerateRequest(BaseModel):
    """Request model for AI-generated job descriptions"""
    job_title: str = Field(..., description="Job title")
    years_of_experience: int = Field(..., description="Years of experience required")
    must_have_skills: str = Field(..., description="Comma-separated must-have skills")
    company_name: str = Field(..., description="Company name")
    employment_type: EmploymentType = Field(..., description="Employment type")
    industry: str = Field(..., description="Industry")
    location: str = Field(..., description="Job location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Python Developer",
                "years_of_experience": 5,
                "must_have_skills": "Python, FastAPI, PostgreSQL, Docker",
                "company_name": "Tech Corp",
                "employment_type": "Full-time",
                "industry": "Technology",
                "location": "San Francisco, CA"
            }
        }


class JobDescriptionResponse(BaseModel):
    """Response model for job description"""
    job_description: str = Field(..., description="Generated or uploaded job description text")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")

