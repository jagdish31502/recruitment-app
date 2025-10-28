"""
Router for Resume Matching
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.models.resume import ResumeMatchingRequest, ResumeMatchingResponse
from app.services.matching_service.resume_matcher import match_resumes
from app.services.ai_service.ai_provider import AIProviderFactory
from app.services.database_service import mongodb_service
from app.utilities.logger import setup_logger

logger = setup_logger()
router = APIRouter()


@router.post("/resume-matching/match", response_model=ResumeMatchingResponse)
async def match_resumes_with_jd(request: ResumeMatchingRequest, provider: str = "openai", use_ai: bool = True, api_key: str = None):
    """
    Match resumes against job description and calculate scores
    """
    try:
        logger.info(f"Matching {len(request.resume_texts)} resumes with AI: {use_ai}")
        
        if len(request.resume_texts) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 resumes allowed per request"
            )
        
        if len(request.resume_texts) != len(request.resume_filenames):
            raise HTTPException(
                status_code=400,
                detail="Number of resume texts must match number of filenames"
            )
        
        # Create AI provider if using AI
        ai_provider = None
        if use_ai:
            try:
                ai_provider = AIProviderFactory.create_provider(provider_type=provider, api_key=api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize AI provider, using basic matching: {e}")
                use_ai = False
        
        # Match resumes
        results = await match_resumes(
            resume_texts=request.resume_texts,
            filenames=request.resume_filenames,
            job_description=request.job_description,
            provider=ai_provider,
            use_ai=use_ai,
            required_skills=request.skills_keywords
        )
        
        # Convert to response format
        from app.models.resume import ResumeMatchResult
        match_results = [
            ResumeMatchResult(
                filename=r['filename'],
                score=r['score'],
                missing_skills=r.get('missing_skills', []),
                matching_skills=r.get('matching_skills', []),
                remarks=r['remarks'],
                extracted_text=r['extracted_text']
            )
            for r in results
        ]
        
        # Get best match (first result, already sorted by score)
        best_match = match_results[0] if match_results else None
        
        # Save candidates to MongoDB if job_description_id is provided
        best_match_candidate_id = None
        if request.job_description_id:
            try:
                # Save each candidate
                candidate_ids = []
                for i, result in enumerate(results):
                    # Extract candidate info if provided
                    candidate_name = "Unknown"
                    candidate_email = "unknown@example.com"
                    candidate_phone = None
                    
                    if request.candidate_info and i < len(request.candidate_info):
                        candidate_info = request.candidate_info[i]
                        candidate_name = candidate_info.get('name', candidate_name)
                        candidate_email = candidate_info.get('email', candidate_email)
                        candidate_phone = candidate_info.get('phone', candidate_phone)
                    else:
                        # Generate from filename
                        candidate_name = result['filename'].split('.')[0].replace('_', ' ').title()
                        candidate_email = f"{candidate_name.lower().replace(' ', '.')}@example.com"
                    
                    candidate_id = await mongodb_service.save_candidate(
                        job_description_id=request.job_description_id,
                        name=candidate_name,
                        email=candidate_email,
                        phone=candidate_phone,
                        filename=result['filename'],
                        matching_score=result['score'],
                        matching_skills=result.get('matching_skills', []),
                        missing_skills=result.get('missing_skills', []),
                        remarks=result['remarks']
                    )
                    candidate_ids.append(candidate_id)
                    
                    # Store best match candidate ID
                    if i == 0:
                        best_match_candidate_id = candidate_id
                
                # Save matching session
                await mongodb_service.save_matching_session(
                    job_description_id=request.job_description_id,
                    total_candidates=len(results),
                    best_match_score=results[0]['score'] if results else 0,
                    best_match_candidate_id=best_match_candidate_id
                )
                
                logger.info(f"Saved {len(results)} candidates to MongoDB")
                
            except Exception as e:
                logger.error(f"Error saving candidates to MongoDB: {e}")
                # Don't fail the request if MongoDB save fails
        
        return ResumeMatchingResponse(
            results=match_results,
            best_match=best_match,
            total_candidates=len(results)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error matching resumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

