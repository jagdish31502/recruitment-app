"""
Router for Database Operations
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.services.database_service import mongodb_service
from app.utilities.logger import setup_logger

logger = setup_logger()
router = APIRouter()


@router.get("/database/job-descriptions")
async def get_all_job_descriptions():
    """Get all job descriptions from database"""
    try:
        job_descriptions = await mongodb_service.get_all_job_descriptions()
        return {"job_descriptions": job_descriptions}
    except Exception as e:
        logger.error(f"Error getting job descriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/job-descriptions/{job_description_id}")
async def get_job_description(job_description_id: str):
    """Get specific job description by ID"""
    try:
        job_description = await mongodb_service.get_job_description(job_description_id)
        if not job_description:
            raise HTTPException(status_code=404, detail="Job description not found")
        return job_description
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/job-descriptions/{job_description_id}/candidates")
async def get_candidates_by_job_description(job_description_id: str):
    """Get all candidates for a specific job description"""
    try:
        candidates = await mongodb_service.get_candidates_by_job_description(job_description_id)
        return {"candidates": candidates}
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/candidates")
async def get_all_candidates():
    """Get all candidates from database"""
    try:
        candidates = await mongodb_service.get_all_candidates()
        return {"candidates": candidates}
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/matching-sessions")
async def get_matching_sessions():
    """Get all matching sessions"""
    try:
        sessions = await mongodb_service.get_matching_sessions()
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting matching sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/summary")
async def get_data_summary():
    """Get summary of all data in database"""
    try:
        summary = await mongodb_service.get_all_data_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/job-descriptions/{job_description_id}/full")
async def get_job_description_with_candidates(job_description_id: str):
    """Get job description with all its candidates"""
    try:
        data = await mongodb_service.get_job_description_with_candidates(job_description_id)
        if not data:
            raise HTTPException(status_code=404, detail="Job description not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job description with candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
