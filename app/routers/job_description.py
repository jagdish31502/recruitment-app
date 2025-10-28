"""
Router for Job Description management
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import tempfile
import os

from app.models.job_description import JobDescriptionGenerateRequest, JobDescriptionResponse, EmploymentType
from app.services.ai_service.ai_provider import AIProviderFactory
from app.services.document_processor import extract_text_from_file
from app.services.database_service import mongodb_service
from app.utilities.file_handler import save_uploaded_file, get_file_extension, validate_file_extension
from app.utilities.logger import setup_logger
from app.utilities.prompts import GENERATE_JOB_DESCRIPTION

logger = setup_logger()
router = APIRouter()


@router.post("/job-description/upload", response_model=JobDescriptionResponse)
async def upload_job_description(file: UploadFile = File(...)):
    """
    Upload a job description file (PDF or DOCX)
    """
    try:
        # Validate file extension
        if not validate_file_extension(file.filename, ['.pdf', '.doc', '.docx']):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload PDF, DOC, or DOCX files."
            )
        
        # Save uploaded file
        file_path = save_uploaded_file(file.file, file.filename)
        file_ext = get_file_extension(file.filename)
        
        logger.info(f"Extracting text from {file.filename}")
        
        # Extract text
        job_description_text = extract_text_from_file(file_path, file_ext)
        
        # Clean up
        os.remove(file_path)
        
        # Save to MongoDB
        job_description_id = await mongodb_service.save_job_description(
            job_description=job_description_text,
            source="upload",
            filename=file.filename,
            metadata={"file_size": file.size}
        )
        
        return JobDescriptionResponse(
            job_description=job_description_text,
            metadata={
                "filename": file.filename, 
                "file_size": file.size,
                "job_description_id": job_description_id
            }
        )
    
    except Exception as e:
        logger.exception(f"Error uploading job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job-description/input", response_model=JobDescriptionResponse)
async def input_job_description(job_description: str):
    """
    Submit job description via text input
    """
    try:
        if not job_description or len(job_description.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Job description must be at least 50 characters long."
            )
        
        # Save to MongoDB
        job_description_id = await mongodb_service.save_job_description(
            job_description=job_description,
            source="manual_input",
            metadata={"source": "manual_input"}
        )
        
        return JobDescriptionResponse(
            job_description=job_description,
            metadata={
                "source": "manual_input",
                "job_description_id": job_description_id
            }
        )
    
    except Exception as e:
        logger.exception(f"Error processing job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job-description/generate", response_model=JobDescriptionResponse)
async def generate_job_description(request: JobDescriptionGenerateRequest, provider: str = "openai", api_key: str = None):
    """
    Generate a job description using AI based on job requirements
    """
    try:
        logger.info(f"Generating job description for {request.job_title} using {provider}")
        
        # Create AI provider
        ai_provider = AIProviderFactory.create_provider(
            provider_type=provider,
            api_key=api_key
        )
        
        prompt = GENERATE_JOB_DESCRIPTION.format(
            job_title=request.job_title,
            years_of_experience=request.years_of_experience,
            must_have_skills=request.must_have_skills,
            company_name=request.company_name,
            employment_type=request.employment_type,
            industry=request.industry,
            location=request.location
        )
        
        job_description = await ai_provider.generate_text(prompt, temperature=0.7)
        
        # Save to MongoDB
        job_description_id = await mongodb_service.save_job_description(
            job_description=job_description,
            source="ai_generated",
            metadata={
                "job_title": request.job_title,
                "industry": request.industry,
                "location": request.location,
                "years_of_experience": request.years_of_experience,
                "must_have_skills": request.must_have_skills,
                "company_name": request.company_name,
                "employment_type": request.employment_type
            }
        )
        
        return JobDescriptionResponse(
            job_description=job_description,
            metadata={
                "source": "ai_generated",
                "job_title": request.job_title,
                "industry": request.industry,
                "location": request.location,
                "job_description_id": job_description_id
            }
        )
    
    except Exception as e:
        logger.exception(f"Error generating job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

