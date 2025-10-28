"""
Resume matching service using AI to evaluate candidates with intelligent extraction
"""
import re
from typing import List
from app.utilities.logger import setup_logger
from app.services.matching_service.ai_extractor import (
    extract_resume_info_ai, 
    extract_jd_info_ai, 
    intelligent_match
)

logger = setup_logger()


async def match_resumes(resume_texts: List[str], filenames: List[str], job_description: str, 
                        provider=None, use_ai: bool = True, required_skills: List[str] = None) -> List[dict]:
    """Match multiple resumes against job description using AI-based extraction"""
    
    results = []
    
    # Extract JD information once
    jd_info = {}
    if use_ai and provider:
        try:
            logger.info("Extracting job description information with AI...")
            jd_info = await extract_jd_info_ai(job_description, provider)
        except Exception as e:
            logger.error(f"Error extracting JD info: {e}")
    
    # Match each resume
    for idx, (resume_text, filename) in enumerate(zip(resume_texts, filenames)):
        logger.info(f"Matching resume {idx + 1}/{len(resume_texts)}: {filename}")
        
        try:
            if use_ai and provider:
                # AI-based extraction and matching
                resume_info = await extract_resume_info_ai(resume_text, provider)
                
                # Perform intelligent matching
                match_result = await intelligent_match(
                    resume_info, 
                    jd_info, 
                    provider,
                    resume_text,
                    job_description
                )
            else:
                # Fallback to basic scoring
                from app.services.matching_service.ai_extractor import calculate_basic_score
                jd_required_skills = jd_info.get('required_skills', required_skills or [])
                match_result = calculate_basic_score(resume_text, job_description, jd_required_skills)
            
            results.append({
                'filename': filename,
                'score': match_result['score'],
                'missing_skills': match_result.get('missing_skills', []),
                'matching_skills': match_result.get('matching_skills', []),
                'remarks': match_result.get('remarks', 'No remarks available.'),
                'extracted_text': resume_text[:1000],  # First 1000 chars
                'resume_info': resume_info if use_ai and provider else None  # Include extracted resume info
            })
            
        except Exception as e:
            logger.error(f"Error matching resume {filename}: {e}")
            # Add result with error
            results.append({
                'filename': filename,
                'score': 0,
                'missing_skills': [],
                'matching_skills': [],
                'remarks': f'Error processing resume: {str(e)}',
                'extracted_text': resume_text[:500]
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

