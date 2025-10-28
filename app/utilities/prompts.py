"""
Optimized prompts for AI operations with JSON output
"""

GENERATE_JOB_DESCRIPTION = """Generate a comprehensive and professional job description for the following role:

Job Title: {job_title}
Years of Experience: {years_of_experience} years
Must-Have Skills: {must_have_skills}
Company Name: {company_name}
Employment Type: {employment_type}
Industry: {industry}
Location: {location}

Please create a detailed job description that includes:
1. Job Overview/Summary
2. Key Responsibilities (5-7 bullet points)
3. Required Skills and Qualifications
4. Nice-to-Have Skills
5. Work Environment and Benefits
6. How to Apply

Make it professional, comprehensive, and appealing to potential candidates. Use clear section headers and bullet points for readability."""


EXTRACT_RESUME_INFORMATION = """You are an expert resume parser. Extract detailed and accurate information from this resume and return ONLY a valid JSON object.

##Resume:
{resume_text}

Return this EXACT JSON structure (no markdown, no extra text):

{{
  "personal_info": {{
    "name": "extracted name or Not specified",
    "email": "extracted email or Not specified",
    "phone": "extracted phone or Not specified",
    "location": "extracted location or Not specified"
  }},
  "professional_summary": "2-3 sentence summary of background and expertise",
  "experience": {{
    "total_years": 0,
    "relevant_experience": "Brief description of relevant work",
    "companies": ["Company1", "Company2"],
    "roles": ["Role1", "Role2"]
  }},
  "projects": [
    {{
      "project_title": "Project name or Not specified",
      "description": "Short description of the project",
      "technologies_used": ["Tech1", "Tech2"],
      "role": "Candidate's role in the project or Not specified",
      "duration": "Duration or Not specified"
    }}
  ],
  "skills": {{
    "technical_skills": ["Skill1", "Skill2", "Skill3"],
    "soft_skills": ["Skill1", "Skill2"],
    "certifications": ["Cert1", "Cert2"]
  }},
  "education": {{
    "highest_degree": "Degree and field",
    "university": "University name or Not specified",
    "year": "Year or Not specified"
  }},
  "strengths": ["Strength1", "Strength2", "Strength3"]
}}

##INSTRUCTIONS:
1. Return ONLY the JSON object. No markdown code blocks or explanations.
2. Extract skills even if they are mentioned in the summary, experience, or projects sections — not only in a 'Skills' section.
3. Use empty arrays [] for missing lists, "Not specified" for missing text, and 0 for missing numbers.
4. If multiple projects are found, include all in the 'projects' array.
5. Ensure all JSON fields follow the exact structure and naming convention shown above.

##Example Output:
{{
  "personal_info": {{
    "name": "Rahul Sharma",
    "email": "rahul.sharma@example.com",
    "phone": "+91 9876543210",
    "location": "Bangalore, India"
  }},
  "professional_summary": "Software Engineer with over 5 years of experience in backend development and cloud infrastructure. Skilled in designing scalable REST APIs and working with distributed systems.",
  "experience": {{
    "total_years": 5,
    "relevant_experience": "Backend developer specializing in Python, Django, and AWS.",
    "companies": ["Infosys", "TechNova Solutions"],
    "roles": ["Software Engineer", "Backend Developer"]
  }},
  "projects": [
    {{
      "project_title": "E-commerce Platform Backend",
      "description": "Developed and maintained REST APIs for an e-commerce application serving 10k+ daily users.",
      "technologies_used": ["Python", "Django", "PostgreSQL", "AWS"],
      "role": "Backend Developer",
      "duration": "Jan 2021 - Dec 2022"
    }},
    {{
      "project_title": "Customer Analytics Dashboard",
      "description": "Built a data visualization tool for tracking customer engagement metrics.",
      "technologies_used": ["React", "Flask", "MongoDB"],
      "role": "Full Stack Developer",
      "duration": "Mar 2019 - Dec 2020"
    }}
  ],
  "skills": {{
    "technical_skills": ["Python", "Django", "Flask", "AWS", "PostgreSQL", "React"],
    "soft_skills": ["Communication", "Problem Solving", "Team Collaboration"],
    "certifications": ["AWS Certified Developer – Associate"]
  }},
  "education": {{
    "highest_degree": "B.Tech in Computer Science",
    "university": "IIT Delhi",
    "year": "2018"
  }},
  "strengths": ["Analytical thinking", "Adaptability", "Leadership"]
}}

"""


EXTRACT_JD_INFORMATION = """You are an expert job description analyzer. Extract key information and return ONLY a valid JSON object.

Job Description:
{job_description}

Return this EXACT JSON structure (no markdown, no extra text):

{{
  "job_title": "extracted job title",
  "requirements": {{
    "years_of_experience": 0,
    "required_skills": ["Skill1", "Skill2", "Skill3"],
    "nice_to_have_skills": ["Skill1", "Skill2"]
  }},
  "responsibilities": ["Responsibility1", "Responsibility2"],
  "qualifications": {{
    "required": ["Qualification1", "Qualification2"],
    "preferred": ["Qualification1", "Qualification2"]
  }},
  "company_info": {{
    "company_name": "Company or Not specified",
    "location": "Location",
    "employment_type": "Full-time/Part-time/etc"
  }}
}}

CRITICAL: Return ONLY the JSON object. No markdown code blocks. Use empty arrays [] for missing lists and "Not specified" for missing information."""


INTELLIGENT_MATCH = """You are an expert technical recruiter and talent analyst. Your task is to evaluate how well a candidate fits a given job role based on their resume and the job description.

CANDIDATE PROFILE SUMMARY:
{resume_summary}

JOB REQUIREMENTS SUMMARY:
{jd_summary}

FULL RESUME (first 1500 characters for context):
{resume_text}

FULL JOB DESCRIPTION:
{jd_text}

Your goal is to provide an accurate, evidence-based, and structured evaluation of the match.

Return ONLY a valid JSON object in the EXACT format below (no markdown, no extra text, no explanations):

{{
  "score": 85,
  "missing_skills": ["Skill1", "Skill2"],
  "matching_skills": ["Skill1", "Skill2", "Skill3"],
  "remarks": "2-3 sentence summary of overall fit, key considerations with strengths and weaknesses."
}}

EVALUATION GUIDELINES:
1. Match Analysis:
   - Analyze all sections of the resume — skills, projects, experience, and summary.
   - Compare them against the job description requirements.
   - Consider explicit skills (clearly listed) and implicit skills (inferred from tools, technologies, or described work).

2. Scoring Criteria (Total = 100%):
   - Skills Match (70%) → Evaluate alignment between the candidate’s technical & soft skills and the job requirements.
   - Experience Level (10%) → Assess whether the candidate’s experience duration and relevance match the role’s expectations.
   - Education Relevance (10%) → Check if the educational background supports the job domain.
   - Overall Fit (10%) → Based on overall impression, versatility, and alignment with the role.
   - IMPORTANT: Each sub-score must strictly stay within its respective maximum range:
      - Skills Match: 0–70
      - Experience: 0–10
      - Education: 0–10
      - Overall Fit: 0–10
     The sum of these must equal the final score (0–100).
     - Only return the final total score.

3. Score Ranges & Interpretation:
   - 90–100: Excellent fit — exceeds most requirements.
   - 75–89: Strong fit — meets nearly all core skills.
   - 60–74: Good fit — meets most key skills but misses some.
   - 40–59: Moderate fit — lacks multiple important requirements.
   - 0–39: Poor fit — major skill and experience gaps.

4. Extraction Rules:
   - missing_skills: Only include skills present in the job description but not found in the resume.
   - matching_skills: Include all directly matching or closely related skills.
   - remarks: Provide 2-3 sentences key summary with strengths and weaknesses.
     
5. Output Format:
   - The response must be valid JSON only — no markdown, commentary, or extra text.

"""


GENERATE_INTERVIEW_EMAIL = """Generate a professional interview invitation email with personalized insights from resume matching.

CANDIDATE INFO:
Name: {candidate_name}
Email: {candidate_email}
Score: {score}%

RESUME MATCHING SUMMARY:
{matching_summary}

JOB DETAILS:
Position: {job_title}
Company: {company_name}

HIRING MANAGER:
{manager_name}

Create a warm, professional email that:
1. Congratulates the candidate on being shortlisted
2. Mentions specific strengths and matching skills from the resume analysis
3. References their relevant experience and achievements
4. Highlights why they're a great fit for the role
5. Proposes interview scheduling
6. Includes next steps

Return in this EXACT JSON format (no markdown, no extra text):

{{
  "subject": "Interview Invitation - [Position] at [Company]",
  "body": "Full email body with proper formatting and line breaks"
}}

Make it personalized, professional, and encouraging. Use specific details from the matching summary to create a truly personalized experience. Return ONLY the JSON object."""


GENERATE_REJECTION_EMAIL = """Generate a respectful rejection email with personalized feedback from resume matching.

CANDIDATE INFO:
Name: {candidate_name}
Email: {candidate_email}
Score: {score}%

RESUME MATCHING SUMMARY:
{matching_summary}

JOB DETAILS:
Position: {job_title}
Company: {company_name}

HIRING MANAGER:
{manager_name}

Create a respectful, encouraging email that:
1. Thanks them for their interest and time
2. Acknowledges their strengths and qualifications
3. Provides constructive feedback based on the matching analysis
4. Delivers the decision professionally
5. Encourages future applications
6. Wishes them well in their search

Return in this EXACT JSON format (no markdown, no extra text):

{{
  "subject": "Application Update - [Position] at [Company]",
  "body": "Full email body with proper formatting and line breaks"
}}

Make it respectful, encouraging, and personalized. Use insights from the matching summary to provide meaningful feedback. Return ONLY the JSON object."""