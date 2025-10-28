"""
Router for Email Generation
"""
from fastapi import APIRouter, HTTPException
import json
import re

from app.services.ai_service.ai_provider import AIProviderFactory
from app.utilities.logger import setup_logger
from app.utilities.prompts import GENERATE_INTERVIEW_EMAIL, GENERATE_REJECTION_EMAIL
from app.models.email import EmailGenerationRequest, EmailGenerationResponse, ResumeMatchingSummary, CandidateInfo
from pydantic import BaseModel
from typing import Optional, Dict, Any

logger = setup_logger()
router = APIRouter()


class EmailWithMatchingRequest(BaseModel):
    """Request model for email generation with matching data"""
    candidate_name: str
    candidate_email: str
    job_description: str
    email_type: str
    company_name: str = "Our Company"
    hiring_manager_name: str = "Hiring Manager"
    job_title: Optional[str] = None
    matching_result: Optional[Dict[str, Any]] = None


def clean_json_response(response: str) -> str:
    """Clean JSON response from AI models"""
    cleaned = response.strip()
    
    # Remove markdown code blocks
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()
    
    # Try to extract JSON if there's extra text
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group()
    
    return cleaned


def format_matching_summary(matching_summary):
    """Format resume matching summary for email prompts"""
    if not matching_summary:
        return "No detailed matching analysis available."
    
    summary_parts = []
    
    # Add matching skills
    if matching_summary.matching_skills:
        skills_text = ", ".join(matching_summary.matching_skills[:5])  # Limit to top 5
        summary_parts.append(f"✅ Matching Skills: {skills_text}")
    
    # Add experience info
    if matching_summary.experience_years:
        summary_parts.append(f"📈 Experience: {matching_summary.experience_years} years")
    
    if matching_summary.relevant_experience:
        summary_parts.append(f"💼 Relevant Experience: {matching_summary.relevant_experience}")
    
    # Add education
    if matching_summary.education:
        summary_parts.append(f"🎓 Education: {matching_summary.education}")
    
    # Add strengths
    if matching_summary.strengths:
        strengths_text = ", ".join(matching_summary.strengths[:3])  # Limit to top 3
        summary_parts.append(f"🌟 Key Strengths: {strengths_text}")
    
    # Add missing skills (for rejection emails)
    if matching_summary.missing_skills:
        missing_text = ", ".join(matching_summary.missing_skills[:3])  # Limit to top 3
        summary_parts.append(f"⚠️ Areas for Growth: {missing_text}")
    
    # Add detailed remarks
    if matching_summary.remarks:
        summary_parts.append(f"📝 Analysis: {matching_summary.remarks}")
    
    formatted_summary = "\n".join(summary_parts) if summary_parts else "No detailed matching analysis available."
    
    # Debug logging
    logger.info(f"Formatted matching summary: {formatted_summary}")
    
    return formatted_summary


def convert_resume_match_to_summary(match_result: dict) -> ResumeMatchingSummary:
    """Convert resume matching result to ResumeMatchingSummary format"""
    resume_info = match_result.get('resume_info', {})
    
    # Debug logging
    logger.info(f"Converting match result: {match_result}")
    logger.info(f"Resume info: {resume_info}")
    
    return ResumeMatchingSummary(
        matching_skills=match_result.get('matching_skills', []),
        missing_skills=match_result.get('missing_skills', []),
        remarks=match_result.get('remarks', ''),
        experience_years=resume_info.get('experience_years'),
        relevant_experience=resume_info.get('relevant_experience'),
        education=resume_info.get('education'),
        strengths=resume_info.get('strengths', [])
    )


@router.post("/email/generate-with-matching", response_model=EmailGenerationResponse)
async def generate_email_with_matching(
    request: EmailWithMatchingRequest,
    provider: str = "openai",
    api_key: str = None
):
    """
    Generate personalized email with resume matching data
    This endpoint accepts resume matching results and generates personalized emails
    """
    try:
        logger.info(f"Generating {request.email_type} email for {request.candidate_name} with matching data")
        
        # Convert matching result to summary format
        matching_summary = None
        if request.matching_result:
            matching_summary = convert_resume_match_to_summary(request.matching_result)
        
        # Create candidate info with matching summary
        candidate_info = CandidateInfo(
            name=request.candidate_name,
            email=request.candidate_email,
            score=request.matching_result.get('score', 0) if request.matching_result else 0,
            matching_summary=matching_summary
        )
        
        # Create request for main email generation function
        email_request = EmailGenerationRequest(
            candidate_info=candidate_info,
            job_description=request.job_description,
            email_type=request.email_type,
            company_name=request.company_name,
            hiring_manager_name=request.hiring_manager_name,
            job_title=request.job_title
        )
        
        # Generate email using the main function
        return await generate_email(email_request, provider, api_key)
        
    except Exception as e:
        logger.exception(f"Error generating email with matching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/generate", response_model=EmailGenerationResponse)
async def generate_email(request: EmailGenerationRequest, provider: str = "openai", api_key: str = None):
    """
    Generate personalized emails for candidates with resume matching insights
    """
    try:
        logger.info(f"Generating {request.email_type} email for {request.candidate_info.name}")
        
        # Validate email type
        if request.email_type not in ["interview", "rejection"]:
            raise HTTPException(
                status_code=400,
                detail="email_type must be either 'interview' or 'rejection'"
            )
        
        # Create AI provider
        ai_provider = AIProviderFactory.create_provider(
            provider_type=provider,
            api_key=api_key
        )
        
        # Extract job title from JD if not provided
        job_title = request.job_title or "the position"
        if job_title == "the position":
            jd_text = request.job_description[:500]
            title_match = re.search(r'(?:position|role|title)[:.]?\s*([A-Za-z\s]+)', jd_text, re.IGNORECASE)
            if title_match:
                job_title = title_match.group(1).strip()
        
        # Format matching summary
        matching_summary_text = format_matching_summary(request.candidate_info.matching_summary)
        
        # Select appropriate prompt
        if request.email_type == "interview":
            prompt = GENERATE_INTERVIEW_EMAIL.format(
                candidate_name=request.candidate_info.name,
                candidate_email=request.candidate_info.email,
                score=request.candidate_info.score,
                matching_summary=matching_summary_text,
                job_title=job_title,
                company_name=request.company_name,
                manager_name=request.hiring_manager_name
            )
        else:
            prompt = GENERATE_REJECTION_EMAIL.format(
                candidate_name=request.candidate_info.name,
                candidate_email=request.candidate_info.email,
                score=request.candidate_info.score,
                matching_summary=matching_summary_text,
                job_title=job_title,
                company_name=request.company_name,
                manager_name=request.hiring_manager_name
            )
        
        # Generate email
        response = await ai_provider.generate_text(prompt, temperature=0.7)
        
        # Parse JSON response
        try:
            cleaned = clean_json_response(response)
            email_data = json.loads(cleaned)
            
            return EmailGenerationResponse(
                email_subject=email_data.get('subject', f"Application Update - {job_title}"),
                email_body=email_data.get('body', response),
                candidate_name=request.candidate_info.name,
                email_type=request.email_type,
                personalized_insights=matching_summary_text
            )
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response[:200]}")
            # Fallback: use the response as body with a default subject
            return EmailGenerationResponse(
                email_subject=f"{'Interview Invitation' if request.email_type == 'interview' else 'Application Update'} - {job_title}",
                email_body=response,
                candidate_name=request.candidate_info.name,
                email_type=request.email_type,
                personalized_insights=matching_summary_text
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))