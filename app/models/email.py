"""
Pydantic models for Email Generation
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class ResumeMatchingSummary(BaseModel):
    """Resume matching summary for personalized emails"""
    matching_skills: List[str] = Field(default=[], description="Skills that match the job requirements")
    missing_skills: List[str] = Field(default=[], description="Skills missing from the candidate")
    remarks: str = Field(default="", description="Detailed matching analysis and remarks")
    experience_years: Optional[int] = Field(default=None, description="Candidate's years of experience")
    relevant_experience: Optional[str] = Field(default=None, description="Relevant work experience")
    education: Optional[str] = Field(default=None, description="Educational background")
    strengths: List[str] = Field(default=[], description="Candidate's key strengths")


class CandidateInfo(BaseModel):
    """Candidate information for email generation"""
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    score: float = Field(..., description="Candidate matching score")
    matching_summary: Optional[ResumeMatchingSummary] = Field(default=None, description="Resume matching analysis")


class EmailGenerationRequest(BaseModel):
    """Request model for email generation"""
    candidate_info: CandidateInfo = Field(..., description="Candidate information")
    job_description: str = Field(..., description="Job description text")
    email_type: Literal["interview", "rejection"] = Field(..., description="Type of email to generate")
    company_name: Optional[str] = Field(default="Our Company", description="Company name")
    hiring_manager_name: Optional[str] = Field(default="Hiring Manager", description="Hiring manager name")
    job_title: Optional[str] = Field(default=None, description="Job title")


class EmailGenerationResponse(BaseModel):
    """Response model for generated email"""
    email_subject: str = Field(..., description="Email subject line")
    email_body: str = Field(..., description="Email body text")
    candidate_name: str = Field(..., description="Candidate name")
    email_type: str = Field(..., description="Type of email")
    personalized_insights: Optional[str] = Field(default=None, description="Key insights used for personalization")

