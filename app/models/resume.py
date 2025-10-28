"""
Pydantic models for Resume
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeMatchResult(BaseModel):
    """Result of matching a resume against job description"""
    filename: str = Field(..., description="Resume filename")
    score: float = Field(..., description="Matching score (0-100)")
    missing_skills: List[str] = Field(default_factory=list, description="Missing required skills")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match requirements")
    remarks: str = Field(..., description="Brief evaluation remarks")
    extracted_text: str = Field(..., description="Extracted resume text")


class ResumeMatchingRequest(BaseModel):
    """Request model for resume matching"""
    job_description: str = Field(..., description="Job description text")
    job_description_id: Optional[str] = Field(None, description="Job description ID from database")
    resume_texts: List[str] = Field(..., description="List of resume texts")
    resume_filenames: List[str] = Field(..., description="List of resume filenames")
    skills_keywords: Optional[List[str]] = Field(default=None, description="Required skills keywords")
    candidate_info: Optional[List[dict]] = Field(default=None, description="Candidate information (name, email, phone)")


class ResumeMatchingResponse(BaseModel):
    """Response model for resume matching results"""
    results: List[ResumeMatchResult] = Field(..., description="List of matching results")
    best_match: Optional[ResumeMatchResult] = Field(default=None, description="Best matching candidate")
    total_candidates: int = Field(..., description="Total number of candidates evaluated")

