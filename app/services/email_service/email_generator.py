"""
Email generation service for interview and rejection emails
"""
from app.utilities.logger import setup_logger

logger = setup_logger()


async def generate_email(provider, candidate_info: dict, job_description: str, 
                         email_type: str, company_name: str = "Our Company",
                         hiring_manager_name: str = "Hiring Manager") -> dict:
    """Generate personalized email using AI"""
    
    if email_type == "interview":
        prompt = f"""Generate a professional and warm interview call email with the following details:

Candidate Name: {candidate_info['name']}
Candidate Email: {candidate_info['email']}
Company Name: {company_name}
Hiring Manager Name: {hiring_manager_name}
Job Description: {job_description}

The email should:
1. Congratulate the candidate on their impressive background
2. Highlight what made them stand out (mention their strong skills match of {candidate_info['score']}%)
3. Express enthusiasm about scheduling an interview
4. Be professional yet warm and inviting
5. Include a subject line

Format as:
SUBJECT: <subject line>
BODY:
<email body>"""
    
    else:  # rejection
        prompt = f"""Generate a professional and respectful rejection email for a candidate who wasn't selected:

Candidate Name: {candidate_info['name']}
Candidate Email: {candidate_info['email']}
Company Name: {company_name}
Hiring Manager Name: {hiring_manager_name}

The email should:
1. Thank them for their interest
2. Acknowledge their qualifications
3. Explain that while they are qualified, another candidate was selected
4. Wish them well in their job search
5. Keep the door open for future opportunities
6. Be respectful and not damage their confidence
7. Include a subject line

Format as:
SUBJECT: <subject line>
BODY:
<email body>"""
    
    try:
        response = await provider.generate_text(prompt, temperature=0.7)
        
        # Parse response
        import re
        subject_match = re.search(r'SUBJECT:\s*(.+)', response)
        body_match = re.search(r'BODY:\s*(.+?)(?=\n\n|\Z)', response, re.DOTALL)
        
        subject = subject_match.group(1).strip() if subject_match else "Interview Opportunity" if email_type == "interview" else "Update on Your Application"
        body = body_match.group(1).strip() if body_match else response
        
        return {
            'email_subject': subject,
            'email_body': body,
            'candidate_name': candidate_info['name'],
            'email_type': email_type
        }
    
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        # Return template email
        if email_type == "interview":
            subject = f"Interview Opportunity at {company_name}"
            body = f"""Dear {candidate_info['name']},

Thank you for your interest in our position. We were impressed with your background and would like to invite you for an interview.

We believe your skills and experience align well with what we're looking for. Please let us know your availability for a call.

Best regards,
{hiring_manager_name}
{company_name}"""
        else:
            subject = f"Update on Your Application to {company_name}"
            body = f"""Dear {candidate_info['name']},

Thank you for your interest in our position and for taking the time to apply.

After careful consideration, we have decided to move forward with another candidate whose qualifications more closely match our current needs.

We appreciate your interest and wish you success in your job search.

Best regards,
{hiring_manager_name}
{company_name}"""
        
        return {
            'email_subject': subject,
            'email_body': body,
            'candidate_name': candidate_info['name'],
            'email_type': email_type
        }

