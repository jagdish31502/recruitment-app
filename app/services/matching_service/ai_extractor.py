"""
AI-based information extraction from resumes and job descriptions with JSON output
"""
import json
import re
from typing import Dict, List, Optional
from app.utilities.logger import setup_logger
from app.utilities.prompts import (
    EXTRACT_RESUME_INFORMATION,
    EXTRACT_JD_INFORMATION,
    INTELLIGENT_MATCH
)

logger = setup_logger()


def clean_json_response(response: str) -> str:
    """Clean JSON response from AI models (remove markdown, extra text)"""
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


async def extract_resume_info_ai(resume_text: str, provider) -> Dict:
    """Extract structured information from resume using AI with JSON output"""
    
    prompt = EXTRACT_RESUME_INFORMATION.format(resume_text=resume_text)
    
    try:
        response = await provider.generate_text(prompt, temperature=0.2)
        
        # Clean and parse response
        cleaned = clean_json_response(response)
        resume_info = json.loads(cleaned)
        
        # Flatten structure for easier use
        return {
            'name': resume_info.get('personal_info', {}).get('name', 'Not specified'),
            'email': resume_info.get('personal_info', {}).get('email', 'Not specified'),
            'phone': resume_info.get('personal_info', {}).get('phone', 'Not specified'),
            'location': resume_info.get('personal_info', {}).get('location', 'Not specified'),
            'skills': resume_info.get('skills', {}).get('technical_skills', []),
            'soft_skills': resume_info.get('skills', {}).get('soft_skills', []),
            'certifications': resume_info.get('skills', {}).get('certifications', []),
            'experience_years': resume_info.get('experience', {}).get('total_years', 0),
            'relevant_experience': resume_info.get('experience', {}).get('relevant_experience', ''),
            'companies': resume_info.get('experience', {}).get('companies', []),
            'roles': resume_info.get('experience', {}).get('roles', []),
            'education': resume_info.get('education', {}).get('highest_degree', 'Not specified'),
            'university': resume_info.get('education', {}).get('university', 'Not specified'),
            'graduation_year': resume_info.get('education', {}).get('year', 'Not specified'),
            'summary': resume_info.get('professional_summary', ''),
            'strengths': resume_info.get('strengths', [])
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in resume extraction: {e}")
        logger.error(f"Response was: {response[:500]}")
        return extract_resume_info_fallback(resume_text)
    except Exception as e:
        logger.error(f"Error extracting resume info with AI: {e}")
        return extract_resume_info_fallback(resume_text)


async def extract_jd_info_ai(job_description: str, provider) -> Dict:
    """Extract structured information from job description using AI with JSON output"""
    
    prompt = EXTRACT_JD_INFORMATION.format(job_description=job_description)
    
    try:
        response = await provider.generate_text(prompt, temperature=0.2)
        
        # Clean and parse response
        cleaned = clean_json_response(response)
        jd_info = json.loads(cleaned)
        
        # Flatten structure for easier use
        return {
            'job_title': jd_info.get('job_title', 'Not specified'),
            'required_skills': jd_info.get('requirements', {}).get('required_skills', []),
            'nice_to_have_skills': jd_info.get('requirements', {}).get('nice_to_have_skills', []),
            'experience_years': jd_info.get('requirements', {}).get('years_of_experience', 0),
            'responsibilities': jd_info.get('responsibilities', []),
            'required_qualifications': jd_info.get('qualifications', {}).get('required', []),
            'preferred_qualifications': jd_info.get('qualifications', {}).get('preferred', []),
            'company': jd_info.get('company_info', {}).get('company_name', 'Not specified'),
            'location': jd_info.get('company_info', {}).get('location', 'Not specified'),
            'employment_type': jd_info.get('company_info', {}).get('employment_type', 'Not specified')
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in JD extraction: {e}")
        logger.error(f"Response was: {response[:500]}")
        return extract_jd_info_fallback(job_description)
    except Exception as e:
        logger.error(f"Error extracting JD info with AI: {e}")
        return extract_jd_info_fallback(job_description)


async def intelligent_match(extracted_resume: Dict, extracted_jd: Dict, provider, resume_text: str, jd_text: str) -> Dict:
    """Use AI to perform intelligent matching with structured JSON output"""
    
    # Create concise summaries
    resume_summary = f"""
Name: {extracted_resume.get('name', 'N/A')}
Experience: {extracted_resume.get('experience_years', 0)} years
Skills: {', '.join(extracted_resume.get('skills', [])[:10])}
Education: {extracted_resume.get('education', 'N/A')}
Companies: {', '.join(extracted_resume.get('companies', [])[:3])}
Roles: {', '.join(extracted_resume.get('roles', [])[:3])}
"""
    
    jd_summary = f"""
Position: {extracted_jd.get('job_title', 'N/A')}
Required Experience: {extracted_jd.get('experience_years', 0)} years
Required Skills: {', '.join(extracted_jd.get('required_skills', [])[:10])}
Nice-to-Have: {', '.join(extracted_jd.get('nice_to_have_skills', [])[:5])}
Location: {extracted_jd.get('location', 'N/A')}
"""
    
    prompt = INTELLIGENT_MATCH.format(
        resume_summary=resume_summary,
        jd_summary=jd_summary,
        resume_text=resume_text[:1500],
        jd_text=jd_text[:1500]
    )
    
    try:
        response = await provider.generate_text(prompt, temperature=0.3)
        
        # Clean and parse response
        cleaned = clean_json_response(response)
        match_result = json.loads(cleaned)
        
        # Ensure score is within bounds
        score = float(match_result.get('score', 50))
        score = max(0, min(100, score))  # Clamp between 0-100
        
        return {
            'score': score,
            'missing_skills': match_result.get('missing_skills', []),
            'matching_skills': match_result.get('matching_skills', []),
            'strengths': match_result.get('strengths', []),
            'weaknesses': match_result.get('weaknesses', []),
            'remarks': match_result.get('remarks', 'Analysis completed.')
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in matching: {e}")
        logger.error(f"Response was: {response[:500]}")
        return calculate_basic_score(resume_text, jd_text, extracted_jd.get('required_skills', []))
    except Exception as e:
        logger.error(f"AI matching error: {e}")
        return calculate_basic_score(resume_text, jd_text, extracted_jd.get('required_skills', []))


def extract_resume_info_fallback(resume_text: str) -> Dict:
    """Fallback method using regex patterns when AI is unavailable"""
    info = {
        'name': 'Not specified',
        'email': 'Not specified',
        'phone': 'Not specified',
        'location': 'Not specified',
        'skills': [],
        'soft_skills': [],
        'certifications': [],
        'experience_years': 0,
        'relevant_experience': '',
        'companies': [],
        'roles': [],
        'education': 'Not specified',
        'university': 'Not specified',
        'graduation_year': 'Not specified',
        'summary': '',
        'strengths': []
    }
    
    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    if email_match:
        info['email'] = email_match.group()
    
    # Extract phone
    phone_match = re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', resume_text)
    if phone_match:
        info['phone'] = phone_match.group()
    
    # Extract skills using common patterns
    skills_patterns = [
        r'SKILLS[:.]?\s*([^\n]+)',
        r'TECHNICAL SKILLS[:.]?\s*([^\n]+)',
        r'CORE COMPETENCIES[:.]?\s*([^\n]+)'
    ]
    
    for pattern in skills_patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            skills = [s.strip() for s in re.split(r'[,;|]', match.group(1))]
            info['skills'] = [s for s in skills if s and len(s) > 2][:10]
            break
    
    # Extract experience years
    exp_patterns = [
        r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
        r'experience[:.]?\s*(\d+)\s*(?:\+)?\s*(?:years?|yrs?)'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            info['experience_years'] = int(match.group(1))
            break
    
    # Extract education
    edu_patterns = [
        r'(Bachelor|Master|PhD|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|MBA)[^\n]*',
        r'(BE|ME|MS|BS)\s+(?:in\s+)?[^\n]+'
    ]
    
    for pattern in edu_patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            info['education'] = match.group().strip()
            break
    
    return info


def extract_jd_info_fallback(job_description: str) -> Dict:
    """Fallback method for extracting JD info using regex"""
    info = {
        'job_title': 'Not specified',
        'required_skills': [],
        'nice_to_have_skills': [],
        'experience_years': 0,
        'responsibilities': [],
        'required_qualifications': [],
        'preferred_qualifications': [],
        'company': 'Not specified',
        'location': 'Not specified',
        'employment_type': 'Not specified'
    }
    
    # Extract job title (usually first line or heading)
    title_match = re.search(r'^([A-Z][^\n]{10,60})', job_description, re.MULTILINE)
    if title_match:
        info['job_title'] = title_match.group(1).strip()
    
    # Extract required skills
    req_patterns = [
        r'(?:required|must have|essential)[\s:]?(?:skills?|qualifications?)[:.]?\s*([^\n]+)',
        r'requirements?[:.]?\s*([^\n]+)'
    ]
    
    for pattern in req_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            skills = [s.strip() for s in re.split(r'[,;|]', match.group(1))]
            info['required_skills'] = [s for s in skills if s and len(s) > 2][:10]
            break
    
    # Extract nice-to-have skills
    nice_patterns = [
        r'(?:nice to have|preferred|bonus)[\s:]?(?:skills?|qualifications?)[:.]?\s*([^\n]+)',
        r'preferred?[:.]?\s*([^\n]+)'
    ]
    
    for pattern in nice_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            skills = [s.strip() for s in re.split(r'[,;|]', match.group(1))]
            info['nice_to_have_skills'] = [s for s in skills if s and len(s) > 2][:10]
            break
    
    # Extract experience years
    exp_match = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)', job_description, re.IGNORECASE)
    if exp_match:
        info['experience_years'] = int(exp_match.group(1))
    
    return info


def calculate_basic_score(resume_text: str, jd_text: str, required_skills: List[str] = None) -> Dict:
    """Fallback basic scoring method using keyword matching"""
    if not required_skills:
        required_skills = []
    
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    # Match skills
    matched_skills = [skill for skill in required_skills if skill.lower() in resume_lower]
    missing_skills = [skill for skill in required_skills if skill.lower() not in resume_lower]
    
    # Calculate base score from skills
    if required_skills:
        skill_score = (len(matched_skills) / len(required_skills)) * 70
    else:
        skill_score = 50
    
    # Extract and compare experience
    exp_match_resume = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)', resume_text, re.IGNORECASE)
    exp_match_jd = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)', jd_text, re.IGNORECASE)
    
    exp_score = 0
    if exp_match_resume and exp_match_jd:
        resume_years = int(exp_match_resume.group(1))
        required_years = int(exp_match_jd.group(1))
        
        if resume_years >= required_years:
            exp_score = 20
        elif resume_years >= required_years * 0.7:
            exp_score = 15
        else:
            exp_score = 10
    else:
        exp_score = 10
    
    # Add education bonus
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'b.tech', 'm.tech', 'mba']
    edu_score = 10 if any(keyword in resume_lower for keyword in edu_keywords) else 5
    
    total_score = skill_score + exp_score + edu_score
    total_score = max(0, min(100, total_score))  # Clamp between 0-100
    
    remarks = f"Basic matching: {len(matched_skills)} of {len(required_skills)} required skills found."
    if matched_skills:
        remarks += f" Strong in: {', '.join(matched_skills[:3])}."
    if missing_skills:
        remarks += f" Missing: {', '.join(missing_skills[:3])}."
    
    return {
        'score': round(total_score, 2),
        'missing_skills': missing_skills,
        'matching_skills': matched_skills,
        'strengths': matched_skills[:3] if matched_skills else [],
        'weaknesses': missing_skills[:3] if missing_skills else [],
        'remarks': remarks
    }